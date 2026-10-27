# Tradexa — Box Selection for Orders

A small Django + Django REST Framework system built for the Tradexa
hiring assignment. A warehouse needs to know which shipping box to use
for an order. This service recommends the most suitable box, and says
so explicitly when no box fits.

## The fit rules

A box fits an order only if **all three** hold:

1. **Weight** — total order weight (sum of quantity × product weight)
   is less than or equal to the box's `max_weight`.
2. **Dimensions, rotation allowed** — for **every** product in the order,
   the product's dimensions, sorted smallest-to-largest, are each less
   than or equal to the box's internal dimensions, also sorted
   smallest-to-largest. Sorting is what allows rotation: an item may be
   turned on any side, but it may not stick out of the box.
3. **Volume** — total product volume is less than or equal to the box's
   internal volume.

Among fitting boxes, the **cheapest** (lowest `cost`) is recommended.
Ties break on the smallest box id, so the answer is deterministic.

If no box fits, the API returns `recommended_box: null` plus a reason —
never a forced fit.

### Why not volume alone?

Volume alone would approve nonsense. A 100 × 2 × 2 cm item has a volume
of only 400 cm³, so it "fits" a 20 × 20 × 20 cm box (8,000 cm³) on volume
— but the item is 100 cm long and the box is only 20 cm on its longest
side. The per-product dimension check is what stops that. This case is
covered by a test (`test_volume_only_would_wrongly_accept`).

### Scope note (honest limitation)

The dimension check is per product, not a full 3D bin-packing solver:
it does not try to arrange several items side by side inside one box
beyond the total-volume check. That matches the assignment spec, which
asks for dimension + weight + volume rules, not a packing optimiser.

## Units

Dimensions in centimetres, weight in kilograms, cost in INR. All
measurements and money use `Decimal`, not floats.

## How to run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The API is then at `http://127.0.0.1:8000/api/`. The Django admin is
at `/admin/` (create a superuser with `python manage.py createsuperuser`).

## API endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET, POST | `/api/products/` | List / create products |
| GET, PUT, PATCH, DELETE | `/api/products/{id}/` | Product detail |
| GET, POST | `/api/boxes/` | List / create boxes |
| GET, PUT, PATCH, DELETE | `/api/boxes/{id}/` | Box detail |
| GET, POST | `/api/orders/` | List / create orders (with items) |
| GET, DELETE | `/api/orders/{id}/` | Order detail |
| POST | `/api/orders/{id}/recommend/` | Recommend a box for the order |

### Example: create a product

```bash
curl -X POST http://127.0.0.1:8000/api/products/ \
  -H 'Content-Type: application/json' \
  -d '{"name": "Bluetooth Speaker", "length": 20, "width": 15,
       "height": 10, "weight": 2}'
```

### Example: create boxes

```bash
curl -X POST http://127.0.0.1:8000/api/boxes/ \
  -H 'Content-Type: application/json' \
  -d '{"name": "Small", "internal_length": 25, "internal_width": 20,
       "internal_height": 15, "max_weight": 5, "cost": 49}'
curl -X POST http://127.0.0.1:8000/api/boxes/ \
  -H 'Content-Type: application/json' \
  -d '{"name": "Tiny", "internal_length": 10, "internal_width": 10,
       "internal_height": 10, "max_weight": 5, "cost": 29}'
```

### Example: create an order and get a recommendation

```bash
curl -X POST http://127.0.0.1:8000/api/orders/ \
  -H 'Content-Type: application/json' \
  -d '{"items": [{"product_id": 1, "quantity": 1}]}'

curl -X POST http://127.0.0.1:8000/api/orders/1/recommend/
```

Response (the "Small" box wins: it fits, and it is cheaper than any
other fitting box; "Tiny" is rejected because the speaker is 20 cm
long and Tiny is only 10 cm on a side):

```json
{
  "recommended_box": {
    "id": 1, "name": "Small",
    "internal_length": "25.00", "internal_width": "20.00",
    "internal_height": "15.00", "max_weight": "5.00", "cost": "49.00"
  },
  "reason": "'Small' is the cheapest box that fits: total weight 2.00 kg within 5.00 kg, every product fits inside 25.00 x 20.00 x 15.00 cm in some orientation, and total volume 3000.000000 cm^3 within 7500.000000 cm^3",
  "evaluated_boxes": [
    {"box": {"id": 1, "name": "Small", "internal_length": "25.00",
             "internal_width": "20.00", "internal_height": "15.00",
             "max_weight": "5.00", "cost": "49.00"},
     "fits": true, "reasons": []},
    {"box": {"id": 2, "name": "Tiny", "internal_length": "10.00",
             "internal_width": "10.00", "internal_height": "10.00",
             "max_weight": "5.00", "cost": "29.00"},
     "fits": false,
     "reasons": ["product 'Bluetooth Speaker' (20.00 x 15.00 x 10.00 cm) does not fit inside box 'Tiny' (10.00 x 10.00 x 10.00 cm) in any orientation"]}
  ]
}
```

Response when no box fits:

```json
{
  "recommended_box": null,
  "reason": "no suitable box: no box satisfies the weight, dimension and volume rules for this order",
  "evaluated_boxes": [{"box": {...}, "fits": false, "reasons": ["..."]}]
}
```

## How to run tests

```bash
python manage.py test shipping -v 2
```

12 tests, all passing at submission time — see `TEST_OUTPUT.md` for the
verbatim run and `TEST_CASES.md` for the cases in plain language.

## Project layout

```
boxselect/            Django project (settings, root urls)
shipping/             The app
  models.py           Product, Box, Order, OrderItem
  services.py         The recommendation algorithm (fit rules)
  serializers.py      DRF serializers, including nested order creation
  views.py            ViewSets + POST /orders/{id}/recommend/
  urls.py             Router: products, boxes, orders
  tests.py            12 tests (service + API level)
.github/workflows/ci.yml   Runs check + tests on push/PR
```

## Other documents

- `AI_USAGE.md` — truthful record of AI-tool use in this build.
- `CHAT_TRANSCRIPT.md` — log of the actual build session (not a
  fabricated human conversation).
- `TEST_CASES.md` — test cases in plain language.
- `TEST_OUTPUT.md` — verbatim test-run output.
- `LEARNINGS.md` — what building this demonstrated.
