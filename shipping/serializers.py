"""Serializers for the box-selection API."""

from rest_framework import serializers

from .models import Box, Order, OrderItem, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "length", "width", "height", "weight"]


class BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = [
            "id",
            "name",
            "internal_length",
            "internal_width",
            "internal_height",
            "max_weight",
            "cost",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_id", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total_weight = serializers.ReadOnlyField()
    total_volume = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ["id", "created_at", "items", "total_weight", "total_volume"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        order = Order.objects.create()
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order


class RecommendationBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = [
            "id",
            "name",
            "internal_length",
            "internal_width",
            "internal_height",
            "max_weight",
            "cost",
        ]
