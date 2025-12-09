#!/usr/bin/env python3
"""
GitHub Summary Generator

Generates human-readable summaries of merged PRs with AI-powered analysis.
Supports multiple output destinations: files, Slack, and email.
Can be run manually or via cron for automated daily reports.

Note: At least one output destination (--file, --slack, or --email) is required.

Usage:
    # Output to file
    python github_summary.py --repos shop/world --time-range 7d --file report.md

    # Send via email
    python github_summary.py --repos shop/world --labels "Slice: delivery" --time-range 24h \
        --email user@example.com

    # Output to multiple destinations
    python github_summary.py --repos shop/world --time-range 24h \
        --file report.md \
        --slack https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
        --email user@example.com

    # Using config file
    python github_summary.py --config github_summary_config.yaml
"""

import argparse
import base64
import json
import logging
import os
import subprocess
import sys
import traceback
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import yaml

try:
    import anthropic
except ImportError:
    print("Error: anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("Error: requests package not installed. Run: pip install requests")
    sys.exit(1)

# Gmail API imports (optional - only needed for email functionality)
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_API_AVAILABLE = True
except ImportError:
    GMAIL_API_AVAILABLE = False


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Known bots to exclude from reviewers and commenters
KNOWN_BOTS = [
    'graphite-app',
    'caution-tape-bot',
    'observe-monitoring',
    'shopify-code-magic-production',
    'dependabot',
    'github-actions',
    'codecov',
    'renovate',
    'greenkeeper',
    'snyk-bot',
    'test-oversight-service',
    'admin-web-ci-bot',
    'shopify-review-assigner',
]


class GitHubSummary:
    def __init__(self, config: Dict[str, Any]):
        self.repos = config.get('repos', [])
        self.labels = config.get('labels', [])
        self.usernames = config.get('usernames', [])
        self.time_range = config.get('time_range', '24h')
        self.github_username = config.get('github_username', '')

        # Validate labels are strings (common YAML config error)
        if self.labels and any(not isinstance(label, str) for label in self.labels):
            raise ValueError(
                "Labels must be strings. Check your config file - labels with colons must be quoted.\n"
                "Example: labels:\n"
                '  - "Slice: delivery"\n'
                '  - "Component: Fulfillment"'
            )

        # Output destinations (can have 0 or more of each)
        self.slack_urls = config.get('slack_urls', [])
        self.email_addresses = config.get('email_addresses', [])
        self.output_files = config.get('output_files', [])

        # Read API key from OPENAI_API_KEY for Shopify proxy compatibility
        # Use environment variable if config value is None or not set
        self.anthropic_api_key = config.get('anthropic_api_key') or os.getenv('OPENAI_API_KEY')

        if not self.anthropic_api_key:
            raise ValueError("Anthropic API key not configured (set OPENAI_API_KEY env var or in config)")

        # Use Shopify's AI proxy for all Anthropic API calls
        shopify_proxy_url = config.get('anthropic_base_url', 'https://proxy.shopify.ai')
        self.client = anthropic.Anthropic(
            api_key=self.anthropic_api_key,
            base_url=shopify_proxy_url
        )

    def run(self) -> None:
        """Main entry point - generate and post summary."""
        logger.info("Starting GitHub summary generation")

        # Calculate time range
        start_time = self._parse_time_range(self.time_range)
        end_time = datetime.now(timezone.utc)

        logger.info(f"Fetching PRs from {start_time} to {end_time}")

        # Fetch PRs awaiting review (uses repos config, ignores label/username filters)
        prs_awaiting_review = []
        if self.github_username:
            logger.info(f"Fetching PRs awaiting review for {self.github_username}")
            prs_awaiting_review = self._fetch_prs_awaiting_review()
            logger.info(f"Found {len(prs_awaiting_review)} PRs awaiting review")

        # Fetch comments on user's PRs (uses repos and time_range config, ignores label/username filters)
        comments_on_my_prs = []
        if self.github_username:
            logger.info(f"Fetching comments on PRs authored by {self.github_username}")
            comments_on_my_prs = self._fetch_comments_on_my_prs(start_time)
            logger.info(f"Found {len(comments_on_my_prs)} comments on your PRs")

        # Fetch merged PRs for each repo (uses all filters)
        all_prs = []
        for repo in self.repos:
            prs = self._fetch_merged_prs(repo, start_time)
            filtered_prs = self._filter_prs(prs)
            all_prs.extend(filtered_prs)

        # Generate summary for each PR
        summaries = []
        if all_prs:
            logger.info(f"Found {len(all_prs)} matching merged PRs")
            for pr in all_prs:
                logger.info(f"Analyzing PR #{pr['number']} in {pr['repository']}")
                try:
                    summary = self._generate_pr_summary(pr)
                    summaries.append(summary)
                except Exception as e:
                    logger.error(f"Failed to generate summary for PR #{pr.get('number', 'unknown')}: {e}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    logger.info("Continuing with next PR...")
                    continue
        else:
            logger.info("No matching merged PRs found")

        # Check if there's anything to report
        if not summaries and not prs_awaiting_review and not comments_on_my_prs:
            logger.info("Nothing to report")
            report = self._format_empty_report(start_time, end_time)
            self._output_report(report)
            return

        # Format and output report
        report = self._format_report(
            summaries,
            start_time,
            end_time,
            prs_awaiting_review=prs_awaiting_review,
            comments_on_my_prs=comments_on_my_prs,
        )
        self._output_report(report)

        failed_count = len(all_prs) - len(summaries) if all_prs else 0
        if failed_count > 0:
            logger.warning(f"Summary generation complete. {len(summaries)} successful, {failed_count} failed")
        else:
            logger.info("Summary generation complete")

    def _parse_time_range(self, time_range: str) -> datetime:
        """Convert time range string (e.g., '24h', '7d') to datetime."""
        unit = time_range[-1]
        value = int(time_range[:-1])

        if unit == 'h':
            delta = timedelta(hours=value)
        elif unit == 'd':
            delta = timedelta(days=value)
        else:
            raise ValueError(f"Invalid time range unit: {unit}. Use 'h' for hours or 'd' for days")

        return datetime.now(timezone.utc) - delta

    def _fetch_merged_prs(self, repo: str, since: datetime) -> List[Dict[str, Any]]:
        """Fetch merged PRs from GitHub using gh CLI."""
        since_str = since.strftime('%Y-%m-%dT%H:%M:%SZ')

        # If filtering by username, use --author instead of --search for better results
        if self.usernames:
            all_prs = []
            for username in self.usernames:
                cmd = [
                    'gh', 'pr', 'list',
                    '--repo', repo,
                    '--state', 'merged',
                    '--author', username,
                    '--json', 'number,title,url,author,labels,mergedAt,createdAt,body',
                    '--limit', '100'
                ]

                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    prs = json.loads(result.stdout)

                    # Filter by date manually
                    for pr in prs:
                        merged_at = pr.get('mergedAt', '')
                        if merged_at and merged_at >= since_str:
                            pr['repository'] = repo
                            all_prs.append(pr)
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to fetch PRs from {repo} for {username}: {e.stderr}")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse PR data from {repo} for {username}: {e}")

            return all_prs
        else:
            # Use search for label-based filtering
            # For high-volume repos, fetch PRs day-by-day to avoid hitting limits
            all_prs = []
            current_date = since.date()
            end_date = datetime.now(timezone.utc).date()

            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                cmd = [
                    'gh', 'pr', 'list',
                    '--repo', repo,
                    '--state', 'merged',
                    '--search', f'merged:{date_str}',
                    '--json', 'number,title,url,author,labels,mergedAt,createdAt,body',
                    '--limit', '2000'  # Increased limit for high-volume repos
                ]

                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    prs = json.loads(result.stdout)

                    # Add repository info and filter by time
                    for pr in prs:
                        merged_at = pr.get('mergedAt', '')
                        if merged_at and merged_at >= since_str:
                            pr['repository'] = repo
                            all_prs.append(pr)

                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to fetch PRs from {repo} for {date_str}: {e.stderr}")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse PR data from {repo} for {date_str}: {e}")

                current_date += timedelta(days=1)

            return all_prs

    def _fetch_prs_awaiting_review(self) -> List[Dict[str, Any]]:
        """Fetch open PRs where the current user is requested as a reviewer."""
        if not self.github_username:
            logger.info("No github_username configured, skipping PRs awaiting review")
            return []

        all_prs = []
        for repo in self.repos:
            cmd = [
                'gh', 'pr', 'list',
                '--repo', repo,
                '--state', 'open',
                '--search', f'user-review-requested:{self.github_username}',
                '--json', 'number,title,url,author,labels,createdAt,updatedAt',
                '--limit', '100'
            ]

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                prs = json.loads(result.stdout)

                for pr in prs:
                    pr['repository'] = repo
                    all_prs.append(pr)

            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to fetch PRs awaiting review from {repo}: {e.stderr}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse PR data from {repo}: {e}")

        return all_prs

    def _fetch_comments_on_my_prs(self, since: datetime) -> List[Dict[str, Any]]:
        """Fetch recent comments on PRs authored by the current user."""
        if not self.github_username:
            logger.info("No github_username configured, skipping comments on my PRs")
            return []

        since_str = since.strftime('%Y-%m-%dT%H:%M:%SZ')
        all_comments = []

        for repo in self.repos:
            # Fetch open and recently merged PRs authored by the user
            for state in ['open', 'merged']:
                cmd = [
                    'gh', 'pr', 'list',
                    '--repo', repo,
                    '--state', state,
                    '--author', self.github_username,
                    '--json', 'number,title,url,comments,reviews',
                    '--limit', '50'
                ]

                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    prs = json.loads(result.stdout)

                    for pr in prs:
                        pr_info = {
                            'number': pr['number'],
                            'title': pr['title'],
                            'url': pr['url'],
                            'repository': repo,
                        }

                        # Get comments from the comments array
                        comments = pr.get('comments') or []
                        for comment in comments:
                            created_at = comment.get('createdAt', '')
                            if created_at >= since_str:
                                author = comment.get('author')
                                author_login = author.get('login', 'unknown') if author else 'unknown'
                                # Skip bots and self-comments
                                if author_login in KNOWN_BOTS or author_login.endswith('[bot]'):
                                    continue
                                if author_login == self.github_username:
                                    continue

                                all_comments.append({
                                    'pr': pr_info,
                                    'author': author_login,
                                    'body': comment.get('body', '')[:300],  # Truncate long comments
                                    'created_at': created_at,
                                    'type': 'comment',
                                })

                        # Get comments from reviews
                        reviews = pr.get('reviews') or []
                        for review in reviews:
                            submitted_at = review.get('submittedAt', '')
                            if submitted_at >= since_str:
                                author = review.get('author')
                                author_login = author.get('login', 'unknown') if author else 'unknown'
                                # Skip bots and self-reviews
                                if author_login in KNOWN_BOTS or author_login.endswith('[bot]'):
                                    continue
                                if author_login == self.github_username:
                                    continue

                                body = review.get('body', '')
                                state = review.get('state', '')
                                if body or state in ['APPROVED', 'CHANGES_REQUESTED']:
                                    all_comments.append({
                                        'pr': pr_info,
                                        'author': author_login,
                                        'body': body[:300] if body else f'[{state}]',
                                        'created_at': submitted_at,
                                        'type': 'review',
                                        'state': state,
                                    })

                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to fetch comments from {repo}: {e.stderr}")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse comment data from {repo}: {e}")

        # Sort by created_at descending
        all_comments.sort(key=lambda x: x['created_at'], reverse=True)
        return all_comments

    def _filter_prs(self, prs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter PRs by labels and usernames."""
        if not self.labels and not self.usernames:
            return prs

        filtered = []
        for pr in prs:
            # Check labels
            if self.labels:
                pr_labels = [label['name'] for label in pr.get('labels', [])]
                if any(label in pr_labels for label in self.labels):
                    filtered.append(pr)
                    continue

            # Check usernames
            if self.usernames:
                author = pr.get('author', {}).get('login', '')
                if author in self.usernames:
                    filtered.append(pr)
                    continue

        return filtered

    def _get_user_info(self, username: str) -> Dict[str, str]:
        """Fetch user's full name and profile URL from GitHub."""
        if not username or username in KNOWN_BOTS:
            return {'login': username, 'name': username, 'url': ''}

        cmd = ['gh', 'api', f'users/{username}', '--jq', '.name,.login,.html_url']

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')

            name = lines[0] if len(lines) > 0 and lines[0] != 'null' else username
            login = lines[1] if len(lines) > 1 else username
            url = lines[2] if len(lines) > 2 else f'https://github.com/{username}'

            return {
                'login': login,
                'name': name if name else login,  # Fallback to login if name is empty
                'url': url
            }
        except (subprocess.CalledProcessError, IndexError) as e:
            logger.warning(f"Failed to fetch user info for {username}: {e}")
            return {
                'login': username,
                'name': username,
                'url': f'https://github.com/{username}'
            }

    def _fetch_pr_details(self, repo: str, pr_number: int) -> Dict[str, Any]:
        """Fetch detailed PR information including files and reviews."""
        cmd = [
            'gh', 'pr', 'view', str(pr_number),
            '--repo', repo,
            '--json', 'title,body,author,url,reviews,comments,files'
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to fetch PR details for #{pr_number}: {e.stderr}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse PR details for #{pr_number}: {e}")
            return {}

    def _generate_pr_summary(self, pr: Dict[str, Any]) -> Dict[str, Any]:
        """Generate contextual summary using Claude API."""
        try:
            repo = pr['repository']
            pr_number = pr['number']

            # Fetch detailed PR info
            details = self._fetch_pr_details(repo, pr_number)

            # Extract relevant information
            title = pr.get('title', 'Untitled')
            body = pr.get('body', '')
            author = pr.get('author')
            author_login = author.get('login', 'unknown') if author else 'unknown'
            url = pr.get('url', '')
            merged_at = pr.get('mergedAt', '')
            created_at = pr.get('createdAt', '')
        except Exception as e:
            logger.error(f"Failed to extract PR info for #{pr.get('number', 'unknown')}: {e}")
            raise

        # Ensure we have lists even if API returns None
        files = details.get('files') or []
        reviews = details.get('reviews') or []
        comments = details.get('comments') or []

        # Get reviewers (people who approved, excluding bots)
        reviewer_logins = [
            r.get('author', {}).get('login', '')
            for r in reviews
            if r.get('state') == 'APPROVED' and r.get('author', {}).get('login', '') not in KNOWN_BOTS and r.get('author')
        ]

        # Get commenters (exclude bots, author, and duplicates)
        commenter_logins = set()
        for comment in comments:
            author = comment.get('author')
            if not author:
                continue
            login = author.get('login', '')
            if login and login not in KNOWN_BOTS and not login.endswith('[bot]') and login != author_login:
                commenter_logins.add(login)

        # Fetch user info (full names) for author, reviewers, and commenters
        author_info = self._get_user_info(author_login)
        reviewer_infos = [self._get_user_info(login) for login in reviewer_logins]
        commenter_infos = [self._get_user_info(login) for login in commenter_logins]

        # Build prompt for Claude
        prompt = self._build_summary_prompt(title, body, files, repo)

        # Call Claude API
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            summary_text = message.content[0].text
        except Exception as e:
            logger.error(f"Failed to generate summary for PR #{pr_number}: {e}")
            summary_text = "Error generating summary. See PR description for details."

        return {
            'number': pr_number,
            'title': title,
            'url': url,
            'author': author_info,
            'created_at': created_at,
            'merged_at': merged_at,
            'reviewers': reviewer_infos,
            'commenters': commenter_infos,
            'summary': summary_text,
            'files': files,
            'repository': repo,
            'labels': pr.get('labels', []),
        }

    def _build_summary_prompt(self, title: str, body: str, files: List[Dict], repo: str) -> str:
        """Build prompt for Claude to generate contextual summary."""
        file_list = "\n".join([f"- {f['path']}" for f in files[:20]])  # Limit to 20 files
        if len(files) > 20:
            file_list += f"\n... and {len(files) - 20} more files"

        num_files = len(files)

        # Dynamic summary instructions based on PR size
        if num_files <= 2:
            # Small PR: just 2-3 sentences
            summary_instructions = """Write a concise 2-3 sentence summary that covers:
- What changed and why
- Any notable impact or considerations"""
        elif num_files <= 10:
            # Medium PR: 1 paragraph
            summary_instructions = """Write a single paragraph (4-5 sentences) covering:
- What problem was being solved or feature was needed
- What changes were made and which components were modified
- Who is affected and any notable considerations"""
        else:
            # Large PR: 2 paragraphs
            summary_instructions = """Write a 2-paragraph summary:

**Paragraph 1 (4-5 sentences):**
- What problem was being solved or what feature was needed?
- What was the state of things before this change?
- Include any relevant context from the PR description

**Paragraph 2 (4-5 sentences):**
- What changes were made to address this?
- Which components or files were modified?
- Who is affected by this change (merchants, customers, internal systems)?
- Any notable side effects or follow-up work?"""

        return f"""Generate a human-readable summary of this pull request. The summary should be understandable by someone unfamiliar with this area of the codebase.

**PR Title:** {title}

**PR Description:**
{body or 'No description provided'}

**Changed Files ({num_files} files):**
{file_list}

**Repository:** {repo}

---

{summary_instructions}

Also, extract any links to:
- Vault projects (vault.shopify.io)
- GitHub issues

Format your response as:

## Summary

[Your summary here]

## Related Resources

- [Link text](url) - if found
- [Another link](url) - if found

If no related resources found, write "None found in PR description"
"""

    def _format_report(
        self,
        summaries: List[Dict[str, Any]],
        start_time: datetime,
        end_time: datetime,
        prs_awaiting_review: Optional[List[Dict[str, Any]]] = None,
        comments_on_my_prs: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Format all summaries into final report."""
        prs_awaiting_review = prs_awaiting_review or []
        comments_on_my_prs = comments_on_my_prs or []

        # Format repositories with links
        repo_links = [f"[{repo}](https://github.com/{repo})" for repo in self.repos]
        repos_line = f"**Repositories:** {', '.join(repo_links)}"

        # Format labels (without links to avoid clutter in emails)
        if self.labels:
            labels_text = ', '.join(self.labels)
        else:
            labels_text = 'None'

        usernames_text = ', '.join(self.usernames) if self.usernames else 'None'

        report = f"""# GitHub Summary

**Report Period:** {start_time.strftime('%Y-%m-%d %H:%M UTC')} to {end_time.strftime('%Y-%m-%d %H:%M UTC')}

{repos_line}

"""

        # Add PRs awaiting review section (before main content)
        if prs_awaiting_review:
            report += self._format_prs_awaiting_review_section(prs_awaiting_review)
            report += "\n---\n\n"

        # Add comments on my PRs section
        if comments_on_my_prs:
            report += self._format_comments_on_my_prs_section(comments_on_my_prs)
            report += "\n---\n\n"

        # Add merged PRs section header if there are summaries
        if summaries:
            report += f"""## Merged PRs ({len(summaries)} total)

**Filters:** Labels: {labels_text} | Usernames: {usernames_text}

---
"""
            for summary in summaries:
                report += self._format_pr_section(summary)
                report += "\n---\n\n"

            # Add statistics
            total_authors = len(set(s['author']['login'] for s in summaries))
            total_files = sum(len(s['files']) for s in summaries)

            report += f"""## Summary Statistics

- **Total Merged PRs:** {len(summaries)}
- **Authors:** {total_authors} unique contributors
- **Files Changed:** {total_files} files across all PRs
"""
        elif not prs_awaiting_review and not comments_on_my_prs:
            report += f"""**Filters:** Labels: {labels_text} | Usernames: {usernames_text}

---

No merged pull requests found matching the specified criteria.
"""

        return report

    def _format_prs_awaiting_review_section(self, prs: List[Dict[str, Any]]) -> str:
        """Format the PRs awaiting review section."""
        section = f"""## PRs Awaiting Your Review ({len(prs)})

"""
        for pr in prs:
            author = pr.get('author')
            author_login = author.get('login', 'unknown') if author else 'unknown'
            created_at = pr.get('createdAt', '')
            created_date = created_at[:10] if created_at else 'Unknown'

            section += f"- [PR #{pr['number']}: {pr['title']}]({pr['url']}) by **{author_login}** ({created_date})\n"

        return section

    def _format_comments_on_my_prs_section(self, comments: List[Dict[str, Any]]) -> str:
        """Format the comments on my PRs section."""
        section = f"""## Recent Activity on Your PRs ({len(comments)})

"""
        for comment in comments:
            pr_info = comment['pr']
            author = comment['author']
            created_at = comment['created_at']
            created_date = created_at[:10] if created_at else 'Unknown'
            created_time = created_at[11:16] if created_at and len(created_at) > 16 else ''
            comment_type = comment.get('type', 'comment')
            state = comment.get('state', '')

            # Format the type indicator
            if comment_type == 'review' and state:
                if state == 'APPROVED':
                    type_indicator = '✅ Approved'
                elif state == 'CHANGES_REQUESTED':
                    type_indicator = '🔄 Changes Requested'
                else:
                    type_indicator = f'📝 Review ({state})'
            else:
                type_indicator = '💬 Comment'

            body = comment.get('body', '')
            # Truncate body for display
            if body and len(body) > 150:
                body = body[:150] + '...'

            section += f"- **{type_indicator}** on [PR #{pr_info['number']}: {pr_info['title']}]({pr_info['url']})\n"
            section += f"  - By **{author}** at {created_date} {created_time} UTC\n"
            if body and body != f'[{state}]':
                # Escape newlines in the body for markdown display
                body_oneline = body.replace('\n', ' ').replace('\r', '')
                section += f"  - \"{body_oneline}\"\n"
            section += "\n"

        return section

    def _format_pr_section(self, summary: Dict[str, Any]) -> str:
        """Format a single PR summary."""
        author = summary['author']
        created_at = summary['created_at']
        merged_at = summary['merged_at']

        # Format dates
        created_date = created_at[:10] if created_at else 'Unknown'
        created_time = created_at[11:16] if created_at and len(created_at) > 16 else ''
        merged_date = merged_at[:10] if merged_at else 'Unknown'
        merged_time = merged_at[11:16] if merged_at and len(merged_at) > 16 else ''

        # Format author
        author_name = author.get('name', author.get('login', 'Unknown'))
        author_url = author.get('url', '')
        author_link = f"[{author_name}]({author_url})" if author_url else author_name
        author_line = f"**Author:** {author_link}"

        # Extract components from labels (labels starting with "//area")
        # Also filter out ZoneID labels and has-min-approvals
        components = []
        all_labels = []
        for label in summary.get('labels', []):
            label_name = label.get('name', '') if isinstance(label, dict) else str(label)

            # Skip ZoneID labels and has-min-approvals
            if label_name.startswith('ZoneID:') or label_name == 'has-min-approvals':
                continue

            all_labels.append(label_name)
            if label_name.startswith('//area'):
                components.append(label_name)

        if components:
            components_line = f"**Components:** {', '.join(components)}"
        else:
            components_line = ""

        # Format labels (cap at 6)
        if all_labels:
            labels_to_show = all_labels[:6]
            labels_text = ', '.join(labels_to_show)
            if len(all_labels) > 6:
                remaining = len(all_labels) - 6
                labels_text += f", and {remaining} more"
            labels_line = f"**Labels:** {labels_text}"
        else:
            labels_line = ""

        # Format reviewers
        if summary['reviewers']:
            reviewer_links = [
                f"[{r.get('name', r.get('login'))}]({r['url']})" if r.get('url') else r.get('name', r.get('login'))
                for r in summary['reviewers']
            ]
            reviewers_line = f"**Reviewers:** {', '.join(reviewer_links)}"
        else:
            reviewers_line = "**Reviewers:** None"

        # Format commenters
        if summary['commenters']:
            commenter_links = [
                f"[{c.get('name', c.get('login'))}]({c['url']})" if c.get('url') else c.get('name', c.get('login'))
                for c in summary['commenters']
            ]
            commenters_line = f"**Commenters:** {', '.join(commenter_links)}"
        else:
            commenters_line = "**Commenters:** None"

        # Build PR section with conditional components and labels lines
        pr_section = f"""## [PR #{summary['number']}: {summary['title']}]({summary['url']})

**Issue Opened On:** {created_date} {created_time} UTC by {author_link}

**Merged:** {merged_date} {merged_time} UTC

{author_line}

"""

        # Add components line if present
        if components_line:
            pr_section += f"{components_line}\n\n"

        # Add labels line if present
        if labels_line:
            pr_section += f"{labels_line}\n\n"

        pr_section += f"""{reviewers_line}

{commenters_line}

{summary['summary']}

### Changed Files

"""

        # Add file links (limit to 15 for readability)
        files_to_show = summary['files'][:15]
        for file_info in files_to_show:
            file_path = file_info['path']
            repo = summary['repository']
            file_url = f"https://github.com/{repo}/blob/main/{file_path}"
            pr_section += f"- [`{file_path}`]({file_url})\n"

        if len(summary['files']) > 15:
            pr_section += f"- ... and {len(summary['files']) - 15} more files\n"

        return pr_section

    def _format_empty_report(self, start_time: datetime, end_time: datetime) -> str:
        """Format report when no PRs found."""
        # Format repositories with links
        repo_links = [f"[{repo}](https://github.com/{repo})" for repo in self.repos]
        repos_line = f"**Repositories:** {', '.join(repo_links)}"

        # Format labels (without links to avoid clutter in emails)
        if self.labels:
            labels_text = ', '.join(self.labels)
        else:
            labels_text = 'None'

        usernames_text = ', '.join(self.usernames) if self.usernames else 'None'

        return f"""# GitHub Summary

**Total PRs:** 0

**Report Period:** {start_time.strftime('%Y-%m-%d %H:%M UTC')} to {end_time.strftime('%Y-%m-%d %H:%M UTC')}

{repos_line}

**Filters:** Labels: {labels_text} | Usernames: {usernames_text}

---

No merged pull requests found matching the specified criteria.
"""

    def _output_report(self, report: str) -> None:
        """Output report to configured destinations (files, Slack, email)."""
        # Output to files
        for file_path in self.output_files:
            self._write_to_file(report, file_path)

        # Output to Slack
        for slack_url in self.slack_urls:
            self._post_to_slack(report, slack_url)

        # Output to email
        for email_address in self.email_addresses:
            self._send_email(report, email_address)

    def _write_to_file(self, report: str, file_path: str) -> None:
        """Write formatted report to a file."""
        try:
            with open(file_path, 'w') as f:
                f.write(report)
            logger.info(f"Report written to: {file_path}")
            print(f"✅ Report written to: {file_path}")
        except Exception as e:
            logger.error(f"Failed to write report to {file_path}: {e}")
            raise

    def _post_to_slack(self, report: str, slack_url: str) -> None:
        """Post formatted report to Slack."""
        # Split into chunks if too long (Slack has message length limits)
        max_length = 3000

        if len(report) <= max_length:
            self._send_slack_message(report, slack_url)
        else:
            # Split into chunks at section boundaries
            chunks = self._split_report(report, max_length)
            for i, chunk in enumerate(chunks, 1):
                header = f"*Part {i}/{len(chunks)}*\n\n" if len(chunks) > 1 else ""
                self._send_slack_message(header + chunk, slack_url)

    def _split_report(self, report: str, max_length: int) -> List[str]:
        """Split report into chunks at logical boundaries."""
        # Simple splitting at PR boundaries (marked by "---")
        sections = report.split('\n---\n')
        chunks = []
        current_chunk = sections[0]  # Header section

        for section in sections[1:]:
            if len(current_chunk) + len(section) + 10 < max_length:
                current_chunk += '\n---\n' + section
            else:
                chunks.append(current_chunk)
                current_chunk = section

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _send_slack_message(self, text: str, slack_url: str) -> None:
        """Send a single message to Slack."""
        payload = {
            "text": text,
            "mrkdwn": True
        }

        try:
            response = requests.post(slack_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Successfully posted to Slack webhook")
            print(f"✅ Posted to Slack webhook")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to post to Slack: {e}")
            raise

    def _send_email(self, report: str, email_address: str) -> None:
        """Send report via email using configured method."""
        # Check which email method to use
        smtp_method = os.getenv('EMAIL_METHOD', 'smtp').lower()

        if smtp_method == 'gmail-api':
            self._send_email_via_gmail_api(report, email_address)
        elif smtp_method == 'smtp-oauth':
            self._send_email_via_smtp_oauth(report, email_address)
        else:
            self._send_email_via_smtp(report, email_address)

    def _convert_inline_markdown(self, text: str) -> str:
        """Convert inline markdown syntax to HTML."""
        import re

        # Convert markdown links to HTML (must be done before backticks to preserve link text)
        text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)

        # Convert backticks to code tags (excluding what's already in HTML tags)
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

        # Convert bold markdown to HTML
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)

        # Convert italic markdown to HTML
        text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)

        return text

    def _markdown_to_html(self, markdown_text: str) -> str:
        """Convert markdown report to HTML with email-friendly styling."""
        import re

        html_parts = []
        html_parts.append('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #24292e;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
        }
        h1 {
            color: #1a1a1a;
            border-bottom: 2px solid #e1e4e8;
            padding-bottom: 10px;
            font-size: 28px;
        }
        h2 {
            color: #0366d6;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 22px;
        }
        h3 {
            color: #24292e;
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 18px;
        }
        p {
            margin: 10px 0;
        }
        strong {
            color: #1a1a1a;
        }
        a {
            color: #0366d6;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        ul {
            margin: 10px 0;
            padding-left: 30px;
        }
        li {
            margin: 5px 0;
        }
        hr {
            border: none;
            border-top: 1px solid #e1e4e8;
            margin: 30px 0;
        }
        .metadata {
            background-color: #f6f8fa;
            padding: 15px;
            border-radius: 6px;
            margin: 15px 0;
            border-left: 4px solid #0366d6;
        }
        .summary {
            background-color: #ffffff;
            padding: 15px;
            margin: 15px 0;
            border-left: 3px solid #28a745;
        }
        .files {
            background-color: #f6f8fa;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
            font-size: 14px;
        }
        .stats {
            background-color: #fff5b1;
            padding: 15px;
            border-radius: 6px;
            margin-top: 20px;
            border-left: 4px solid #ffd33d;
        }
        code {
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 13px;
            background-color: #ffffff;
            padding: 2px 6px;
            border-radius: 3px;
            border: 1px solid #e1e4e8;
            color: #24292e;
        }
    </style>
</head>
<body>
''')

        lines = markdown_text.split('\n')
        in_summary = False
        in_files = False
        in_stats = False

        for line in lines:
            # Main title
            if line.startswith('# '):
                html_parts.append(f'<h1>{self._convert_inline_markdown(line[2:])}</h1>')

            # PR title (h2)
            elif line.startswith('## '):
                if in_summary:
                    html_parts.append('</div>')
                    in_summary = False
                if in_files:
                    html_parts.append('</div>')
                    in_files = False

                # Extract PR link
                match = re.match(r'## \[(.*?)\]\((.*?)\)', line)
                if match:
                    title = match.group(1)
                    url = match.group(2)
                    html_parts.append(f'<h2><a href="{url}">{self._convert_inline_markdown(title)}</a></h2>')
                else:
                    html_parts.append(f'<h2>{self._convert_inline_markdown(line[3:])}</h2>')

            # Subsections (h3)
            elif line.startswith('### '):
                if in_summary:
                    html_parts.append('</div>')
                    in_summary = False
                if line.startswith('### Changed Files'):
                    html_parts.append('<h3>Changed Files</h3><div class="files">')
                    in_files = True
                else:
                    html_parts.append(f'<h3>{self._convert_inline_markdown(line[4:])}</h3>')

            # Summary section
            elif line.startswith('## Summary'):
                html_parts.append('<div class="summary">')
                in_summary = True

            # Statistics section
            elif line.startswith('## Summary Statistics'):
                if in_files:
                    html_parts.append('</div>')
                    in_files = False
                html_parts.append('<div class="stats"><h3>Summary Statistics</h3>')
                in_stats = True

            # Metadata (bold fields)
            elif line.startswith('**') and ':' in line and not in_summary:
                if not any(x in line for x in ['Summary', 'Related', 'Changed']):
                    # Start metadata section if needed
                    if 'Total PRs:' in line or 'Report Period:' in line:
                        if in_stats:
                            html_parts.append('</div>')
                            in_stats = False
                        html_parts.append('<div class="metadata">')

                    # Parse bold text
                    match = re.match(r'\*\*(.*?):\*\*(.*)', line)
                    if match:
                        key = match.group(1)
                        value = match.group(2).strip()

                        # Use monospace font for Components and Labels
                        if key in ['Components', 'Labels']:
                            # Split by comma, wrap each item in code tags (before markdown conversion)
                            items = value.split(', ')
                            code_items = [f'<code>{self._convert_inline_markdown(item)}</code>' for item in items]
                            value = ', '.join(code_items)
                        elif key == 'Filters':
                            # Convert markdown to HTML and replace spaces with non-breaking spaces within label names
                            value = self._convert_inline_markdown(value)
                            # Replace "Slice: " with "Slice:&nbsp;" to prevent breaking
                            value = value.replace('Slice: ', 'Slice:&nbsp;')
                        else:
                            # Convert markdown to HTML for other fields
                            value = self._convert_inline_markdown(value)

                        html_parts.append(f'<p><strong>{key}:</strong> {value}</p>')

                    # Close metadata after Filters
                    if 'Filters:' in line:
                        html_parts.append('</div>')

            # Horizontal rules
            elif line.strip() == '---':
                if in_summary:
                    html_parts.append('</div>')
                    in_summary = False
                if in_files:
                    html_parts.append('</div>')
                    in_files = False
                if in_stats:
                    html_parts.append('</div>')
                    in_stats = False
                html_parts.append('<hr>')

            # List items
            elif line.strip().startswith('- '):
                content = line.strip()[2:]
                # Convert all inline markdown to HTML
                content = self._convert_inline_markdown(content)
                html_parts.append(f'<li>{content}</li>')

            # Regular paragraphs
            elif line.strip() and not line.startswith('#'):
                # Convert all inline markdown to HTML
                content = self._convert_inline_markdown(line)
                html_parts.append(f'<p>{content}</p>')

            # Empty lines
            elif not line.strip():
                pass  # Skip empty lines, spacing handled by CSS

        # Close any open sections
        if in_summary:
            html_parts.append('</div>')
        if in_files:
            html_parts.append('</div>')
        if in_stats:
            html_parts.append('</div>')

        html_parts.append('</body></html>')

        return '\n'.join(html_parts)

    def _send_email_via_smtp(self, report: str, email_address: str) -> None:
        """Send email using SMTP (app password or relay)."""
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText as MIMETextEmail

        smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_user = os.getenv('SMTP_USER')
        smtp_password = os.getenv('SMTP_PASSWORD')
        smtp_from = os.getenv('SMTP_FROM', smtp_user)

        if not smtp_user or not smtp_password:
            logger.error("SMTP credentials not configured. Set SMTP_USER and SMTP_PASSWORD")
            print(f"❌ SMTP credentials not configured. Cannot send email to: {email_address}")
            print("   See scripts/EMAIL_SETUP.md for setup instructions")
            return

        try:
            # Convert markdown to HTML
            html_content = self._markdown_to_html(report)

            msg = MIMEMultipart('alternative')
            msg['From'] = smtp_from
            msg['To'] = email_address
            msg['Subject'] = f'GitHub Summary - {datetime.now(timezone.utc).strftime("%Y-%m-%d")}'

            # Attach both plain text and HTML versions
            msg.attach(MIMETextEmail(report, 'plain', 'utf-8'))
            msg.attach(MIMETextEmail(html_content, 'html', 'utf-8'))

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)

            logger.info(f"Successfully sent email to: {email_address}")
            print(f"✅ Email sent to: {email_address}")

        except Exception as e:
            logger.error(f"Failed to send email via SMTP to {email_address}: {e}")
            print(f"❌ Failed to send email to {email_address}: {e}")

    def _send_email_via_smtp_oauth(self, report: str, email_address: str) -> None:
        """Send email using SMTP with OAuth2 authentication."""
        if not GMAIL_API_AVAILABLE:
            logger.error("Google auth packages not installed. Run: pip install google-auth google-auth-oauthlib")
            print(f"❌ Google auth packages not installed. Cannot send email to: {email_address}")
            return

        import smtplib
        from email.mime.multipart import MIMEMultipart

        gmail_credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH')
        gmail_token_path = os.getenv('GMAIL_TOKEN_PATH', 'gmail_token.json')
        smtp_from = os.getenv('SMTP_FROM')

        if not gmail_credentials_path:
            logger.error("Gmail credentials not configured. Set GMAIL_CREDENTIALS_PATH")
            print(f"❌ Gmail OAuth credentials not configured. Cannot send email to: {email_address}")
            return

        try:
            # Get OAuth credentials
            SCOPES = ['https://mail.google.com/']
            creds = None

            if os.path.exists(gmail_token_path):
                creds = Credentials.from_authorized_user_file(gmail_token_path, SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    from google_auth_oauthlib.flow import InstalledAppFlow
                    flow = InstalledAppFlow.from_client_secrets_file(gmail_credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)

                with open(gmail_token_path, 'w') as token:
                    token.write(creds.to_json())

            # Generate OAuth2 string
            auth_string = f"user={smtp_from or creds.client_id}\x01auth=Bearer {creds.token}\x01\x01"

            # Send via SMTP with OAuth
            msg = MIMEMultipart()
            msg['From'] = smtp_from or creds.client_id
            msg['To'] = email_address
            msg['Subject'] = f'GitHub Summary - {datetime.now(timezone.utc).strftime("%Y-%m-%d")}'
            msg.attach(MIMEText(report, 'plain', 'utf-8'))

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.docmd('AUTH', 'XOAUTH2 ' + base64.b64encode(auth_string.encode()).decode())
                server.send_message(msg)

            logger.info(f"Successfully sent email to: {email_address}")
            print(f"✅ Email sent to: {email_address}")

        except Exception as e:
            logger.error(f"Failed to send email via SMTP OAuth to {email_address}: {e}")
            print(f"❌ Failed to send email to {email_address}: {e}")

    def _send_email_via_gmail_api(self, report: str, email_address: str) -> None:
        """Send report via email using Gmail API."""
        if not GMAIL_API_AVAILABLE:
            logger.error("Gmail API packages not installed. Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
            print(f"❌ Gmail API packages not installed. Cannot send email to: {email_address}")
            return

        # Get Gmail credentials from environment or config
        gmail_credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH')
        gmail_token_path = os.getenv('GMAIL_TOKEN_PATH', 'gmail_token.json')
        gmail_service_account_path = os.getenv('GMAIL_SERVICE_ACCOUNT_PATH')

        if not gmail_credentials_path and not gmail_service_account_path:
            logger.error("Gmail credentials not configured. Set GMAIL_CREDENTIALS_PATH or GMAIL_SERVICE_ACCOUNT_PATH")
            print(f"❌ Gmail credentials not configured. Cannot send email to: {email_address}")
            print("   See scripts/EMAIL_SETUP.md for setup instructions")
            return

        try:
            # Build Gmail service
            if gmail_service_account_path:
                # Service account flow (for automation)
                service = self._build_gmail_service_with_service_account(gmail_service_account_path, email_address)
            else:
                # OAuth flow (for user authentication)
                service = self._build_gmail_service_with_oauth(gmail_credentials_path, gmail_token_path)

            # Create email message
            message = MIMEText(report, 'plain', 'utf-8')
            message['To'] = email_address
            message['Subject'] = f'GitHub Summary - {datetime.now(timezone.utc).strftime("%Y-%m-%d")}'

            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            send_message = {'raw': raw_message}

            # Send the email
            service.users().messages().send(userId='me', body=send_message).execute()
            logger.info(f"Successfully sent email to: {email_address}")
            print(f"✅ Email sent to: {email_address}")

        except HttpError as e:
            logger.error(f"Gmail API error sending to {email_address}: {e}")
            print(f"❌ Failed to send email to {email_address}: {e}")
        except Exception as e:
            logger.error(f"Failed to send email to {email_address}: {e}")
            print(f"❌ Failed to send email to {email_address}: {e}")

    def _build_gmail_service_with_oauth(self, credentials_path: str, token_path: str):
        """Build Gmail service using OAuth credentials."""
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        creds = None

        # Load existing token if available
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        # If no valid credentials, need to authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                from google_auth_oauthlib.flow import InstalledAppFlow
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        return build('gmail', 'v1', credentials=creds)

    def _build_gmail_service_with_service_account(self, service_account_path: str, delegate_to: str):
        """Build Gmail service using service account with domain-wide delegation."""
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']

        credentials = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=SCOPES
        )

        # Delegate to the user email address
        delegated_credentials = credentials.with_subject(delegate_to)

        return build('gmail', 'v1', credentials=delegated_credentials)


def load_config(config_path: Optional[str]) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    if not config_path:
        return {}

    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Failed to parse config file: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Generate team changes summary with multiple output options')
    parser.add_argument('--config', help='Path to YAML config file')
    parser.add_argument('--repos', help='Comma-separated list of repositories (owner/repo)')
    parser.add_argument('--labels', help='Comma-separated list of labels to filter')
    parser.add_argument('--usernames', help='Comma-separated list of usernames to filter')
    parser.add_argument('--time-range', help='Time range (e.g., 24h, 7d)')
    parser.add_argument('--github-username', help='Your GitHub username (for PRs awaiting review and comments on your PRs)')
    parser.add_argument('--slack', action='append', help='Slack webhook URL (can be specified multiple times)')
    parser.add_argument('--email', action='append', help='Email address to send summary (can be specified multiple times)')
    parser.add_argument('--file', action='append', help='Output file path (can be specified multiple times)')

    args = parser.parse_args()

    # Load config from file or build from CLI args
    if args.config:
        config = load_config(args.config)
    else:
        config = {}

    # CLI args override config file
    if args.repos:
        config['repos'] = [r.strip() for r in args.repos.split(',')]
    if args.labels:
        config['labels'] = [l.strip() for l in args.labels.split(',')]
    if args.usernames:
        config['usernames'] = [u.strip() for u in args.usernames.split(',')]
    if args.time_range:
        config['time_range'] = args.time_range
    if args.github_username:
        config['github_username'] = args.github_username
    if args.slack:
        config['slack_urls'] = args.slack
    if args.email:
        config['email_addresses'] = args.email
    if args.file:
        config['output_files'] = args.file

    # Validate required config
    if not config.get('repos'):
        logger.error("No repositories specified. Use --repos or config file")
        sys.exit(1)

    # Require at least one output method
    has_output = (
        config.get('slack_urls') or
        config.get('email_addresses') or
        config.get('output_files')
    )
    if not has_output:
        logger.error("At least one output method required: --slack, --email, or --file")
        sys.exit(1)

    try:
        summary_generator = GitHubSummary(config)
        summary_generator.run()
    except Exception as e:
        logger.error(f"Failed to generate summary: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
