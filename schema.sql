-- Pasalify schema additions for Wishlist (US 2.4) and Product Reviews (US 2.5)
-- Run this after your existing tables are created.

-- ── Wishlists table ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS wishlists (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    product_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_wish (user_id, product_id),
    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- ── Reviews table ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reviews (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    user_id    INT NOT NULL,
    order_id   INT,
    rating     TINYINT NOT NULL,
    title      VARCHAR(150),
    body       TEXT,
    is_approved TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_review (product_id, user_id),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE
);

-- Add avg_rating and review_count columns to products if not already present
ALTER TABLE products
    ADD COLUMN IF NOT EXISTS avg_rating   DECIMAL(3,2) DEFAULT 0.00,
    ADD COLUMN IF NOT EXISTS review_count INT          DEFAULT 0;
