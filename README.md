# Pasalify — Sprint 2

Nepal's multi-vendor marketplace — Flask MVC, Sprint 1 (auth) + Sprint 2 (shopping, seller, admin).

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy and fill in your credentials
cp .env.example .env
# Edit .env → set MYSQL_PASSWORD (and MYSQL_DB if needed)

# 3. Initialize database (creates tables + demo accounts)
python setup_db.py

# 4. Run
python run.py
# → http://127.0.0.1:5000
```

## Demo Login Accounts

| Role     | Email                      | Password      |
|----------|---------------------------|---------------|
| Admin    | admin@pasalify.com        | admin123      |
| Customer | customer@pasalify.com     | customer123   |
| Seller   | seller@pasalify.com       | seller123     |

## Login Dashboards

- **Admin** → `/admin/dashboard` — stats, sellers, products, users, finance, categories, promos, system logs
- **Seller** → `/seller/dashboard` — revenue, orders, products, inventory, reviews
- **Customer** → `/customer/` — browse, cart, checkout, orders, wishlist, profile

## Project Structure

```
pasalify_sprint2/
├── run.py                  ← entry point
├── setup_db.py             ← DB init script
├── schema.sql              ← full database schema
├── requirements.txt
├── .env.example
└── app/
    ├── app.py
    ├── config.py
    ├── db.py
    ├── controllers/        ← OOP controllers (auth, customer, seller, admin)
    ├── models/             ← OOP models (user, product, store, order, cart…)
    ├── routes/             ← Flask blueprints
    ├── templates/          ← Jinja2 HTML templates
    │   ├── base.html
    │   ├── auth/
    │   ├── admin/
    │   ├── seller/
    │   └── customer/
    ├── static/
    │   ├── css/pasalify.css
    │   └── js/pasalify.js
    └── utils/auth.py       ← password hashing, decorators
```

## Sprint Coverage

| Story | Feature | Status |
|-------|---------|--------|
| US 1.1 | Create User Account | ✅ Sprint 1 |
| US 1.2 | Login System | ✅ Sprint 1 |
| US 1.3 | Reset Password | ✅ Sprint 1 |
| US 1.6 | Platform Security | ✅ Sprint 1 |
| US 2.1 | Search Products | ✅ Sprint 2 |
| US 2.2 | View Product | ✅ Sprint 2 |
| US 2.3 | Manage Cart | ✅ Sprint 2 |
| US 3.1 | Place Order | ✅ Sprint 2 |
| US 3.3 | Make Payment | ✅ Sprint 2 |
| US 4.1 | Register Store | ✅ Sprint 2 |
| US 4.3 | Manage Products | ✅ Sprint 2 |
| US 5.1 | Admin Dashboard | ✅ Sprint 2 |
