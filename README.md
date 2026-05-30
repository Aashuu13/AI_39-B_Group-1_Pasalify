# Pasalify — Sprint 2: View Product (US 2.2)

**Team Member Feature:** View Product  
**User Story:** As a user, I want to view product details so that I can see the information I need before deciding.

## Acceptance Criteria
1. Click on the desired product
2. Show the product information and details
3. Display the availability status of the product
4. Load all relevant product data
5. Provide a back navigation system to return to the previous page

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up your database credentials
cp .env.example .env
# Edit .env → set MYSQL_PASSWORD (and MYSQL_DB if needed)

# 3. Initialize database (creates tables + demo product)
python setup_db.py

# 4. Run the app
python run.py
# → http://127.0.0.1:5000
```

The app opens on the **Products listing** page. Click any product to reach the **View Product** detail page.

## Demo Accounts

| Role     | Email                      | Password      |
|----------|---------------------------|---------------|
| Customer | customer@pasalify.com     | customer123   |
| Seller   | seller@pasalify.com       | seller123     |

## Feature Flow (US 2.2)

1. Go to `http://127.0.0.1:5000` → lands on **Products** listing
2. Click on any product card
3. **Product Detail page** opens showing:
   - Product images with thumbnail switcher
   - Name, price, discount badge
   - **Availability/stock status** (In Stock / Low Stock / Out of Stock)
   - Full description and product details
   - Customer reviews and rating
   - Related products in the same category
4. Click **Back to Products** breadcrumb or button to return

## Files for This Feature

| File | Purpose |
|------|---------|
| `app/controllers/customer_controller.py` | `product_detail()` method — core logic |
| `app/routes/customer.py` | URL rule for `/customer/product/<pid>` |
| `app/templates/customer/product_detail.html` | Product detail page template |
| `app/models/product_model.py` | `get_with_images()`, `search()` |
| `app/models/review_model.py` | `find_by_product()` |
