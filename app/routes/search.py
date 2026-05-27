# =============================================================
#  Pasalify — Sprint 2
#  User Story : US 2.1 – Search Products
#  Feature ID : F2 / Story Point: 2
#  Developer  : Yubraj KC
#  Tasks      : Backend Development · Database · Validation
#
#  Acceptance Criteria (from Sprint 2 Backlog):
#   1. Open the search bar on the platform.
#   2. Enter a keyword for the desired product.
#   3. Apply filters to narrow down the results.
#   4. Show the matching results to the user.
#   5. Display a no result message if nothing is found.
# =============================================================

from flask import Blueprint, request, render_template, jsonify
import pymysql.cursors
from db import get_db          # your existing helper — returns a pymysql connection

search_bp = Blueprint("search", __name__)


# ──────────────────────────────────────────────────────────────
#  INTERNAL HELPER  (Database Task)
#  Builds a safe, parameterised query from whatever filters the
#  user passed in.  Nothing is interpolated directly into SQL.
# ──────────────────────────────────────────────────────────────

def _execute_search(keyword="", category_id=None,
                    min_price=None, max_price=None,
                    sort="relevance", page=1, per_page=16):
    """
    Run the product search against the database.

    Returns:
        products    – list of dicts (one per product)
        total       – total matching rows (for pagination)
        total_pages – number of pages
    """

    # Base SELECT — joins products → stores → categories
    # and grabs the primary image in a correlated sub-select
    sql = """
        SELECT
            p.id,
            p.name,
            p.slug,
            p.price,
            p.compare_price,
            p.avg_rating,
            p.review_count,
            p.stock_qty,
            s.name  AS store_name,
            s.slug  AS store_slug,
            c.name  AS category_name,
            (
                SELECT pi.image_path
                FROM   product_images pi
                WHERE  pi.product_id = p.id
                  AND  pi.is_primary  = 1
                LIMIT  1
            ) AS primary_image
        FROM  products   p
        JOIN  stores     s ON s.id = p.store_id
        LEFT JOIN categories c ON c.id = p.category_id
        WHERE p.is_active   = 1
          AND p.is_approved = 1
          AND s.is_active   = 1
          AND s.is_approved = 1
    """

    count_sql = """
        SELECT COUNT(*) AS total
        FROM   products p
        JOIN   stores   s ON s.id = p.store_id
        WHERE  p.is_active   = 1
          AND  p.is_approved = 1
          AND  s.is_active   = 1
          AND  s.is_approved = 1
    """

    conditions = []
    params     = []

    # AC-2: keyword entered by the user → search name, description, SKU
    if keyword:
        conditions.append(
            "(p.name LIKE %s OR p.description LIKE %s OR p.sku LIKE %s)"
        )
        like = f"%{keyword}%"
        params += [like, like, like]

    # AC-3: category filter
    if category_id:
        conditions.append("p.category_id = %s")
        params.append(category_id)

    # AC-3: price range filter
    if min_price is not None:
        conditions.append("p.price >= %s")
        params.append(min_price)

    if max_price is not None:
        conditions.append("p.price <= %s")
        params.append(max_price)

    # Append conditions to both queries
    if conditions:
        clause = " AND " + " AND ".join(conditions)
        sql       += clause
        count_sql += clause

    # Sorting
    order_map = {
        "relevance":  "p.review_count DESC, p.avg_rating DESC",
        "price_asc":  "p.price ASC",
        "price_desc": "p.price DESC",
        "newest":     "p.created_at DESC",
        "rating":     "p.avg_rating DESC",
        "popular":    "p.review_count DESC",
    }
    sql += " ORDER BY " + order_map.get(sort, order_map["relevance"])

    # Pagination
    offset  = (page - 1) * per_page
    sql    += f" LIMIT {per_page} OFFSET {offset}"

    # --- run queries ---
    db = get_db()
    with db.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute(count_sql, params)
        total = cur.fetchone()["total"]

        cur.execute(sql, params)
        products = cur.fetchall()

    total_pages = max(1, (total + per_page - 1) // per_page)
    return products, total, total_pages


# ──────────────────────────────────────────────────────────────
#  ROUTE 1 — Full results page  (AC 1 · 3 · 4 · 5)
#  GET /search
# ──────────────────────────────────────────────────────────────

@search_bp.route("/search")
def search():
    """
    Renders the search results page.

    AC 1 – The search bar is visible on the page.
    AC 3 – Category and price filters are shown in the sidebar.
    AC 4 – Matching products are displayed in a grid.
    AC 5 – An empty-state message is shown when there are no results.
    """

    # --- read query params ---
    keyword     = request.args.get("q", "").strip()
    category_id = request.args.get("category", type=int)
    min_price   = request.args.get("min_price",  type=float)
    max_price   = request.args.get("max_price",  type=float)
    sort        = request.args.get("sort",  "relevance")
    page        = request.args.get("page",  1, type=int)

    # --- Validation Task: sanitise inputs ---
    # Prevent absurd page numbers
    page = max(1, page)
    # Prevent inverted price range
    if min_price and max_price and min_price > max_price:
        min_price, max_price = max_price, min_price

    products, total, total_pages = _execute_search(
        keyword, category_id, min_price, max_price, sort, page
    )

    # Load categories for the filter sidebar
    db = get_db()
    with db.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute(
            "SELECT id, name, slug, icon FROM categories "
            "WHERE parent_id IS NULL ORDER BY name"
        )
        categories = cur.fetchall()

    return render_template(
        "search/results.html",
        keyword          = keyword,
        products         = products,
        total            = total,
        total_pages      = total_pages,
        current_page     = page,
        categories       = categories,
        selected_category= category_id,
        min_price        = min_price,
        max_price        = max_price,
        sort             = sort,
    )


# ──────────────────────────────────────────────────────────────
#  ROUTE 2 — JSON / AJAX results  (AC 4)
#  GET /api/search
# ──────────────────────────────────────────────────────────────

@search_bp.route("/api/search")
def api_search():
    """
    Returns product results as JSON.
    Used by the frontend for live filtering without a full page reload.
    Same query params as /search.
    """

    keyword     = request.args.get("q", "").strip()
    category_id = request.args.get("category", type=int)
    min_price   = request.args.get("min_price",  type=float)
    max_price   = request.args.get("max_price",  type=float)
    sort        = request.args.get("sort",  "relevance")
    page        = request.args.get("page",  1, type=int)

    # Return empty payload when nothing is searched yet
    if not keyword and not category_id:
        return jsonify({"products": [], "total": 0, "total_pages": 0})

    products, total, total_pages = _execute_search(
        keyword, category_id, min_price, max_price, sort, page
    )

    # Serialise — Decimal and datetime are not JSON-safe by default
    def to_dict(p):
        return {
            "id":            p["id"],
            "name":          p["name"],
            "slug":          p["slug"],
            "price":         float(p["price"]),
            "compare_price": float(p["compare_price"]) if p["compare_price"] else None,
            "avg_rating":    float(p["avg_rating"]),
            "review_count":  p["review_count"],
            "stock_qty":     p["stock_qty"],
            "store_name":    p["store_name"],
            "store_slug":    p["store_slug"],
            "category_name": p["category_name"],
            "primary_image": p["primary_image"],
        }

    return jsonify({
        "products":    [to_dict(p) for p in products],
        "total":       total,
        "total_pages": total_pages,
        "page":        page,
        "keyword":     keyword,
    })


# ──────────────────────────────────────────────────────────────
#  ROUTE 3 — Autocomplete suggestions  (AC 2)
#  GET /api/search/suggest?q=<keyword>
# ──────────────────────────────────────────────────────────────

@search_bp.route("/api/search/suggest")
def api_suggest():
    """
    AC-2: As the user types a keyword, up to 8 matching product
    names appear in a dropdown so they can find products faster.
    Requires at least 2 characters to fire.
    """

    keyword = request.args.get("q", "").strip()

    # Validation Task: ignore very short queries
    if len(keyword) < 2:
        return jsonify({"suggestions": []})

    db  = get_db()
    sql = """
        SELECT DISTINCT
            p.name,
            p.slug,
            (
                SELECT pi.image_path
                FROM   product_images pi
                WHERE  pi.product_id = p.id AND pi.is_primary = 1
                LIMIT  1
            ) AS thumb
        FROM  products p
        WHERE p.is_active   = 1
          AND p.is_approved = 1
          AND p.name LIKE %s
        ORDER BY p.review_count DESC
        LIMIT 8
    """
    with db.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute(sql, (f"%{keyword}%",))
        rows = cur.fetchall()

    return jsonify({
        "suggestions": [
            {"name": r["name"], "slug": r["slug"], "thumb": r["thumb"]}
            for r in rows
        ]
    })
