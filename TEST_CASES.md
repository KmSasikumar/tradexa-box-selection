# Test cases (plain language)

Dimensions in cm, weight in kg, cost in INR. "Fits" always means all
three fit rules from the README: weight, per-product dimensions with
rotation allowed, and total volume.

## Service-level tests (`shipping.services.recommend_box`)

1. **Fits exactly** — Product 10 × 20 × 30 cm, 5 kg; box 10 × 20 × 30 cm,
   max 5 kg, cost 100. Expected: the box is recommended. Boundaries use
   "less than or equal", not "strictly less than".
2. **Too heavy rejected** — Product 10 × 10 × 10 cm, 12 kg; box
   50 × 50 × 50 cm, max 10 kg. Dimensions and volume fit, weight does
   not. Expected: no box, with a weight reason.
3. **Too large in one dimension rejected** — Product 10 × 10 × 55 cm,
   1 kg; box 50 × 50 × 50 cm, max 100 kg. Weight and volume fit, height
   does not. Expected: no box, with a dimension reason.
4. **Rotation allowed** — Product 40 × 10 × 5 cm, 1 kg; box stored as
   12 × 45 × 8 cm, max 10 kg. A direct side-by-side comparison
   (40 > 12) would reject it; sorted sides (5, 10, 40) vs (8, 12, 45)
   fit. Expected: the box is recommended.
5. **Volume-only trap rejected** — Product 100 × 2 × 2 cm (400 cm³),
   1 kg; box 20 × 20 × 20 cm (8,000 cm³), max 100 kg. Volume alone
   would accept it; the dimension check rejects it because 100 > 20.
   Expected: no box.
6. **Cheapest among fitting boxes chosen** — One product, three fitting
   boxes costing 200, 80 and 150 (created in that order). Expected: the
   80 box is recommended.
7. **No box case returns None** — Product 10 × 10 × 10 cm, 500 kg;
   boxes with max 10 kg and 20 kg. Expected: None, with a reason for
   every evaluated box — never a forced fit.
8. **Empty order handled** — An order with no items, with boxes
   available. Expected: None, with a "no items" reason.
9. **Quantity scales weight and volume** — 3 × a 4 kg, 1,000 cm³ product
   = 12 kg / 3,000 cm³. A 10 kg box is rejected; a 15 kg box fits.
   Expected: the 15 kg box is recommended.

## API-level tests (real HTTP calls through DRF's test client)

10. **CRUD + recommend end-to-end** — Create a product and two boxes
    through the API, create an order with items, POST
    `/api/orders/{id}/recommend/`. Expected: HTTP 200, the cheaper
    fitting box is returned, and the reason mentions "cheapest".
11. **Recommend endpoint, no box** — An order heavier than the only box.
    Expected: HTTP 200 (no box is a valid answer, not an error),
    `recommended_box` null, a non-empty reason, and the evaluated box
    marked as not fitting.
12. **Recommend endpoint, empty order** — An order created with an empty
    items list. Expected: HTTP 200, `recommended_box` null, and a reason
    mentioning "no items".

## Result

12 tests, 12 passing. See `TEST_OUTPUT.md` for the verbatim run.
