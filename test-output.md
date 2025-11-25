# GitHub Merge Summary

**Total PRs:** 8

**Report Period:** 2025-11-24 14:00 UTC to 2025-11-25 14:00 UTC

**Repositories:** [shop/world](https://github.com/shop/world)

**Filters:** Labels: Slice: delivery | Usernames: None

---
## [PR #286499: Clean up redundant `ActiveSupport::Testing::EventReporter` includes](https://github.com/shop/world/pull/286499)

**Issue Opened On:** 2025-11-24 17:57 UTC by [Adrianna Chang](https://github.com/adrianna-chang-shopify)

**Merged:** 2025-11-24 22:54 UTC

**Author:** [Adrianna Chang](https://github.com/adrianna-chang-shopify)

**Components:** //areas/core/shopify

**Labels:** Component: Shopify payments, Component: Payment processing, Component: Checkouts, Component: Online store, Component: Merchant marketing, Component: Apps, and 24 more

**Reviewers:** [Sophie Déziel](https://github.com/sophiedeziel), [Hartley McGuire](https://github.com/hmcguire-shopify), [George Ma](https://github.com/george-ma)

**Commenters:** None

## Summary

The codebase contained redundant code where test files were explicitly including `ActiveSupport::Testing::EventReporterAssertions`, but this was unnecessary duplication. These includes were likely copy-pasted across many test files throughout the codebase over time. The assertions provided by this module are already available by default in all test cases because `ActiveSupport::TestCase` (the base class for tests) automatically includes them. These redundant includes were probably remnants from an earlier time when the project had a local implementation of `EventReporterAssertions` before it was moved upstream to the framework level.

This pull request removes the redundant `include ActiveSupport::Testing::EventReporterAssertions` statements from 29 test files across multiple components of the Shopify platform. The affected areas span a wide range of functionality including apps framework, checkouts, delivery, fulfillments, merchandising, merchant marketing metrics, online store, and payment processing. No actual functionality was changed—the tests retain access to the same assertion methods, they just inherit them through the standard test case hierarchy instead of explicitly including them. This is purely a code cleanup that eliminates unnecessary boilerplate.

This change affects developers working on the Shopify codebase by reducing code clutter and making the test files cleaner and more maintainable. There is no impact on merchants, customers, or production systems since this only modifies test code. The cleanup helps prevent future confusion about whether these includes are necessary and sets a clearer pattern for new test files. No follow-up work is mentioned, as this is a straightforward deletion of redundant code that doesn't change test behavior.

## Related Resources

None found in PR description

### Changed Files

- [`areas/core/shopify/components/apps/framework/test/models/apps/management/shop_api_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/apps/framework/test/models/apps/management/shop_api_test.rb)
- [`areas/core/shopify/components/checkouts/core/test/support/storefront_carts/logger_test_helper.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/checkouts/core/test/support/storefront_carts/logger_test_helper.rb)
- [`areas/core/shopify/components/checkouts/graph_api/test/models/graph_api/admin/resolvers/abandoned_checkouts_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/checkouts/graph_api/test/models/graph_api/admin/resolvers/abandoned_checkouts_test.rb)
- [`areas/core/shopify/components/checkouts/one/test/controllers/checkouts/one/concerns/checkout_profile_preview_concern_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/checkouts/one/test/controllers/checkouts/one/concerns/checkout_profile_preview_concern_test.rb)
- [`areas/core/shopify/components/checkouts/one/test/models/checkouts/one/web/policies/extensible_discounts/discount_line_satisfaction_logger_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/checkouts/one/test/models/checkouts/one/web/policies/extensible_discounts/discount_line_satisfaction_logger_test.rb)
- [`areas/core/shopify/components/checkouts/one/test/services/checkouts/one/checkout_profile_context_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/checkouts/one/test/services/checkouts/one/checkout_profile_context_test.rb)
- [`areas/core/shopify/components/delivery/test/jobs/delivery/rate_groups_consistency_check_job_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/delivery/test/jobs/delivery/rate_groups_consistency_check_job_test.rb)
- [`areas/core/shopify/components/delivery/test/models/graph_api/admin/delivery_promise/mutations/shop_promise_program_turn_off_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/delivery/test/models/graph_api/admin/delivery_promise/mutations/shop_promise_program_turn_off_test.rb)
- [`areas/core/shopify/components/delivery/test/services/delivery/rate_groups_consistency_check/reporter_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/delivery/test/services/delivery/rate_groups_consistency_check/reporter_test.rb)
- [`areas/core/shopify/components/delivery/test/services/delivery_promise/shop_promise/notify_promise_provider_destroyed_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/delivery/test/services/delivery_promise/shop_promise/notify_promise_provider_destroyed_test.rb)
- [`areas/core/shopify/components/delivery/test/services/find_delivery_options_for_allocation_sets_test/find_delivery_options_for_allocation_sets_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/delivery/test/services/find_delivery_options_for_allocation_sets_test/find_delivery_options_for_allocation_sets_test.rb)
- [`areas/core/shopify/components/fulfillments/test/models/graph_api/admin/fulfillment_open_batch_loader_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/fulfillments/test/models/graph_api/admin/fulfillment_open_batch_loader_test.rb)
- [`areas/core/shopify/components/merchandising/test/services/merchandising/operations/product_set_service/metafield_save_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/merchandising/test/services/merchandising/operations/product_set_service/metafield_save_test.rb)
- [`areas/core/shopify/components/merchant_marketing/metrics/test/models/attribution/attributable_session_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/merchant_marketing/metrics/test/models/attribution/attributable_session_test.rb)
- [`areas/core/shopify/components/merchant_marketing/metrics/test/services/attribution/marketing_channel_classifier/result_fetcher_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/merchant_marketing/metrics/test/services/attribution/marketing_channel_classifier/result_fetcher_test.rb)
- ... and 14 more files

---

## [PR #284889: Add `model_name` override for `build_global_id`](https://github.com/shop/world/pull/284889)

**Issue Opened On:** 2025-11-21 19:18 UTC by [Scott Walkinshaw](https://github.com/swalkinshaw)

**Merged:** 2025-11-24 15:49 UTC

**Author:** [Scott Walkinshaw](https://github.com/swalkinshaw)

**Components:** //areas/core/shopify

**Labels:** Component: Retail, Component: Online store, Component: Merchant marketing, Component: Delivery, Component: Platform, Component: Subscriptions, and 24 more

**Reviewers:** [Greg MacWilliam](https://github.com/gmac), [Calvin Krug](https://github.com/HobbesKrug), [kevinz-shopify](https://github.com/kevinz-shopify)

**Commenters:** None

## Summary

Previously, methods that build GlobalIDs (unique identifiers used in GraphQL) automatically relied on a `graphql_name` property from GraphQL type classes. This created a tight coupling between the GlobalID building logic and GraphQL-specific components, which became problematic when trying to use this functionality outside of traditional GraphQL contexts. Specifically, the code required GraphQL schema members as ancestors, which wouldn't work well with Cardinal resolvers (a different type of API resolver pattern). This limitation meant the GlobalID module wasn't flexible enough for broader use cases across the codebase.

To address this, the PR adds a `model_name` keyword argument option to the `build_global_id` methods, allowing developers to explicitly specify a model name instead of automatically inferring it from GraphQL classes. This change makes the GlobalID module more flexible and represents the first step in reducing its dependency on GraphQL type classes. Additionally, the PR adds proper type annotations to the `GraphApi::GlobalId` module using Sorbet typing, which exposed numerous type inconsistencies throughout the codebase that were then corrected across approximately 24 files spanning multiple components including merchandising, delivery, customers, inventory, and sales.

This change primarily affects internal systems and developers working with GlobalIDs across various Shopify platform components. The modifications touch a wide range of services and models, from product feeds and delivery promises to marketing events and bulk operations, indicating this is a foundational change that improves code quality and flexibility throughout the system. While the immediate impact is on code maintainability and type safety, this sets the stage for future work in making the system more modular and less dependent on GraphQL-specific implementations, as mentioned in the linked GitHub issue about API foundations.

## Related Resources

- [GitHub Issue #1125](https://github.com/shop/issues-api-foundations/issues/1125) - Parent issue tracking this work

### Changed Files

- [`areas/core/shopify/components/channels/product_feeds/app/services/product_feeds/full_sync_payload_builder.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/channels/product_feeds/app/services/product_feeds/full_sync_payload_builder.rb)
- [`areas/core/shopify/components/channels/product_feeds/app/services/product_feeds/versioned_payload_builder.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/channels/product_feeds/app/services/product_feeds/versioned_payload_builder.rb)
- [`areas/core/shopify/components/customers/customer_account/app/models/customers/customer_account/extensibility/schema.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/customers/customer_account/app/models/customers/customer_account/extensibility/schema.rb)
- [`areas/core/shopify/components/delivery/app/models/delivery_promise/shop_promise/shop_eligibility/evaluator.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/delivery/app/models/delivery_promise/shop_promise/shop_eligibility/evaluator.rb)
- [`areas/core/shopify/components/delivery/app/models/graph_api/admin/delivery/rate_definition.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/delivery/app/models/graph_api/admin/delivery/rate_definition.rb)
- [`areas/core/shopify/components/delivery/shipping/app/services/shipping/processes/create_label_purchase_session.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/delivery/shipping/app/services/shipping/processes/create_label_purchase_session.rb)
- [`areas/core/shopify/components/delivery/test/models/graph_api/admin/delivery/mutations/shipping_label_create_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/delivery/test/models/graph_api/admin/delivery/mutations/shipping_label_create_test.rb)
- [`areas/core/shopify/components/domains/test/models/graph_api/admin/mutations/domain_verification_verify_txt_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/domains/test/models/graph_api/admin/mutations/domain_verification_verify_txt_test.rb)
- [`areas/core/shopify/components/inventory/test/models/graph_api/admin/mutations/purchase_order_receive_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/inventory/test/models/graph_api/admin/mutations/purchase_order_receive_test.rb)
- [`areas/core/shopify/components/merchandising/app/services/merchandising/componentized_products/consolidated_option_component.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/merchandising/app/services/merchandising/componentized_products/consolidated_option_component.rb)
- [`areas/core/shopify/components/merchandising/app/services/merchandising/componentized_products/errors.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/merchandising/app/services/merchandising/componentized_products/errors.rb)
- [`areas/core/shopify/components/merchandising/app/services/merchandising/componentized_products/input.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/merchandising/app/services/merchandising/componentized_products/input.rb)
- [`areas/core/shopify/components/merchant_marketing/test/models/graph_api/admin/marketing_event_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/merchant_marketing/test/models/graph_api/admin/marketing_event_test.rb)
- [`areas/core/shopify/components/online_store/app/decorators/online_store/image_decorator.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/online_store/app/decorators/online_store/image_decorator.rb)
- [`areas/core/shopify/components/platform/bulk_operations/test/models/graph_api/admin/mutations/bulk_operation_cancel_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/platform/bulk_operations/test/models/graph_api/admin/mutations/bulk_operation_cancel_test.rb)
- ... and 8 more files

---

## [PR #283679: Validate physical item with None merchandise lines before enforce_fulfillability](https://github.com/shop/world/pull/283679)

**Issue Opened On:** 2025-11-21 01:32 UTC by [maxromaniv](https://github.com/maxromaniv)

**Merged:** 2025-11-24 17:47 UTC

**Author:** [maxromaniv](https://github.com/maxromaniv)

**Components:** //areas/core/shopify

**Labels:** Component: Checkouts, Component: Delivery, #gsd:40934, //areas/core/shopify, Slice: checkouts, Slice: delivery

**Reviewers:** [Narges](https://github.com/nargesashrafizadeh), [Erik Ryhorchuk](https://github.com/erik-shopify), [Beth Townsend](https://github.com/beth92)

**Commenters:** None

## Summary

This pull request fixes a bug that occurred when processing checkout orders containing physical items with a "NONE" delivery method type. Previously, the system would validate these invalid configurations too late in the process, after some processing had already occurred. This timing issue caused the system to throw an unexpected `missing_method_type_fulfillability` error from the `EnforceFulfillability` component rather than catching the problem early with a proper validation error. The issue manifested when physical items (which require shipping) were incorrectly configured with no delivery method.

To resolve this, the validation logic was moved earlier in the checkout process flow within the `DefaultDeliveryStrategyFinder` service. The validation method was refactored and renamed to `physical_item_with_none_method_type?`, and it now checks merchandise lines directly instead of waiting for delivery options input results. This change ensures that the invalid configuration is caught and properly handled before the system attempts to enforce fulfillability rules. An integration test was also added to verify that the correct violation code is returned when this scenario occurs.

This change primarily affects the internal checkout processing system and improves error handling reliability. Merchants and customers benefit indirectly through more predictable error messages and prevention of unexpected system errors during checkout. The fix ensures that configuration issues are caught early and reported clearly, rather than causing downstream processing failures. This should result in better debugging capabilities for support teams and a more robust checkout experience overall.

## Related Resources

- [GitHub Issue #3192](https://github.com/shop/issues-fulfillment/issues/3192) - Original bug report for the missing_method_type_fulfillability error

### Changed Files

- [`areas/core/shopify/components/checkouts/one/test/integration/checkouts/one/web/contextual_inventory_integration_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/checkouts/one/test/integration/checkouts/one/web/contextual_inventory_integration_test.rb)
- [`areas/core/shopify/components/delivery/app/services/delivery/checkout_one/default_delivery_strategy_finder.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/delivery/app/services/delivery/checkout_one/default_delivery_strategy_finder.rb)
- [`areas/core/shopify/components/delivery/test/services/delivery/checkout_one/default_delivery_strategy_finder_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/delivery/test/services/delivery/checkout_one/default_delivery_strategy_finder_test.rb)

---

## [PR #281711: return NoOp in EnforceFulfillability for an all digital cart](https://github.com/shop/world/pull/281711)

**Issue Opened On:** 2025-11-20 06:08 UTC by [Erik Ryhorchuk](https://github.com/erik-shopify)

**Merged:** 2025-11-24 21:47 UTC

**Author:** [Erik Ryhorchuk](https://github.com/erik-shopify)

**Components:** //areas/core/shopify

**Labels:** Component: Checkouts, Component: Delivery, #gsd:40934, //areas/core/shopify, Slice: checkouts, Slice: delivery

**Reviewers:** [Narges](https://github.com/nargesashrafizadeh), [Beth Townsend](https://github.com/beth92), [maxromaniv](https://github.com/maxromaniv)

**Commenters:** None

## Summary

The system was encountering an issue when processing shopping carts that contained only digital products (like downloadable files or digital goods) but still had physical delivery methods specified in the checkout process. This mismatch could occur due to frontend complexity or through invalid cart states triggered by bots accessing checkout URLs directly with products. While this represents an invalid cart configuration, the backend was not handling this scenario gracefully, which could lead to errors or unexpected behavior during the checkout process.

To address this problem, the PR modifies the `EnforceFulfillability` service within the delivery component. A new method was added to detect when all merchandise lines in a cart are digital products. When this condition is met, the service now returns a `NoOp` (no operation) response, effectively skipping fulfillability enforcement since digital products don't require physical shipping or delivery validation. The changes were made across three files: the `EnforceFulfillability` service itself, its corresponding test file, and an integration test for contextual inventory in the checkouts component.

This change primarily affects the backend systems that process checkout requests, making them more resilient to invalid cart states. Customers attempting to checkout with all-digital carts (whether intentionally or through bot activity) will experience smoother processing without encountering fulfillability errors. The fix is defensive in nature, preventing edge cases from causing system failures while the frontend continues to handle the proper user experience for digital-only purchases.

## Related Resources

- [GitHub Issue #3193](https://github.com/shop/issues-fulfillment/issues/3193) - The original issue this PR closes

### Changed Files

- [`areas/core/shopify/components/checkouts/one/test/integration/checkouts/one/web/contextual_inventory_integration_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/checkouts/one/test/integration/checkouts/one/web/contextual_inventory_integration_test.rb)
- [`areas/core/shopify/components/delivery/app/services/delivery/processes/enforce_fulfillability.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/delivery/app/services/delivery/processes/enforce_fulfillability.rb)
- [`areas/core/shopify/components/delivery/test/services/delivery/processes/enforce_fulfillability_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/delivery/test/services/delivery/processes/enforce_fulfillability_test.rb)

---

## [PR #278910: ShipToStoreToCore: Update Location Transfer update service](https://github.com/shop/world/pull/278910)

**Issue Opened On:** 2025-11-18 18:22 UTC by [suhshinhwang](https://github.com/suhshinhwang)

**Merged:** 2025-11-24 18:44 UTC

**Author:** [suhshinhwang](https://github.com/suhshinhwang)

**Components:** //areas/core/shopify

**Labels:** Component: Delivery, //areas/core/shopify, Slice: delivery, #gsd:47627

**Reviewers:** [Mathyas](https://github.com/mathyasp), [F.D.](https://github.com/fekadeabdejene)

**Commenters:** None

## Summary

**Problem/Motivation:** The existing location transfer update service in the delivery system only supported updating a single location transfer at a time. This limitation meant that API clients had to make multiple separate requests if they needed to modify multiple location transfers, which was inefficient and created a poor user experience. Additionally, the previous implementation did not provide comprehensive validation feedback, potentially requiring multiple round-trips to identify and fix all issues.

**Solution:** The update service was modified to support bulk operations, allowing multiple location transfers to be updated in a single API call. The changes were made to the `update_location_transfer_route.rb` service file and its corresponding test file `update_location_transfer_route_test.rb` in the delivery component. The new implementation validates all input elements upfront and returns all validation errors at once rather than failing on the first error encountered, enabling clients to see and fix all issues in one go.

**Impact:** This change primarily benefits internal systems and API clients (such as ShipToStore integrations) that need to update multiple location transfers efficiently. The bulk operation support reduces the number of API calls required, improving performance and reducing network overhead. The improved error handling that returns all validation errors simultaneously significantly enhances the developer experience by eliminating the need for multiple submission attempts to discover all validation issues. This should streamline workflows for any systems managing inventory transfers across multiple locations.

## Related Resources

None found in PR description

### Changed Files

- [`areas/core/shopify/components/delivery/app/services/delivery/update_location_transfer_route.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/delivery/app/services/delivery/update_location_transfer_route.rb)
- [`areas/core/shopify/components/delivery/test/services/delivery/update_location_transfer_route_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/delivery/test/services/delivery/update_location_transfer_route_test.rb)

---

## [PR #277670: Cleanup various beta flags](https://github.com/shop/world/pull/277670)

**Issue Opened On:** 2025-11-17 20:54 UTC by [Chris](https://github.com/chrislessard)

**Merged:** 2025-11-24 16:35 UTC

**Author:** [Chris](https://github.com/chrislessard)

**Components:** //areas/core/shopify

**Labels:** Component: Checkouts, Component: Delivery, Component: Markets, Component: Draft orders, ⚙️ Backend, //areas/core/shopify, and 5 more

**Reviewers:** [Jeff Rothwell](https://github.com/jeffro-shopify), [joykliu](https://github.com/joykliu), [Julie Huguet](https://github.com/LittleCatBear)

**Commenters:** None

## Summary

This pull request removes five feature flags that are no longer needed because they have either been fully rolled out to 100% of users or were never actually used in production. These flags controlled various behaviors related to international commerce features like duty-inclusive pricing, Managed Markets validation for draft orders, and pricing strategy migrations. Before this change, the codebase contained conditional logic that checked these flags to determine whether certain features should be enabled, creating unnecessary complexity now that the features are permanently enabled or obsolete.

The changes were made by removing flag checks and simplifying the code to assume the new behavior is always active. Files modified span multiple components including checkouts, draft orders, markets, and sales. Specifically, code in the order editing system no longer checks a flag before handling duty-inclusive pricing scenarios, draft order validation always performs Managed Markets checks for incoterm requirements, and an unused method related to landed cost migrations was removed. The market pricing strategy killswitch flag was also removed since the underlying feature has been stable for over six months.

This cleanup primarily impacts internal development by reducing technical debt and making the codebase easier to maintain. Merchants and customers should see no change in behavior since these features were already enabled in production. The removal of these flags eliminates potential confusion for developers who might encounter outdated conditional logic, and reduces the surface area for bugs related to flag configuration. No follow-up work is mentioned, suggesting this is a straightforward cleanup with no additional dependencies.

## Related Resources

None found in PR description

### Changed Files

- [`areas/core/shopify/components/checkouts/one/app/models/checkouts/one/web/policies/artifact/market_manager_override_artifact_policy.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/checkouts/one/app/models/checkouts/one/web/policies/artifact/market_manager_override_artifact_policy.rb)
- [`areas/core/shopify/components/checkouts/one/test/models/checkouts/one/web/policies/artifact/market_manager_override_artifact_policy_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/checkouts/one/test/models/checkouts/one/web/policies/artifact/market_manager_override_artifact_policy_test.rb)
- [`areas/core/shopify/components/delivery/test/integration/default_delivery_policy_integration_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/delivery/test/integration/default_delivery_policy_integration_test.rb)
- [`areas/core/shopify/components/draft_orders/app/services/draft_orders/completion_validations.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/draft_orders/app/services/draft_orders/completion_validations.rb)
- [`areas/core/shopify/components/draft_orders/test/services/draft_orders/complete_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/draft_orders/test/services/draft_orders/complete_test.rb)
- [`areas/core/shopify/components/draft_orders/test/services/draft_orders/complete_with_payment_processing_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/draft_orders/test/services/draft_orders/complete_with_payment_processing_test.rb)
- [`areas/core/shopify/components/markets/app/models/markets/feature_set_extension.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/markets/app/models/markets/feature_set_extension.rb)
- [`areas/core/shopify/components/markets/test/models/markets/feature_set_extension_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/markets/test/models/markets/feature_set_extension_test.rb)
- [`areas/core/shopify/components/sales/app/models/sales/order_editing/landed_cost_associator.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/sales/app/models/sales/order_editing/landed_cost_associator.rb)
- [`areas/core/shopify/components/sales/test/models/sales/order_editing/landed_cost_associator_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/sales/test/models/sales/order_editing/landed_cost_associator_test.rb)

---

## [PR #259645: [Taxes] Update tax calculations to support online checkout split carts](https://github.com/shop/world/pull/259645)

**Issue Opened On:** 2025-11-04 14:29 UTC by [Lucas Medeiros](https://github.com/lucasmedeirosleite)

**Merged:** 2025-11-24 18:08 UTC

**Author:** [Lucas Medeiros](https://github.com/lucasmedeirosleite)

**Components:** //areas/core/shopify

**Labels:** Component: Checkouts, Component: Taxes, Component: Delivery, //areas/core/shopify, Slice: taxes, Do not merge, and 3 more

**Reviewers:** [Joshua Murray](https://github.com/joshcom), [Ryan Creps](https://github.com/rcreps-shopify), [Dave Rose](https://github.com/drose-shopify), [Sunitha Patel](https://github.com/sunithapatel)

**Commenters:** None

## Summary

This pull request addresses the need to calculate taxes correctly for "split carts" in the online checkout flow. A split cart occurs when items in a single checkout need to be shipped separately or handled differently for tax purposes. Previously, the tax calculation system didn't properly support these online checkout split cart scenarios, even though the foundational pieces (address handling, tax delivery groups, cross-border detection) had already been implemented. The system needed to be updated to recognize when an online checkout contains a split cart and apply the appropriate tax calculation logic using multiple delivery groups instead of treating everything as a single shipment.

The changes were made primarily to the `TaxRequestMapper` service, specifically updating the `tax_calculation_eligible_for_multiple_delivery_groups?` method to leverage a new eligibility checker class called `Checkouts::One::SplitCart::Online::TaxEligibility`. This allows the system to identify online checkout split carts and route them through the delivery group-based tax calculation flow. The modifications include updates to the core tax request mapping logic, associated test files to verify the new behavior, mock factory helpers for testing, and the delivery group schema model. All changes are protected behind a feature flag (`f_checkout_split_delivery_taxes_support`), making it safe to enable or disable without risk.

This change primarily affects customers making purchases through online checkout where their cart contains items that need to be split for delivery or tax purposes, ensuring they see accurate tax calculations. Merchants benefit indirectly through more accurate tax collection and compliance. The change is safe to rollback since it's feature-flagged, and the team has identified follow-up work to expand the C1 `OrderBuilder` to also support building multiple tax calculation facts for online split carts, completing the end-to-end implementation.

## Related Resources

- [GitHub Issue #7824](https://github.com/shop/issues-checkout/issues/7824)

### Changed Files

- [`areas/core/shopify/components/checkouts/one/app/services/checkouts/one/taxes/tax_request_mapper.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/checkouts/one/app/services/checkouts/one/taxes/tax_request_mapper.rb)
- [`areas/core/shopify/components/checkouts/one/test/services/checkouts/one/taxes/tax_request_mapper_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/checkouts/one/test/services/checkouts/one/taxes/tax_request_mapper_test.rb)
- [`areas/core/shopify/components/delivery/test/support/helpers/delivery/checkout_one/mock_factory.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/delivery/test/support/helpers/delivery/checkout_one/mock_factory.rb)
- [`areas/core/shopify/components/taxes/app/models/taxes/delivery_group_schema.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/taxes/app/models/taxes/delivery_group_schema.rb)
- [`areas/core/shopify/components/taxes/test/models/taxes/delivery_group_schema_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/taxes/test/models/taxes/delivery_group_schema_test.rb)
- [`areas/core/shopify/test/deprecations/components/checkouts/checkouts/one/taxes/tax_request_mapper_test.yml`](https://github.com/shop/world/blob/main/areas/core/shopify/test/deprecations/components/checkouts/checkouts/one/taxes/tax_request_mapper_test.yml)

---

## [PR #162410: Remove the flag for use session data for shopify_pay cookie](https://github.com/shop/world/pull/162410)

**Issue Opened On:** 2025-08-29 21:29 UTC by [Hanying (Elsa) Huang](https://github.com/hyhuang1218)

**Merged:** 2025-11-24 17:33 UTC

**Author:** [Hanying (Elsa) Huang](https://github.com/hyhuang1218)

**Components:** //areas/core/shopify

**Labels:** Component: Checkouts, Component: Online store, Component: Access and auth, Component: Self Serve, Component: Delivery, //areas/core/shopify, and 10 more

**Reviewers:** [Stijn Heymans](https://github.com/sheymans), [Bastian Schon](https://github.com/serioushaircut)

**Commenters:** [stale-pr-closer](https://github.com/stale-pr-closer)

## Summary

This pull request removes a feature flag that was controlling how Shopify Pay cookies are handled during user authentication. Previously, the system had two different methods for managing these cookies: a newer approach using SessionData and an older approach using AuthorizationCookieService. A feature flag had been introduced months ago to gradually roll out the SessionData approach, and since that flag has been enabled and stable for an extended period, it's now safe to remove the conditional logic and fully commit to the new implementation.

The changes primarily affect the login and authentication components within Shopify's checkout system. Multiple controllers, services, and models related to Shopify Pay authentication were modified to remove the feature flag checks and the legacy AuthorizationCookieService code paths. Files across the access_and_auth/login_with_shop component and checkouts components were updated, including the authorize controller, session services, cookie validators, and various Shopify Pay models. Most significantly, the test files were cleaned up to remove duplicated test cases that were previously needed to verify both the old and new cookie handling approaches worked correctly.

This change affects internal systems that handle Shopify Pay authentication flows during checkout. Merchants and customers should see no visible changes since the new SessionData approach has already been the active code path for months. The impact is primarily positive: the codebase is now simpler and easier to maintain without the conditional logic and duplicated tests, reducing technical debt and the potential for bugs. No follow-up work is mentioned, suggesting this is a complete cleanup of the feature flag rollout.

## Related Resources

- [Shopify/shop-identity#5999](https://github.com/Shopify/shop-identity/issues/5999) - Related issue in the shop-identity repository

### Changed Files

- [`areas/core/shopify/components/access_and_auth/login_with_shop/app/controllers/access_and_auth/login_with_shop/authorize_controller.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/access_and_auth/login_with_shop/app/controllers/access_and_auth/login_with_shop/authorize_controller.rb)
- [`areas/core/shopify/components/access_and_auth/login_with_shop/app/controllers/access_and_auth/login_with_shop/concerns/shopify_pay_cookie_analyzer.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/access_and_auth/login_with_shop/app/controllers/access_and_auth/login_with_shop/concerns/shopify_pay_cookie_analyzer.rb)
- [`areas/core/shopify/components/access_and_auth/login_with_shop/app/controllers/access_and_auth/login_with_shop/concerns/shopify_pay_cookie_validator.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/access_and_auth/login_with_shop/app/controllers/access_and_auth/login_with_shop/concerns/shopify_pay_cookie_validator.rb)
- [`areas/core/shopify/components/access_and_auth/login_with_shop/app/services/access_and_auth/login_with_shop/shopify_pay_session_service.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/access_and_auth/login_with_shop/app/services/access_and_auth/login_with_shop/shopify_pay_session_service.rb)
- [`areas/core/shopify/components/access_and_auth/login_with_shop/test/controllers/access_and_auth/login_with_shop/authorize_controller_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/access_and_auth/login_with_shop/test/controllers/access_and_auth/login_with_shop/authorize_controller_test.rb)
- [`areas/core/shopify/components/access_and_auth/login_with_shop/test/controllers/access_and_auth/login_with_shop/concerns/shopify_pay_cookie_analyzer_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/access_and_auth/login_with_shop/test/controllers/access_and_auth/login_with_shop/concerns/shopify_pay_cookie_analyzer_test.rb)
- [`areas/core/shopify/components/access_and_auth/login_with_shop/test/controllers/access_and_auth/login_with_shop/concerns/shopify_pay_cookie_validator_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/access_and_auth/login_with_shop/test/controllers/access_and_auth/login_with_shop/concerns/shopify_pay_cookie_validator_test.rb)
- [`areas/core/shopify/components/access_and_auth/login_with_shop/test/controllers/access_and_auth/login_with_shop/login_controller_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/access_and_auth/login_with_shop/test/controllers/access_and_auth/login_with_shop/login_controller_test.rb)
- [`areas/core/shopify/components/access_and_auth/login_with_shop/test/services/access_and_auth/login_with_shop/shopify_pay_session_service_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/access_and_auth/login_with_shop/test/services/access_and_auth/login_with_shop/shopify_pay_session_service_test.rb)
- [`areas/core/shopify/components/checkouts/one/app/models/checkouts/one/receipt.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/checkouts/one/app/models/checkouts/one/receipt.rb)
- [`areas/core/shopify/components/checkouts/one/app/models/checkouts/one/web/shop_pay/config.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/checkouts/one/app/models/checkouts/one/web/shop_pay/config.rb)
- [`areas/core/shopify/components/checkouts/one/app/models/checkouts/one/web/shop_pay/remember_me.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/checkouts/one/app/models/checkouts/one/web/shop_pay/remember_me.rb)
- [`areas/core/shopify/components/checkouts/one/test/models/checkouts/one/receipt_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/checkouts/one/test/models/checkouts/one/receipt_test.rb)
- [`areas/core/shopify/components/checkouts/one/test/models/checkouts/one/web/shop_pay/config_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/checkouts/one/test/models/checkouts/one/web/shop_pay/config_test.rb)
- [`areas/core/shopify/components/checkouts/one/test/models/checkouts/one/web/shop_pay/remember_me_test.rb`](https://github.com/shop/world/blob/main/areas/core/shopify/components/checkouts/one/test/models/checkouts/one/web/shop_pay/remember_me_test.rb)
- ... and 17 more files

---

## Summary Statistics

- **Total PRs:** 8
- **Authors:** 8 unique contributors
- **Files Changed:** 108 files across all PRs
