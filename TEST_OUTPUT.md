# Test output (verbatim)

Command run: `python manage.py test shipping -v 2`
Result: 12 tests, all passing.

```
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Found 12 test(s).
Operations to perform:
  Synchronize unmigrated apps: messages, rest_framework, staticfiles
  Apply all migrations: admin, auth, contenttypes, sessions, shipping
Synchronizing apps without migrations:
  Creating tables...
    Running deferred SQL...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying sessions.0001_initial... OK
  Applying shipping.0001_initial...test_crud_and_recommend_endpoint (shipping.tests.RecommendationApiTests.test_crud_and_recommend_endpoint)
End-to-end through the API: create product, create boxes, ... ok
test_recommend_endpoint_empty_order (shipping.tests.RecommendationApiTests.test_recommend_endpoint_empty_order)
An order created with no items gets null + an explicit ... ok
test_recommend_endpoint_no_box_returns_null_with_reason (shipping.tests.RecommendationApiTests.test_recommend_endpoint_no_box_returns_null_with_reason)
API no-box case: recommended_box null, reason present, and ... ok
test_cheapest_among_fitting_boxes_chosen (shipping.tests.RecommendationServiceTests.test_cheapest_among_fitting_boxes_chosen)
Three fitting boxes at costs 200, 80 and 150: the 80 one wins, ... ok
test_empty_order_returns_none (shipping.tests.RecommendationServiceTests.test_empty_order_returns_none)
An order with no items never yields a box. ... ok
test_fits_exactly (shipping.tests.RecommendationServiceTests.test_fits_exactly)
Product exactly equal to the box on every side, weight and ... ok
test_no_box_case_returns_none (shipping.tests.RecommendationServiceTests.test_no_box_case_returns_none)
An order heavier than every box returns None, not a forced ... ok
test_quantity_scales_weight_and_volume (shipping.tests.RecommendationServiceTests.test_quantity_scales_weight_and_volume)
3 x a 4 kg, 1000 cm^3 product = 12 kg / 3000 cm^3: fits a ... ok
test_rotation_allowed (shipping.tests.RecommendationServiceTests.test_rotation_allowed)
Product 40 x 10 x 5 stored in that orientation fits a box ... ok
test_too_heavy_rejected (shipping.tests.RecommendationServiceTests.test_too_heavy_rejected)
Order weight 12 kg against a 10 kg box: rejected even though ... ok
test_too_large_in_one_dimension_rejected (shipping.tests.RecommendationServiceTests.test_too_large_in_one_dimension_rejected)
A product 5 cm too tall for the box is rejected even though ... ok
test_volume_only_would_wrongly_accept (shipping.tests.RecommendationServiceTests.test_volume_only_would_wrongly_accept)
The trap the design notes warn about: a 100 x 2 x 2 item ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.098s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
 OK
System check identified no issues (0 silenced).
```
