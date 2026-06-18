CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password_hash VARCHAR(512) NOT NULL,
    role ENUM('customer','seller','admin') DEFAULT 'customer',
    avatar VARCHAR(255),
    address TEXT,
    city VARCHAR(80),
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
    theme_layout ENUM('grid','list','masonry') DEFAULT 'grid',
    is_approved TINYINT(1) DEFAULT 0,
    is_active TINYINT(1) DEFAULT 1,
    commission_rate DECIMAL(5,2) DEFAULT 10.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

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

CREATE TABLE IF NOT EXISTS wishlists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_wish (user_id, product_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT DEFAULT 1,
    UNIQUE KEY uq_cart (user_id, product_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS promo_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    discount_type ENUM('percent','fixed') DEFAULT 'percent',
    discount_value DECIMAL(10,2) NOT NULL,
    min_order DECIMAL(10,2) DEFAULT 0,
    max_uses INT,
    used_count INT DEFAULT 0,
    valid_from DATE,
    valid_until DATE,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    order_number VARCHAR(30) UNIQUE NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    phone VARCHAR(20),
    address TEXT NOT NULL,
    city VARCHAR(80),
    total_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    promo_code_id INT,
    payment_method ENUM('cod','esewa','khalti') DEFAULT 'cod',
    payment_status ENUM('pending','paid','failed','refunded') DEFAULT 'pending',
    status ENUM('placed','confirmed','processing','shipped','delivered','cancelled') DEFAULT 'placed',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (promo_code_id) REFERENCES promo_codes(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    store_id INT NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    quantity INT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    user_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    method ENUM('cod','esewa','khalti') NOT NULL,
    status ENUM('pending','success','failed','refunded') DEFAULT 'pending',
    transaction_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
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

CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('order','payment','promo','system','review') DEFAULT 'system',
    is_read TINYINT(1) DEFAULT 0,
    link VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS support_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    session_id VARCHAR(100),
    role ENUM('user','bot') DEFAULT 'user',
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    seller_id INT NOT NULL,
    product_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chat_id INT NOT NULL,
    sender_id INT NOT NULL,
    message TEXT NOT NULL,
    is_read TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(200) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS commissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_item_id INT NOT NULL,
    store_id INT NOT NULL,
    seller_amount DECIMAL(10,2) NOT NULL,
    platform_amount DECIMAL(10,2) NOT NULL,
    status ENUM('pending','paid') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_item_id) REFERENCES order_items(id) ON DELETE CASCADE,
    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE
);

INSERT IGNORE INTO categories (name, slug, icon) VALUES
('Electronics','electronics','cpu'),
('Fashion','fashion','shopping-bag'),
('Home & Garden','home-garden','home'),
('Sports','sports','activity'),
('Books','books','book-open'),
('Beauty','beauty','star'),
('Food & Grocery','food-grocery','package'),
('Toys & Kids','toys-kids','gift');

INSERT IGNORE INTO users (name,email,phone,password_hash,role,is_active) VALUES
('Pasalify Admin','admin@pasalify.com','9800000000',
 '3ac179c671a66c06af031954e0ed311f35e567477c6cd8b1bdabd09796d267d1:f913dd1eaabbb9cc573a44502cdf9ac90254b8d47a0db0a64082a823da3fa2f7','admin',1);

INSERT IGNORE INTO users (name,email,phone,password_hash,role,is_active) VALUES
('Demo Customer','customer@pasalify.com','9811111111',
 'aabbccddaabbccddaabbccddaabbccddaabbccddaabbccddaabbccddaabbccdd:4fb3cbbc86b04c8c3cdd5a2f566f10a7e041ccf0105ea90813ee519c68def446','customer',1);


INSERT IGNORE INTO users (name,email,phone,password_hash,role,is_active) VALUES
('Demo Seller','seller@pasalify.com','9822222222',
 '1122334455667788112233445566778811223344556677881122334455667788:2a5c34aa29be7f7a5b73b9a76556485e139a4776b1d763ab524f72143f0cd87b','seller',1);


INSERT IGNORE INTO stores (user_id,name,slug,description,is_approved,is_active)
SELECT id,'Demo Store','demo-store','A demo store for testing.',1,1
FROM users WHERE email='seller@pasalify.com' LIMIT 1;


ALTER TABLE stores ADD COLUMN primary_color VARCHAR(20) DEFAULT '#6C3FC8';
ALTER TABLE stores ADD COLUMN banner_text VARCHAR(255);



CREATE TABLE IF NOT EXISTS content_flags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entity_type ENUM('review','product','user') NOT NULL,
    entity_id INT NOT NULL,
    reason TEXT,
    flagged_by INT,
    status ENUM('pending','reviewed','dismissed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (flagged_by) REFERENCES users(id) ON DELETE SET NULL
);


-- Add applied_promo tracking column to orders if not exists
ALTER TABLE orders ADD COLUMN promo_code VARCHAR(50) DEFAULT NULL;

-- Add avatar support to users (Sprint 3 - US 1.5 Edit Profile)
ALTER TABLE orders MODIFY COLUMN status 
    ENUM('placed','confirmed','processing','shipped','out_for_delivery','delivered','cancelled') 
    DEFAULT 'placed';

-- Ensure wishlists uses standard name (sprint2 used 'wishlist' in queries; fix alias)
-- (No structural change needed — table is 'wishlists')
