from flask import render_template, request
from app import db


def products():
    q        = request.args.get('q', '').strip()
    cat_slug = request.args.get('cat', '').strip()
    min_p    = request.args.get('min_price', '').strip()
    max_p    = request.args.get('max_price', '').strip()
    sort     = request.args.get('sort', 'newest')
    rating   = request.args.get('rating', '').strip()

    sql = """
        SELECT p.*, pi.image_path,
               s.name AS store_name, s.slug AS store_slug,
               c.name AS cat_name,  c.slug AS cat_slug_col
        FROM   products p
        LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_primary = 1
        JOIN   stores     s ON s.id = p.store_id
        LEFT JOIN categories c ON c.id = p.category_id
        WHERE  p.is_active = 1 AND p.is_approved = 1
    """
    args = []

    if q:
        sql += " AND (p.name LIKE %s OR p.description LIKE %s)"
        args += [f'%{q}%', f'%{q}%']
    if cat_slug:
        sql += " AND c.slug = %s"
        args.append(cat_slug)
    if min_p:
        sql += " AND p.price >= %s"
        args.append(min_p)
    if max_p:
        sql += " AND p.price <= %s"
        args.append(max_p)
    if rating:
        sql += " AND p.avg_rating >= %s"
        args.append(rating)

    order_map = {
        'newest':     'p.created_at DESC',
        'price_asc':  'p.price ASC',
        'price_desc': 'p.price DESC',
        'rating':     'p.avg_rating DESC',
    }
   