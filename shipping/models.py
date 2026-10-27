"""Domain models for the Tradexa box-selection system.

Units are deliberately plain and documented here so every caller uses the
same convention: dimensions in centimetres, weight in kilograms, cost in
Indian rupees (INR). All dimension/weight fields are Decimals so that
money and measurements are never rounded by binary floating point.
"""

from decimal import Decimal

from django.db import models


class Product(models.Model):
    """A sellable product with physical dimensions and weight."""

    name = models.CharField(max_length=200)
    length = models.DecimalField(max_digits=10, decimal_places=2)
    width = models.DecimalField(max_digits=10, decimal_places=2)
    height = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):  # pragma: no cover - display helper
        return self.name

    @property
    def dimensions(self):
        """Dimensions as a tuple, in the order stored."""
        return (self.length, self.width, self.height)

    @property
    def volume(self):
        """Product volume in cubic centimetres."""
        return self.length * self.width * self.height


class Box(models.Model):
    """A shipping box with internal dimensions, a weight limit and a cost."""

    name = models.CharField(max_length=200)
    internal_length = models.DecimalField(max_digits=10, decimal_places=2)
    internal_width = models.DecimalField(max_digits=10, decimal_places=2)
    internal_height = models.DecimalField(max_digits=10, decimal_places=2)
    max_weight = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):  # pragma: no cover - display helper
        return self.name

    @property
    def internal_dimensions(self):
        return (self.internal_length, self.internal_width, self.internal_height)

    @property
    def internal_volume(self):
        return self.internal_length * self.internal_width * self.internal_height


class Order(models.Model):
    """A customer order. Items are attached via OrderItem."""

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):  # pragma: no cover - display helper
        return f"Order {self.pk}"

    @property
    def total_weight(self):
        return sum(
            (item.product.weight * item.quantity for item in self.items.all()),
            Decimal("0"),
        )

    @property
    def total_volume(self):
        return sum(
            (item.product.volume * item.quantity for item in self.items.all()),
            Decimal("0"),
        )


class OrderItem(models.Model):
    """One product line on an order, with a quantity."""

    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.quantity} x {self.product.name}"
