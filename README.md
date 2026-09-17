# WatchStore — Django E-commerce (Watch shop)

Guest-checkout watch shop with admin/manager dashboard, live popup + Telegram/WhatsApp
notifications, and IP-based abuse detection on order cancellations.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # fill in DB creds + secret key

# Create the database first (in psql):
#   CREATE DATABASE watchstore;
#   CREATE USER watchstore_user WITH PASSWORD 'changeme';
#   GRANT ALL PRIVILEGES ON DATABASE watchstore TO watchstore_user;

python manage.py migrate
python manage.py createsuperuser   # make this user's role "admin" — see note below
python manage.py runserver
```

After creating the superuser, open `/django-admin/`, edit that user, and set
**role = admin** (the createsuperuser command doesn't ask for our custom `role`
field). Managers: create additional users the same way with **role = manager**.

- Storefront: http://localhost:8000/
- Staff login: http://localhost:8000/accounts/login/
- Dashboard: http://localhost:8000/dashboard/
- Full Django admin (products, raw DB access): http://localhost:8000/django-admin/

## How the key features are wired

**Guest checkout, order tracking**
Cart lives in the session (`orders/cart.py`) — no login needed to browse or add
to cart. Checkout creates an `Order` keyed by `phone` + a random `order_number`.
Customers look their order up with **both** phone and order number
(`orders/forms.py::OrderLookupForm`) — phone alone would let anyone browse
other customers' orders/addresses by guessing numbers.

**IP tracking + "same IP re-orders after cancelling" alert**
`tracking/middleware.py` attaches `request.visitor_ip` to every request.
`Order.ip_address` is stamped at checkout. `orders/services.py::check_repeat_ip_after_cancel`
runs right after a new order is saved: if that IP has any prior *cancelled* order,
it fires `notifications.services.notify_repeat_ip_after_cancel`.

**Instant-ish popups + Telegram/WhatsApp**
`notifications/models.py::NotificationEvent` is a simple event log. Every
meaningful action (product viewed, new order, repeat-IP alert) writes a row via
`notifications/services.py`, which also fans out to Telegram/WhatsApp if enabled.
The dashboard (`templates/base/dashboard_base.html`) polls
`GET /api/notifications/poll/?since=<id>` every 5s and shows a toast — that's
the "simple polling" option you picked over WebSockets. Bump
`NOTIFICATION_POLL_INTERVAL_MS` in settings if you want it faster/slower.

**Telegram/WhatsApp API keys in the admin panel**
`Dashboard > Notification API Settings` (admin role only) edits the singleton
`NotificationSettings` row — bot token, chat ID, WhatsApp API URL/token/number,
and per-event toggles. No redeploy needed to change them.

## Known gaps to close before going to production

1. **API calls are synchronous.** `notifications/senders.py` calls Telegram/WhatsApp
   inline during the request. Fine for now; move to Celery/RQ if it starts
   slowing down checkout or product-view requests.
2. **IP spoofing.** `tracking/middleware.py` trusts `X-Forwarded-For` as-is.
   That's fine behind your own nginx/Cloudflare (set it there), but don't expose
   Django directly to the internet without a trusted reverse proxy in front.
3. **Order cancellation is unauthenticated.** Anyone with the phone + order number
   can cancel. Consider adding a short confirmation code (SMS) before enabling
   this for real money.
4. **Product-view notifications will spam fast** on any real traffic — consider
   rate-limiting per product/IP (e.g. only notify once per product per 10 minutes)
   before launch.
5. `NotificationSettings.load()` reads DB settings but Telegram/WhatsApp tokens
   are stored in plaintext in Postgres — fine for a small shop, but encrypt at
   rest (e.g. `django-fernet-fields`) if this matters to you.
