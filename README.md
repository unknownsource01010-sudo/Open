# PromoProwler Core v8

Open-style PromoProwler UI with fixed free-text Deep Search, saved-item suggestions, broad retailer/direct/coupon search routes, local live-source worker, delivered-cost ranking, saved shopping list/import/export, verified offer capture, and user-confirmed purchase queue.

## Run full worker mode
```bash
./start.sh
```
Then open http://127.0.0.1:8787

`index.html` also works as a static front end for Deep Search/list/offer/queue functions. AUTO HUNT requires the local worker.

No prices, promo success, shipping, tax, or checkout success are fabricated. Unknown/blocked sources stay unknown.
