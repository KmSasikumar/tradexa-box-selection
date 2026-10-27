"""Tests for the box-recommendation system.

Every test uses plain, hand-computed numbers so the expected result can
be checked by reading the test, not by trusting the code under test.
Dimensions in cm, weight in kg, cost in INR.
"""

from django.test import TestCase
from rest_framework.test import APIClient

from .models import Box, Order, OrderItem, Product
from .services import recommend_box


def make_product(name, l, w, h, weight):
    return Product.objects.create(
        name=name, length=l, width=w, height=h, weight=weight
    )


def make_box(name, l, w, h, max_weight, cost):
    return Box.objects.create(
        name=name,
        internal_length=l,
        internal_width=w,
        internal_height=h,
        max_weight=max_weight,
        cost=cost,
    )


def make_order(items):
    """items: list of (product, quantity)."""
    order = Order.objects.create()
    for product, qty in items:
        OrderItem.objects.create(order=order, product=product, quantity=qty)
    return order


class RecommendationServiceTests(TestCase):
    def test_fits_exactly(self):
        """Product exactly equal to the box on every side, weight and
        volume at the limit, still fits (rules use <=, not <)."""
        product = make_product("Exact", 10, 20, 30, 5)
        box = make_box("ExactBox", 10, 20, 30, 5, 100)
        order = make_order([(product, 1)])
        recommended, _ = recommend_box(order)
        self.assertEqual(recommended, box)

    def test_too_heavy_rejected(self):
        """Order weight 12 kg against a 10 kg box: rejected even though
        dimensions and volume fit."""
        product = make_product("Heavy", 10, 10, 10, 12)
        box = make_box("LightBox", 50, 50, 50, 10, 50)
        order = make_order([(product, 1)])
        recommended, evaluations = recommend_box(order)
        self.assertIsNone(recommended)
        self.assertFalse(evaluations[0]["fits"])
        self.assertTrue(
            any("weight" in r for r in evaluations[0]["reasons"]),
            evaluations[0]["reasons"],
        )

    def test_too_large_in_one_dimension_rejected(self):
        """A product 5 cm too tall for the box is rejected even though
        its weight and total volume are well within limits."""
        product = make_product("Tall", 10, 10, 55, 1)
        box = make_box("ShortBox", 50, 50, 50, 100, 50)
        order = make_order([(product, 1)])
        recommended, evaluations = recommend_box(order)
        self.assertIsNone(recommended)
        self.assertTrue(
            any("does not fit" in r for r in evaluations[0]["reasons"]),
            evaluations[0]["reasons"],
        )

    def test_rotation_allowed(self):
        """Product 40 x 10 x 5 stored in that orientation fits a box
        stored as 12 x 45 x 8: only a rotation makes it fit, and the
        sorted-dimension comparison allows it. A naive direct
        side-by-side comparison (40 > 12) would wrongly reject it."""
        product = make_product("LongItem", 40, 10, 5, 1)
        box = make_box("RotatedBox", 12, 45, 8, 10, 60)
        order = make_order([(product, 1)])
        recommended, _ = recommend_box(order)
        self.assertEqual(recommended, box)

    def test_volume_only_would_wrongly_accept(self):
        """The trap the design notes warn about: a 100 x 2 x 2 item
        (400 cm^3) against a 20 x 20 x 20 box (8000 cm^3). Volume alone
        says yes; the dimension check says no, because 100 > 20."""
        product = make_product("Pole", 100, 2, 2, 1)
        box = make_box("CubeBox", 20, 20, 20, 100, 40)
        order = make_order([(product, 1)])
        recommended, _ = recommend_box(order)
        self.assertIsNone(recommended)

    def test_cheapest_among_fitting_boxes_chosen(self):
        """Three fitting boxes at costs 200, 80 and 150: the 80 one wins,
        regardless of creation order."""
        product = make_product("Widget", 10, 10, 10, 1)
        make_box("Expensive", 50, 50, 50, 10, 200)
        cheap = make_box("Cheap", 50, 50, 50, 10, 80)
        make_box("Mid", 50, 50, 50, 10, 150)
        order = make_order([(product, 1)])
        recommended, _ = recommend_box(order)
        self.assertEqual(recommended, cheap)

    def test_no_box_case_returns_none(self):
        """An order heavier than every box returns None, not a forced
        fit, and every evaluation explains why."""
        product = make_product("Anvil", 10, 10, 10, 500)
        make_box("Small", 50, 50, 50, 10, 50)
        make_box("Large", 60, 60, 60, 20, 90)
        order = make_order([(product, 1)])
        recommended, evaluations = recommend_box(order)
        self.assertIsNone(recommended)
        self.assertEqual(len(evaluations), 2)
        self.assertTrue(all(not e["fits"] for e in evaluations))
        self.assertTrue(all(e["reasons"] for e in evaluations))

    def test_empty_order_returns_none(self):
        """An order with no items never yields a box."""
        make_box("AnyBox", 50, 50, 50, 10, 50)
        order = Order.objects.create()
        recommended, evaluations = recommend_box(order)
        self.assertIsNone(recommended)
        self.assertIn("no items", evaluations[0]["reasons"][0])

    def test_quantity_scales_weight_and_volume(self):
        """3 x a 4 kg, 1000 cm^3 product = 12 kg / 3000 cm^3: fits a
        15 kg, 5000 cm^3 box but not a 10 kg box."""
        product = make_product("Bulk", 10, 10, 10, 4)
        small = make_box("TooSmall", 50, 50, 50, 10, 50)
        big = make_box("BigEnough", 50, 50, 50, 15, 70)
        order = make_order([(product, 3)])
        recommended, evaluations = recommend_box(order)
        self.assertEqual(recommended, big)
        by_name = {e["box"].name: e for e in evaluations}
        self.assertFalse(by_name["TooSmall"]["fits"])
        self.assertTrue(by_name["BigEnough"]["fits"])
        self.assertNotIn(small, [recommended])


class RecommendationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_crud_and_recommend_endpoint(self):
        """End-to-end through the API: create product, create boxes,
        create an order, ask for a recommendation, get the cheapest fit
        with reasoning."""
        product = self.client.post(
            "/api/products/",
            {"name": "Book", "length": 20, "width": 15, "height": 3, "weight": 1},
            format="json",
        ).json()
        self.client.post(
            "/api/boxes/",
            {
                "name": "Big",
                "internal_length": 40,
                "internal_width": 40,
                "internal_height": 40,
                "max_weight": 10,
                "cost": 120,
            },
            format="json",
        )
        self.client.post(
            "/api/boxes/",
            {
                "name": "Small",
                "internal_length": 25,
                "internal_width": 20,
                "internal_height": 10,
                "max_weight": 5,
                "cost": 45,
            },
            format="json",
        )
        order = self.client.post(
            "/api/orders/",
            {"items": [{"product_id": product["id"], "quantity": 2}]},
            format="json",
        ).json()
        response = self.client.post(f"/api/orders/{order['id']}/recommend/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["recommended_box"]["name"], "Small")
        self.assertIn("cheapest", data["reason"])

    def test_recommend_endpoint_no_box_returns_null_with_reason(self):
        """API no-box case: recommended_box null, reason present, and
        the HTTP status is still 200 because 'no box' is a valid
        answer, not an error."""
        product = self.client.post(
            "/api/products/",
            {"name": "Brick", "length": 10, "width": 10, "height": 10, "weight": 99},
            format="json",
        ).json()
        self.client.post(
            "/api/boxes/",
            {
                "name": "Tiny",
                "internal_length": 50,
                "internal_width": 50,
                "internal_height": 50,
                "max_weight": 10,
                "cost": 30,
            },
            format="json",
        )
        order = self.client.post(
            "/api/orders/",
            {"items": [{"product_id": product["id"], "quantity": 1}]},
            format="json",
        ).json()
        response = self.client.post(f"/api/orders/{order['id']}/recommend/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["recommended_box"])
        self.assertTrue(data["reason"])
        self.assertFalse(data["evaluated_boxes"][0]["fits"])

    def test_recommend_endpoint_empty_order(self):
        """An order created with no items gets null + an explicit
        reason, not a crash and not a box."""
        order = self.client.post("/api/orders/", {"items": []}, format="json").json()
        response = self.client.post(f"/api/orders/{order['id']}/recommend/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["recommended_box"])
        self.assertIn("no items", data["reason"])
