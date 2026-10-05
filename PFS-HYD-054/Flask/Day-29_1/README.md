# ShopZone Flask E-commerce

## Database behavior

- New customer registration inserts a row into `users` through `database/authDB.py`.
- Successful login stores `id`, `role`, `username`, and `email` in the Flask session.
- Protected routes use the `login_required` decorator with user/admin role checks.
- Categories remain text values in `products.category`; there is no category table.
- Placing an order creates an `orders` row, `order_details` rows, a `transactions` row, and a legacy-compatible `payments` row in one database transaction.
- Product stock is reserved/decremented when the order is created.
- COD orders become `processing` with payment status `pending`.
- Razorpay orders remain `pending` until the Razorpay signature is verified.
- Successful Razorpay verification updates `orders` and `transactions`/`payments` to `paid` and clears the cart.
- Failed/cancelled Razorpay payments mark the order cancelled, mark the transaction/payment failed, and return reserved stock.
- Admin cancellation also returns reserved stock and updates pending transaction/payment records.

## Razorpay test mode

Set these values in `.env`:

```env
FLASK_SECRET_KEY=change-this-secret
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-password
DB_NAME=ecommerce
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=xxxxx
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python app.py
```
