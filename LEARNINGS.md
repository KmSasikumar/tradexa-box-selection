# Learnings

Plain first-person notes from building this assignment — what the work
itself demonstrated. Nothing here claims experience I do not have; each
point traces to something actually done in this build.

## 1. A fit rule is only as good as its worst accepted case

The spec's three rules look redundant until you test each one against a
case designed to break it. Volume alone accepts a 100 cm pole in a
20 cm box. Dimensions alone accept a box that collapses under the
weight. Weight + dimensions alone accept a box whose total volume is
too small for several items together. Writing one test per rule — each
with the other two rules satisfied — is what proved that all three are
necessary, not just plausible. I will carry that habit forward: for any
multi-rule decision, test each rule in isolation with the others held
passing.

## 2. Sorted-dimension comparison is the honest way to allow rotation

Comparing sides directly (length-to-length, width-to-width) rejects
items that fit after a turn. Sorting both sets of sides smallest-to-
largest and comparing pairwise is the correct test for a rectangular
item in a rectangular box, and it is easy to explain to a reviewer.
Its limit is also clear: it checks one item at a time, so it is not a
3D bin-packing solver. Stating that limit in the README matters more
than pretending the algorithm does more than it does.

## 3. Boundaries deserve their own test

The "fits exactly" test (product exactly equal to the box on every
side, weight exactly at the limit) exists because off-by-one-style
errors live at boundaries: `<` where the spec says `<=` would silently
reject valid orders. If a rule says "less than or equal", the test
suite should contain an exactly-equal case.

## 4. "No result" is a result, and it needs a reason

Returning `null` for "no suitable box" is easy; returning `null` with
an explanation is what makes the API usable. Every evaluated box
carries its failure reasons, and the endpoint returns HTTP 200 for the
no-box case, because "no box fits" is a valid answer to the question,
not a server error. The same applies to the empty order: it gets an
explicit reason instead of a crash or a meaningless default box.

## 5. Tests passing does not prove the API path works

The test suite passed on its first run, but the shell-based API smoke
test failed on `ALLOWED_HOSTS`: the test runner silently allows the
`testserver` host, while a real shell/APIClient session does not.
That one failure taught me to verify through more than one path — unit
tests plus a live smoke run — before calling something done.

## 6. DRF design choices that paid off

- Nested order creation (items inside the order payload) matches how a
  warehouse actually submits an order: one request, not one per line.
- A dedicated action (`POST /orders/{id}/recommend/`) keeps the
  recommendation separate from order creation, so recommending twice
  does not create duplicate orders and the reasoning can be re-fetched.
- `Decimal` fields for dimensions, weight and money avoid float
  rounding in exactly the places (cost comparison, weight limits) where
  a rounding error would change an answer.

## 7. Documentation is part of the deliverable, not an afterthought

The assignment explicitly asks for AI usage, transcript, test cases and
test output documents. Writing them forced checks that code alone did
not: the README example had to be corrected to match the real API
response, and the AI usage record had to distinguish what was accepted
from what was rejected. A reviewer reading only the code would never
see those decisions.
