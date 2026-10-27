"""Box-recommendation algorithm.

Fit rules (all three must hold for a box to fit an order):

1. Weight: total order weight <= box max_weight.
2. Dimensions per product, rotation allowed: for EVERY product in the
   order, the product's dimensions, sorted smallest-to-largest, must each
   be <= the box's internal dimensions, also sorted smallest-to-largest.
   Sorting is what allows rotation: a 40 x 10 x 10 item fits a
   30 x 20 x 15 box only if some orientation works, and comparing sorted
   sides is the correct test for a rectangular item in a rectangular box.
   (It is a necessary condition; it does not attempt 3D bin packing of
   several items side by side, which the spec does not ask for.)
3. Volume: total product volume <= box internal volume.

Among fitting boxes the cheapest (lowest cost) wins. Ties break on the
smallest box id so the result is deterministic.

Why not volume alone? Volume alone would let a 100 cm long item "fit" a
10 x 10 x 10 box whose volume happens to be large enough in total but
whose sides are all far too short. The per-product dimension check is
what stops that. See README.md and LEARNINGS.md for a worked example.

A box that does not fit reports exactly which rule(s) it failed, so the
API response can explain itself instead of returning a bare rejection.
"""


def _sorted_dims(dims):
    return tuple(sorted(dims))


def product_fits_box(product, box):
    """True if this one product fits inside this box, rotation allowed."""
    return all(
        p <= b
        for p, b in zip(
            _sorted_dims(product.dimensions), _sorted_dims(box.internal_dimensions)
        )
    )


def evaluate_box(order, box):
    """Evaluate one box against an order.

    Returns a dict with the fit verdict and the reason(s) for failure.
    """
    reasons = []
    items = list(order.items.select_related("product").all())

    if not items:
        return {
            "box": box,
            "fits": False,
            "reasons": ["order has no items, so no box can be recommended"],
        }

    if order.total_weight > box.max_weight:
        reasons.append(
            f"total weight {order.total_weight} kg exceeds "
            f"box capacity {box.max_weight} kg"
        )

    for item in items:
        if not product_fits_box(item.product, box):
            reasons.append(
                f"product '{item.product.name}' "
                f"({item.product.length} x {item.product.width} x "
                f"{item.product.height} cm) does not fit inside box "
                f"'{box.name}' ({box.internal_length} x {box.internal_width} x "
                f"{box.internal_height} cm) in any orientation"
            )

    if order.total_volume > box.internal_volume:
        reasons.append(
            f"total volume {order.total_volume} cm^3 exceeds "
            f"box internal volume {box.internal_volume} cm^3"
        )

    return {"box": box, "fits": not reasons, "reasons": reasons}


def recommend_box(order, boxes=None):
    """Recommend the cheapest fitting box for an order, or None.

    Returns (box_or_None, evaluations) where evaluations is the list of
    per-box dicts from evaluate_box, so callers can show the reasoning.
    An empty order never yields a box: recommending a box for nothing
    would be a forced fit, so it returns None with an explicit reason.
    """
    if boxes is None:
        from .models import Box

        boxes = Box.objects.all()

    items = list(order.items.select_related("product").all())
    if not items:
        return None, [
            {
                "box": box,
                "fits": False,
                "reasons": ["order has no items, so no box can be recommended"],
            }
            for box in boxes
        ]

    evaluations = [evaluate_box(order, box) for box in boxes]
    fitting = [e for e in evaluations if e["fits"]]
    if not fitting:
        return None, evaluations

    cheapest = min(fitting, key=lambda e: (e["box"].cost, e["box"].pk))
    return cheapest["box"], evaluations
