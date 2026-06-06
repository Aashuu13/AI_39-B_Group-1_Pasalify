# My Sprint Features — Pasalify Project

## Developer Assignment

| Sprint | User Story | Feature |
|--------|-----------|---------|
| Sprint 1 | US 1.3 | Reset Password (Forgot Password) |
| Sprint 2 | US 2.2 | View Product (Product Detail Page) |
| Sprint 3 | US 1.4 | Change Password |
| Sprint 3 | US 2.6 | Seller Chat (Customer ↔ Seller messaging) |

---

## My Feature Files (Primary Ownership)

### US 1.3 — Reset Password (Sprint 1)
- **Controller logic:** `app/controllers/auth_controller.py` → `forgot_password()` method
- **Route:** `app/routes/auth.py` → `/auth/forgot-password`
- **Template:** `app/templates/auth/forgot_password.html`

### US 2.2 — View Product (Sprint 2)
- **Controller logic:** `app/controllers/customer_controller.py` → `product_detail()` method
- **Route:** `app/routes/customer.py` → `/customer/product/<int:pid>`
- **Template:** `app/templates/customer/product_detail.html`
- **Model query used:** `ProductModel.get_with_images()` in `app/models/product_model.py`

### US 1.4 — Change Password (Sprint 3)
- **Controller logic:** `app/controllers/auth_controller.py` → `change_password()` method
- **Route:** `app/routes/auth.py` → `/auth/change-password`
- **Template:** `app/templates/auth/change_password.html`
- **Model method:** `UserModel.change_password()` in `app/models/user_model.py`
- **Security:** Verifies old password via `UserModel.authenticate()` before updating

### US 2.6 — Seller Chat (Sprint 3)
- **Customer side controller:** `app/controllers/customer_controller.py`
  - `start_chat()` — creates or resumes a chat session
  - `my_chats()` — lists all chats for the customer
  - `chat_detail()` — view messages + send message (POST)
- **Seller side controller:** `app/controllers/seller_controller.py`
  - `chats()` — lists all incoming chats for the seller
  - `chat_detail()` — view + reply to customer
  - `send_message()` — POST alias for sending
- **Routes (customer):** `app/routes/customer.py` → `/customer/chats`, `/customer/chats/start/<seller_id>`, `/customer/chats/<chat_id>`
- **Routes (seller):** `app/routes/seller.py` → `/seller/chats`, `/seller/chats/<chat_id>`
- **Templates:**
  - `app/templates/customer/chats.html` — customer chat list
  - `app/templates/customer/chat_detail.html` — customer chat window
  - `app/templates/seller/chats.html` — seller chat list
  - `app/templates/seller/chat_detail.html` — seller chat window
- **DB tables used:** `chats`, `chat_messages` (defined in `schema.sql`)

---

## Supporting Files (Needed to Run, Owned by Team)

| File | Purpose |
|------|---------|
| `app/app.py` | Flask app factory, blueprint registration |
| `app/config.py` | DB and app configuration |
| `app/db.py` | Raw pymysql connection layer |
| `app/__init__.py` | Package entry |
| `run.py` | Entry point — `python run.py` to start server |
| `schema.sql` | Database schema + seed data |
| `setup_db.py` | One-time DB initialiser |
| `requirements.txt` | pip dependencies |
| `app/models/basemodel.py` | Abstract base CRUD model |
| `app/models/database.py` | DB wrapper used by all models |
| `app/models/user_model.py` | User CRUD + auth helpers |
| `app/models/product_model.py` | Product search + detail queries |
| `app/models/*.py` | Other models (store, order, cart, etc.) |
| `app/controllers/base_controller.py` | Shared controller helpers |
| `app/utils/auth.py` | `login_required`, `role_required`, `hash_password` |
| `app/templates/base.html` | Master layout (all pages extend this) |
| `app/static/css/pasalify.css` | Global stylesheet |
| `app/static/js/pasalify.js` | Global JS |

---

## Setup & Run

```bash
# 1. Create & activate venv
python -m venv venv
# Windows:  venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment (copy .env.example → .env and fill in DB credentials)
cp .env.example .env

# 4. Initialise database
python setup_db.py

# 5. Run the app
python run.py
# Visit: http://127.0.0.1:5000
```

---

## Key Credentials (Demo Accounts)
| Role | Email | Password |
|------|-------|----------|
| Customer | customer@pasalify.com | customer123 |
| Seller | seller@pasalify.com | seller123 |
| Admin | admin@pasalify.com | (set in DB) |

