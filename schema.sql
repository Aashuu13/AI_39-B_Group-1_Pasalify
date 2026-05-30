-- Sprint 2: US 2.2 View Product
-- Tables required for the View Product feature

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password_hash VARCHAR(512) NOT NULL,
    role ENUM('customer','seller','admin') DEFAULT 'customer',
    is_active TINYINT(1) DEFAULT 1,
    failed_logins TINYINT DEFAULT 0,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    slug VARCHAR(150) UNIQUE NOT NULL,
    description TEXT,
    logo VARCHAR(255),
    banner VARCHAR(255),
    theme_color VARCHAR(20) DEFAULT '#6C3FC8',
    is_approved TINYINT(1) DEFAULT 0,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ALTER TABLE stores ADD COLUMN primary_color VARCHAR(20) DEFAULT '#6C3FC8'; -- Run manually if needed
-- ALTER TABLE stores ADD COLUMN banner_text VARCHAR(255); -- Run manually if needed

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    parent_id INT DEFAULT NULL,
    icon VARCHAR(50) DEFAULT 'tag',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT NOT NULL,
    category_id INT,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(220) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    compare_price DECIMAL(10,2),
    sku VARCHAR(100),
    stock_qty INT DEFAULT 0,
    low_stock_threshold INT DEFAULT 5,
    is_active TINYINT(1) DEFAULT 1,
    is_approved TINYINT(1) DEFAULT 0,
    avg_rating DECIMAL(3,2) DEFAULT 0.00,
    review_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS product_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    image_path VARCHAR(255) NOT NULL,
    is_primary TINYINT(1) DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    user_id INT NOT NULL,
    order_id INT,
    rating TINYINT NOT NULL,
    title VARCHAR(150),
    body TEXT,
    is_approved TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_review (product_id, user_id),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100),
    entity_type VARCHAR(50),
    entity_id INT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('order','payment','promo','system','review') DEFAULT 'system',
    is_read TINYINT(1) DEFAULT 0,
    link VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Demo data
INSERT IGNORE INTO categories (name, slug, icon) VALUES
('Electronics', 'electronics', 'cpu'),
('Fashion',     'fashion',     'bag'),
('Home & Garden','home-garden','house'),
('Books',       'books',       'book'),
('Sports',      'sports',      'trophy');

-- Demo customer (password: customer123)
INSERT IGNORE INTO users (name,email,phone,password_hash,role,is_active) VALUES
('Demo Customer','customer@pasalify.com','9811111111',
 'aabbccddaabbccddaabbccddaabbccddaabbccddaabbccddaabbccddaabbccdd:4fb3cbbc86b04c8c3cdd5a2f566f10a7e041ccf0105ea90813ee519c68def446','customer',1);

-- Demo seller (password: seller123)
INSERT IGNORE INTO users (name,email,phone,password_hash,role,is_active) VALUES
('Demo Seller','seller@pasalify.com','9822222222',
 '1122334455667788112233445566778811223344556677881122334455667788:2a5c34aa29be7f7a5b73b9a76556485e139a4776b1d763ab524f72143f0cd87b','seller',1);

-- Demo store
INSERT IGNORE INTO stores (user_id,name,slug,description,is_approved,is_active)
SELECT id,'Demo Store','demo-store','A demo store for testing.',1,1
FROM users WHERE email='seller@pasalify.com' LIMIT 1;

-- Demo product (visible on product listing and detail page)
INSERT IGNORE INTO products (store_id,category_id,name,slug,description,price,compare_price,sku,stock_qty,is_active,is_approved,avg_rating,review_count)
SELECT
  s.id,
  c.id,
  'Pasalify Demo Product',
  'pasalify-demo-product',
  'This is a demo product to showcase the View Product feature. It displays all product information including name, price, stock status, description, and reviews.',
  1499.00,
  1999.00,
  'DEMO-001',
  25,
  1,
  1,
  4.50,
  2
FROM stores s, categories c
WHERE s.slug='demo-store' AND c.slug='electronics'
LIMIT 1;
