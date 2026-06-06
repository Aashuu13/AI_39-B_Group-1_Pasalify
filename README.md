# Pasalify - Sprint 3

Flask MVC e-commerce platform. Sprint 3 completes all features through v3.0.

## Sprint Coverage

### Sprint 1 · Core Foundation (Completed)
- US 1.1 Create User Account · US 1.2 Login System · US 1.3 Reset Password · US 1.6 Platform Security

### Sprint 2 · Core Shopping (Completed)
- US 2.1 Search Products · US 2.2 View Product · US 2.3 Manage Cart
- US 3.1 Place Order · US 3.3 Make Payment
- US 4.1 Register Store · US 4.3 Manage Products · US 5.1 Admin Dashboard

### Sprint 3 · Seller & Orders (This Release)
- **US 1.4** Change Password · **US 1.5** Edit Profile (avatar, address, city)
- **US 2.4** Wishlist (fixed table name, add/remove)
- **US 2.5** Product Reviews (submit, display, avg rating update)
- **US 2.6** Seller Chat (customer ↔ seller messaging, unread badges)
- **US 3.2** Track Orders (status timeline, cancel if 'placed')
- **US 3.5** Apply Promo Code (AJAX validation at checkout)
- **US 4.5** Manage Inventory (filter by low/out, bulk update)
- **US 4.6** Manage Orders (status filter, update with customer notification)
- **US 5.2** Content Control (review moderation, flag resolution)
- **US 5.3** Track Transactions (paginated view, CSV export, commission report)

## Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your MySQL credentials

# 4. Create database and tables
python setup_db.py

# 5. Run
python run.py
```

## Demo Accounts

| Role     | Email                    | Password    |
|----------|--------------------------|-------------|
| Admin    | admin@pasalify.com       | admin123    |
| Seller   | seller@pasalify.com      | seller123   |
| Customer | customer@pasalify.com    | customer123 |

## Project Structure

```
pasalify_sprint3/
├── app/
│   ├── controllers/        # MVC Controllers (OOP: Inheritance, Encapsulation)
│   │   ├── base_controller.py      # Abstract base with shared helpers
│   │   ├── auth_controller.py      # Sprint 1: Register, Login, Password
│   │   ├── customer_controller.py  # Sprint 1-3: Shopping + Chat + Orders
│   │   ├── seller_controller.py    # Sprint 1-3: Store + Inventory + Orders
│   │   └── admin_controller.py     # Sprint 1-3: Dashboard + Content + Finance
│   ├── models/             # Database models (OOP: Abstraction)
│   ├── routes/             # Flask blueprints (URL → controller mapping)
│   ├── templates/          # Jinja2 HTML templates
│   │   ├── admin/          # Admin panel templates
│   │   ├── auth/           # Login, register, password templates
│   │   ├── customer/       # Customer-facing templates
│   │   └── seller/         # Seller dashboard templates
│   ├── static/             # CSS, JS, uploaded images
│   └── utils/              # Auth helpers (login_required, role_required)
├── schema.sql              # Full DB schema (all 3 sprints)
├── setup_db.py             # DB initialisation script
├── requirements.txt
└── run.py
```

## OOP Concepts Used

- **Inheritance**: All controllers inherit from `BaseController` (shared `_q`, `_run`, `_ok`, `_err`, `_notify`, `_save_file`)
- **Encapsulation**: Validation, password hashing, file upload logic all hidden inside models/controllers
- **Abstraction**: `BaseModel` provides generic CRUD; controllers call high-level methods, not raw SQL
- **Polymorphism**: `role_required()` decorator routes the same login flow differently per role
