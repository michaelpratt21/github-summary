# Email Setup for GitHub Merge Summary

Three methods to send email reports, in order of easiest to hardest:

---

## Method 1: Google App Password (Easiest - 2 minutes)

**Best for:** Personal testing, quick setup

### Steps:

1. **Enable 2-Factor Authentication** (if not already enabled)
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Create App Password**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (custom name)"
   - Name it "GitHub Summary Script"
   - Click "Generate"
   - Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)

3. **Set Environment Variables**
   ```bash
   export SMTP_USER="michael.pratt@shopify.com"
   export SMTP_PASSWORD="xxxx xxxx xxxx xxxx"  # Your app password
   export SMTP_FROM="michael.pratt@shopify.com"
   ```

4. **Test It**
   ```bash
   export OPENAI_API_KEY="your-key"

   scripts/venv/bin/python3 scripts/team_changes_summary.py \
     --repos "shop/world" \
     --labels "Slice: delivery" \
     --time-range 6h \
     --email michael.pratt@shopify.com
   ```

**Pros:**
- Works immediately
- No API setup needed
- No admin approval required

**Cons:**
- Less secure than OAuth
- Password expires if you disable 2FA
- One password per person (can't share for automation)

---

## Method 2: Internal SMTP Relay (Best for Teams/Automation)

**Best for:** Team automation, cron jobs, shared scripts

Ask your IT/DevOps team if Shopify has an internal SMTP relay. Most large companies do.

### Common Setup:

```bash
export SMTP_HOST="smtp.internal.shopify.com"  # Ask IT for correct host
export SMTP_PORT="25"  # Or 587, ask IT
export SMTP_USER=""  # Often not needed for internal relay
export SMTP_PASSWORD=""  # Often not needed for internal relay
export SMTP_FROM="noreply@shopify.com"  # Or your team email
```

### Test It:
```bash
scripts/venv/bin/python3 scripts/team_changes_summary.py \
  --repos "shop/world" \
  --labels "Slice: delivery" \
  --time-range 6h \
  --email team@shopify.com
```

**Pros:**
- Designed for automation
- No personal credentials needed
- More reliable for high volume
- Can send as team/service account

**Cons:**
- Need to ask IT for details
- May have sending limits
- May require VPN/internal network

---

## Method 3: SMTP with OAuth2 (Most Secure)

**Best for:** When you want OAuth security without Gmail API

This uses SMTP but with OAuth tokens instead of passwords.

### Steps:

1. **Create OAuth Credentials** (one-time setup)
   - Go to https://console.cloud.google.com/
   - Create/select a project
   - Go to "APIs & Services" > "Credentials"
   - Create "OAuth client ID" > "Desktop app"
   - Download JSON file

2. **Set Environment Variables**
   ```bash
   export EMAIL_METHOD="smtp-oauth"
   export GMAIL_CREDENTIALS_PATH="/path/to/client_secret.json"
   export SMTP_FROM="michael.pratt@shopify.com"
   ```

3. **First Run** (opens browser for authentication)
   ```bash
   scripts/venv/bin/python3 scripts/team_changes_summary.py \
     --repos "shop/world" \
     --labels "Slice: delivery" \
     --time-range 6h \
     --email michael.pratt@shopify.com
   ```

4. **Future Runs** (uses saved token, no browser)

**Pros:**
- More secure than app passwords
- Token auto-refreshes
- Doesn't require Gmail API to be enabled

**Cons:**
- Requires Google Cloud project setup
- Browser auth on first run
- More complex setup

---

## Quick Comparison

| Method | Setup Time | Security | Automation | Admin Approval |
|--------|------------|----------|------------|----------------|
| App Password | 2 min | ⭐⭐⭐ | ⭐⭐ | ❌ Not needed |
| SMTP Relay | 5 min | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Ask IT |
| SMTP OAuth | 10 min | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ Not needed |

---

## Troubleshooting

### Error: "SMTP credentials not configured"
```bash
# Make sure you set both variables:
export SMTP_USER="your.email@shopify.com"
export SMTP_PASSWORD="your-app-password"
```

### Error: "Authentication failed"
- **App Password:** Make sure 2FA is enabled, regenerate password
- **Internal Relay:** Check if VPN/internal network is required
- **OAuth:** Delete `gmail_token.json` and re-authenticate

### Error: "Connection refused" or "Timeout"
- Check `SMTP_HOST` and `SMTP_PORT` values
- Verify you're on correct network (VPN for internal relay)
- Test with `telnet $SMTP_HOST $SMTP_PORT`

### Email not received
- Check spam folder
- Verify recipient email address
- Check sender reputation (if using internal relay)
- Look for bounce-back messages

---

## Recommended for Shopify

**For personal use:** Start with **App Password** (Method 1)

**For team automation:** Ask IT about **SMTP Relay** (Method 2), something like:
> "Hi IT, we're automating GitHub PR summaries. Does Shopify have an internal SMTP relay we can use for sending automated emails? We need the hostname, port, and auth requirements."

**Security note:** Store credentials securely:
- Use environment variables (not hardcoded)
- Add to `.gitignore` if using files
- Consider using Shopify's secrets management (Vault)
