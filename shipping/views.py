"""API views: CRUD for products/boxes/orders plus the recommendation action."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Box, Order, Product
from .serializers import (
    BoxSerializer,
    OrderSerializer,
    ProductSerializer,
    RecommendationBoxSerializer,
)
from .services import recommend_box


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("id")
    serializer_class = ProductSerializer


class BoxViewSet(viewsets.ModelViewSet):
    queryset = Box.objects.all().order_by("id")
    serializer_class = BoxSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by("id")
    serializer_class = OrderSerializer

    @action(detail=True, methods=["post"], url_path="recommend")
    def recommend(self, request, pk=None):
        """Recommend the cheapest fitting box for this order.

        Response:
            {"recommended_box": {...} | null,
             "reason": str | null,
             "evaluated_boxes": [{"box": {...}, "fits": bool,
                                  "reasons": [str, ...]}, ...]}
        A null recommended_box is an explicit "no suitable box" result,
        never a forced fit.
        """
        order = self.get_object()
        box, evaluations = recommend_box(order)

        evaluated = [
            {
                "box": RecommendationBoxSerializer(e["box"]).data,
                "fits": e["fits"],
                "reasons": e["reasons"],
            }
            for e in evaluations
        ]

        if box is None:
            if not order.items.exists():
                reason = "order has no items, so no box can be recommended"
            else:
                reason = (
                    "no suitable box: no box satisfies the weight, "
                    "dimension and volume rules for this order"
                )
            return Response(
                {
                    "recommended_box": None,
                    "reason": reason,
                    "evaluated_boxes": evaluated,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "recommended_box": RecommendationBoxSerializer(box).data,
                "reason": (
                    f"'{box.name}' is the cheapest box that fits: "
                    f"total weight {order.total_weight} kg within "
                    f"{box.max_weight} kg, every product fits inside "
                    f"{box.internal_length} x {box.internal_width} x "
                    f"{box.internal_height} cm in some orientation, and "
                    f"total volume {order.total_volume} cm^3 within "
                    f"{box.internal_volume} cm^3"
                ),
                "evaluated_boxes": evaluated,
            },
            status=status.HTTP_200_OK,
        )
