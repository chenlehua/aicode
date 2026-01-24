-- =====================================================
-- Medium Test Database: E-Commerce Platform
-- 电商平台测试数据库（中型）
-- Tables: 25 | Views: 10 | Types: 8 | Indexes: 40+
-- =====================================================

-- 清理现有对象
DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO public;

-- =====================================================
-- 扩展 (Extensions)
-- =====================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =====================================================
-- 自定义类型 (Custom Types)
-- =====================================================

-- 用户角色枚举
CREATE TYPE user_role AS ENUM ('customer', 'seller', 'admin', 'support');

-- 用户状态枚举
CREATE TYPE account_status AS ENUM ('active', 'inactive', 'suspended', 'pending_verification');

-- 订单状态枚举
CREATE TYPE order_status AS ENUM ('pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded');

-- 支付状态枚举
CREATE TYPE payment_status AS ENUM ('pending', 'completed', 'failed', 'refunded', 'cancelled');

-- 支付方式枚举
CREATE TYPE payment_method AS ENUM ('credit_card', 'debit_card', 'alipay', 'wechat_pay', 'bank_transfer', 'cod');

-- 商品状态枚举
CREATE TYPE product_status AS ENUM ('draft', 'active', 'out_of_stock', 'discontinued');

-- 优惠券类型枚举
CREATE TYPE coupon_type AS ENUM ('percentage', 'fixed_amount', 'free_shipping', 'buy_x_get_y');

-- 地址类型
CREATE TYPE address_type AS ENUM ('shipping', 'billing', 'both');

-- =====================================================
-- 表结构 (Tables)
-- =====================================================

-- 1. 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    avatar_url VARCHAR(500),
    role user_role NOT NULL DEFAULT 'customer',
    status account_status NOT NULL DEFAULT 'pending_verification',
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    login_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE users IS '用户账户表';
COMMENT ON COLUMN users.role IS '用户角色：customer/seller/admin/support';

-- 2. 用户地址表
CREATE TABLE user_addresses (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    address_type address_type NOT NULL DEFAULT 'both',
    recipient_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    province VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,
    district VARCHAR(50),
    street_address VARCHAR(255) NOT NULL,
    postal_code VARCHAR(20),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE user_addresses IS '用户地址簿';

-- 3. 商家/店铺表
CREATE TABLE stores (
    id SERIAL PRIMARY KEY,
    owner_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    logo_url VARCHAR(500),
    banner_url VARCHAR(500),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    business_license VARCHAR(100),
    rating DECIMAL(3,2) DEFAULT 0.00,
    review_count INTEGER DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE stores IS '商家店铺表';

-- 4. 商品分类表
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon_url VARCHAR(500),
    image_url VARCHAR(500),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    product_count INTEGER DEFAULT 0,
    level INTEGER NOT NULL DEFAULT 1,
    path VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE categories IS '商品分类表，支持多级分类';
COMMENT ON COLUMN categories.path IS '分类路径，如: /1/5/12/';

-- 5. 品牌表
CREATE TABLE brands (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    logo_url VARCHAR(500),
    description TEXT,
    website_url VARCHAR(255),
    country VARCHAR(50),
    is_featured BOOLEAN DEFAULT FALSE,
    product_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE brands IS '商品品牌表';

-- 6. 商品表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    store_id INTEGER NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    brand_id INTEGER REFERENCES brands(id) ON DELETE SET NULL,
    sku VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    short_description VARCHAR(500),
    description TEXT,
    price DECIMAL(12,2) NOT NULL,
    compare_at_price DECIMAL(12,2),
    cost_price DECIMAL(12,2),
    status product_status NOT NULL DEFAULT 'draft',
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    low_stock_threshold INTEGER DEFAULT 10,
    weight DECIMAL(10,3),
    length DECIMAL(10,2),
    width DECIMAL(10,2),
    height DECIMAL(10,2),
    is_featured BOOLEAN DEFAULT FALSE,
    is_taxable BOOLEAN DEFAULT TRUE,
    tax_rate DECIMAL(5,2) DEFAULT 0.00,
    view_count INTEGER DEFAULT 0,
    sold_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0.00,
    review_count INTEGER DEFAULT 0,
    meta_title VARCHAR(100),
    meta_description VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE products IS '商品主表';
COMMENT ON COLUMN products.compare_at_price IS '划线价/原价';
COMMENT ON COLUMN products.cost_price IS '成本价';

-- 7. 商品图片表
CREATE TABLE product_images (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(255),
    sort_order INTEGER DEFAULT 0,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE product_images IS '商品图片表';

-- 8. 商品规格/变体表
CREATE TABLE product_variants (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    sku VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(12,2),
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    weight DECIMAL(10,3),
    option1_name VARCHAR(50),
    option1_value VARCHAR(100),
    option2_name VARCHAR(50),
    option2_value VARCHAR(100),
    option3_name VARCHAR(50),
    option3_value VARCHAR(100),
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE product_variants IS '商品规格变体表';
COMMENT ON COLUMN product_variants.option1_name IS '规格名称，如：颜色、尺寸';

-- 9. 商品标签表
CREATE TABLE product_tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    slug VARCHAR(50) NOT NULL UNIQUE,
    product_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 10. 商品标签关联表
CREATE TABLE product_tag_relations (
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES product_tags(id) ON DELETE CASCADE,
    PRIMARY KEY (product_id, tag_id)
);

-- 11. 购物车表
CREATE TABLE carts (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(100),
    total_items INTEGER DEFAULT 0,
    subtotal DECIMAL(12,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT cart_owner CHECK (user_id IS NOT NULL OR session_id IS NOT NULL)
);

COMMENT ON TABLE carts IS '购物车表，支持登录用户和游客';

-- 12. 购物车项目表
CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    variant_id INTEGER REFERENCES product_variants(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    unit_price DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(cart_id, product_id, variant_id)
);

COMMENT ON TABLE cart_items IS '购物车商品项';

-- 13. 优惠券表
CREATE TABLE coupons (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    coupon_type coupon_type NOT NULL,
    discount_value DECIMAL(12,2) NOT NULL,
    minimum_order_amount DECIMAL(12,2) DEFAULT 0.00,
    maximum_discount DECIMAL(12,2),
    usage_limit INTEGER,
    usage_count INTEGER DEFAULT 0,
    per_user_limit INTEGER DEFAULT 1,
    starts_at TIMESTAMP WITH TIME ZONE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE coupons IS '优惠券表';

-- 14. 用户优惠券关联表
CREATE TABLE user_coupons (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    coupon_id INTEGER NOT NULL REFERENCES coupons(id) ON DELETE CASCADE,
    used_count INTEGER DEFAULT 0,
    claimed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, coupon_id)
);

-- 15. 订单表
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(30) NOT NULL UNIQUE,
    user_id UUID NOT NULL REFERENCES users(id),
    store_id INTEGER NOT NULL REFERENCES stores(id),
    status order_status NOT NULL DEFAULT 'pending',
    subtotal DECIMAL(12,2) NOT NULL,
    discount_amount DECIMAL(12,2) DEFAULT 0.00,
    shipping_fee DECIMAL(12,2) DEFAULT 0.00,
    tax_amount DECIMAL(12,2) DEFAULT 0.00,
    total_amount DECIMAL(12,2) NOT NULL,
    coupon_id INTEGER REFERENCES coupons(id),
    coupon_code VARCHAR(50),
    shipping_name VARCHAR(100),
    shipping_phone VARCHAR(20),
    shipping_address TEXT,
    shipping_method VARCHAR(50),
    tracking_number VARCHAR(100),
    notes TEXT,
    paid_at TIMESTAMP WITH TIME ZONE,
    shipped_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    cancel_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE orders IS '订单主表';

-- 16. 订单项目表
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    variant_id INTEGER REFERENCES product_variants(id),
    product_name VARCHAR(255) NOT NULL,
    variant_name VARCHAR(100),
    sku VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE order_items IS '订单商品项';

-- 17. 支付记录表
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    payment_number VARCHAR(50) NOT NULL UNIQUE,
    payment_method payment_method NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    status payment_status NOT NULL DEFAULT 'pending',
    transaction_id VARCHAR(100),
    gateway_response JSONB,
    paid_at TIMESTAMP WITH TIME ZONE,
    refunded_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE payments IS '支付记录表';

-- 18. 退款记录表
CREATE TABLE refunds (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    payment_id INTEGER REFERENCES payments(id),
    refund_number VARCHAR(50) NOT NULL UNIQUE,
    amount DECIMAL(12,2) NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE refunds IS '退款记录表';

-- 19. 商品评论表
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    order_id INTEGER REFERENCES orders(id),
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(100),
    content TEXT,
    pros TEXT,
    cons TEXT,
    images JSONB,
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    helpful_count INTEGER DEFAULT 0,
    reply TEXT,
    replied_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE reviews IS '商品评论表';

-- 20. 用户收藏表
CREATE TABLE wishlists (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

COMMENT ON TABLE wishlists IS '用户商品收藏表';

-- 21. 浏览历史表
CREATE TABLE browse_history (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(100),
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    viewed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE browse_history IS '用户浏览历史';

-- 22. 库存变动日志表
CREATE TABLE inventory_logs (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    variant_id INTEGER REFERENCES product_variants(id),
    change_quantity INTEGER NOT NULL,
    previous_quantity INTEGER NOT NULL,
    new_quantity INTEGER NOT NULL,
    change_type VARCHAR(30) NOT NULL,
    reference_type VARCHAR(30),
    reference_id INTEGER,
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE inventory_logs IS '库存变动日志';
COMMENT ON COLUMN inventory_logs.change_type IS '变动类型：sale/return/adjustment/restock';

-- 23. 促销活动表
CREATE TABLE promotions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    promotion_type VARCHAR(30) NOT NULL,
    discount_type VARCHAR(20) NOT NULL,
    discount_value DECIMAL(10,2) NOT NULL,
    minimum_purchase DECIMAL(12,2) DEFAULT 0.00,
    maximum_discount DECIMAL(12,2),
    starts_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ends_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE promotions IS '促销活动表';

-- 24. 促销商品关联表
CREATE TABLE promotion_products (
    promotion_id INTEGER NOT NULL REFERENCES promotions(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    PRIMARY KEY (promotion_id, product_id)
);

-- 25. 系统配置表
CREATE TABLE settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) NOT NULL UNIQUE,
    value TEXT,
    value_type VARCHAR(20) NOT NULL DEFAULT 'string',
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE settings IS '系统配置表';

-- =====================================================
-- 索引 (Indexes)
-- =====================================================

-- 用户索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- 用户地址索引
CREATE INDEX idx_user_addresses_user_id ON user_addresses(user_id);
CREATE INDEX idx_user_addresses_default ON user_addresses(user_id, is_default) WHERE is_default = TRUE;

-- 店铺索引
CREATE INDEX idx_stores_owner_id ON stores(owner_id);
CREATE INDEX idx_stores_is_verified ON stores(is_verified);
CREATE INDEX idx_stores_rating ON stores(rating DESC);

-- 分类索引
CREATE INDEX idx_categories_parent_id ON categories(parent_id);
CREATE INDEX idx_categories_level ON categories(level);
CREATE INDEX idx_categories_path ON categories USING gin(path gin_trgm_ops);

-- 商品索引
CREATE INDEX idx_products_store_id ON products(store_id);
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_brand_id ON products(brand_id);
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_rating ON products(rating DESC);
CREATE INDEX idx_products_sold_count ON products(sold_count DESC);
CREATE INDEX idx_products_created_at ON products(created_at DESC);
CREATE INDEX idx_products_name_trgm ON products USING gin(name gin_trgm_ops);
CREATE INDEX idx_products_featured ON products(is_featured) WHERE is_featured = TRUE;

-- 商品图片索引
CREATE INDEX idx_product_images_product_id ON product_images(product_id);
CREATE INDEX idx_product_images_primary ON product_images(product_id, is_primary) WHERE is_primary = TRUE;

-- 商品变体索引
CREATE INDEX idx_product_variants_product_id ON product_variants(product_id);
CREATE INDEX idx_product_variants_sku ON product_variants(sku);

-- 购物车索引
CREATE INDEX idx_carts_user_id ON carts(user_id);
CREATE INDEX idx_carts_session_id ON carts(session_id);
CREATE INDEX idx_cart_items_cart_id ON cart_items(cart_id);
CREATE INDEX idx_cart_items_product_id ON cart_items(product_id);

-- 优惠券索引
CREATE INDEX idx_coupons_code ON coupons(code);
CREATE INDEX idx_coupons_active ON coupons(is_active, starts_at, expires_at);
CREATE INDEX idx_user_coupons_user_id ON user_coupons(user_id);

-- 订单索引
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_store_id ON orders(store_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);
CREATE INDEX idx_orders_order_number ON orders(order_number);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

-- 支付索引
CREATE INDEX idx_payments_order_id ON payments(order_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_refunds_order_id ON refunds(order_id);

-- 评论索引
CREATE INDEX idx_reviews_product_id ON reviews(product_id);
CREATE INDEX idx_reviews_user_id ON reviews(user_id);
CREATE INDEX idx_reviews_rating ON reviews(rating);
CREATE INDEX idx_reviews_created_at ON reviews(created_at DESC);

-- 收藏和浏览历史索引
CREATE INDEX idx_wishlists_user_id ON wishlists(user_id);
CREATE INDEX idx_wishlists_product_id ON wishlists(product_id);
CREATE INDEX idx_browse_history_user_id ON browse_history(user_id);
CREATE INDEX idx_browse_history_product_id ON browse_history(product_id);
CREATE INDEX idx_browse_history_viewed_at ON browse_history(viewed_at DESC);

-- 库存日志索引
CREATE INDEX idx_inventory_logs_product_id ON inventory_logs(product_id);
CREATE INDEX idx_inventory_logs_created_at ON inventory_logs(created_at DESC);

-- 促销索引
CREATE INDEX idx_promotions_active ON promotions(is_active, starts_at, ends_at);
CREATE INDEX idx_promotion_products_product_id ON promotion_products(product_id);

-- =====================================================
-- 视图 (Views)
-- =====================================================

-- 1. 在售商品视图
CREATE VIEW active_products AS
SELECT 
    p.id,
    p.sku,
    p.name,
    p.slug,
    p.price,
    p.compare_at_price,
    p.stock_quantity,
    p.rating,
    p.review_count,
    p.sold_count,
    s.id AS store_id,
    s.name AS store_name,
    c.id AS category_id,
    c.name AS category_name,
    b.id AS brand_id,
    b.name AS brand_name,
    (SELECT url FROM product_images WHERE product_id = p.id AND is_primary = TRUE LIMIT 1) AS primary_image,
    p.created_at
FROM products p
JOIN stores s ON p.store_id = s.id
LEFT JOIN categories c ON p.category_id = c.id
LEFT JOIN brands b ON p.brand_id = b.id
WHERE p.status = 'active' AND p.stock_quantity > 0;

COMMENT ON VIEW active_products IS '在售商品视图，只包含有库存的活跃商品';

-- 2. 订单概览视图
CREATE VIEW order_summary AS
SELECT 
    o.id,
    o.order_number,
    o.user_id,
    u.email AS user_email,
    CONCAT(u.first_name, ' ', u.last_name) AS user_name,
    o.store_id,
    s.name AS store_name,
    o.status,
    o.subtotal,
    o.discount_amount,
    o.shipping_fee,
    o.total_amount,
    o.shipping_name,
    o.shipping_address,
    o.tracking_number,
    (SELECT COUNT(*) FROM order_items WHERE order_id = o.id) AS item_count,
    o.paid_at,
    o.shipped_at,
    o.delivered_at,
    o.created_at
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN stores s ON o.store_id = s.id;

COMMENT ON VIEW order_summary IS '订单概览视图';

-- 3. 商品销售统计视图
CREATE VIEW product_sales_stats AS
SELECT 
    p.id,
    p.name,
    p.sku,
    s.name AS store_name,
    c.name AS category_name,
    p.price,
    p.stock_quantity,
    p.sold_count,
    COALESCE(SUM(oi.quantity), 0) AS total_quantity_sold,
    COALESCE(SUM(oi.total_price), 0) AS total_revenue,
    COUNT(DISTINCT oi.order_id) AS order_count,
    p.view_count,
    p.rating,
    p.review_count
FROM products p
JOIN stores s ON p.store_id = s.id
LEFT JOIN categories c ON p.category_id = c.id
LEFT JOIN order_items oi ON p.id = oi.product_id
GROUP BY p.id, s.name, c.name;

COMMENT ON VIEW product_sales_stats IS '商品销售统计视图';

-- 4. 店铺销售统计视图
CREATE VIEW store_sales_stats AS
SELECT 
    s.id,
    s.name,
    s.slug,
    s.owner_id,
    u.email AS owner_email,
    s.rating,
    s.review_count,
    COUNT(DISTINCT p.id) AS product_count,
    COUNT(DISTINCT o.id) AS order_count,
    COALESCE(SUM(o.total_amount), 0) AS total_sales,
    COALESCE(AVG(o.total_amount), 0) AS avg_order_value,
    s.created_at
FROM stores s
JOIN users u ON s.owner_id = u.id
LEFT JOIN products p ON s.id = p.store_id
LEFT JOIN orders o ON s.id = o.store_id AND o.status NOT IN ('cancelled', 'refunded')
GROUP BY s.id, u.email;

COMMENT ON VIEW store_sales_stats IS '店铺销售统计视图';

-- 5. 用户订单统计视图
CREATE VIEW user_order_stats AS
SELECT 
    u.id,
    u.email,
    CONCAT(u.first_name, ' ', u.last_name) AS full_name,
    u.role,
    u.status,
    COUNT(DISTINCT o.id) AS total_orders,
    COALESCE(SUM(CASE WHEN o.status = 'delivered' THEN 1 ELSE 0 END), 0) AS completed_orders,
    COALESCE(SUM(o.total_amount), 0) AS total_spent,
    COALESCE(AVG(o.total_amount), 0) AS avg_order_value,
    MAX(o.created_at) AS last_order_date,
    u.created_at AS member_since
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.role = 'customer'
GROUP BY u.id;

COMMENT ON VIEW user_order_stats IS '用户订单统计视图';

-- 6. 库存预警视图
CREATE VIEW low_stock_products AS
SELECT 
    p.id,
    p.sku,
    p.name,
    s.name AS store_name,
    p.stock_quantity,
    p.low_stock_threshold,
    p.sold_count,
    p.status
FROM products p
JOIN stores s ON p.store_id = s.id
WHERE p.status = 'active' 
  AND p.stock_quantity <= p.low_stock_threshold;

COMMENT ON VIEW low_stock_products IS '库存预警商品视图';

-- 7. 热销商品视图
CREATE VIEW bestseller_products AS
SELECT 
    p.id,
    p.name,
    p.slug,
    p.price,
    p.sold_count,
    p.rating,
    p.review_count,
    s.name AS store_name,
    c.name AS category_name,
    (SELECT url FROM product_images WHERE product_id = p.id AND is_primary = TRUE LIMIT 1) AS primary_image
FROM products p
JOIN stores s ON p.store_id = s.id
LEFT JOIN categories c ON p.category_id = c.id
WHERE p.status = 'active'
ORDER BY p.sold_count DESC
LIMIT 100;

COMMENT ON VIEW bestseller_products IS '热销商品排行榜（前100）';

-- 8. 每日销售统计视图
CREATE VIEW daily_sales AS
SELECT 
    DATE(o.created_at) AS sale_date,
    COUNT(DISTINCT o.id) AS order_count,
    SUM(o.total_amount) AS total_sales,
    SUM(o.discount_amount) AS total_discounts,
    AVG(o.total_amount) AS avg_order_value,
    COUNT(DISTINCT o.user_id) AS unique_customers
FROM orders o
WHERE o.status NOT IN ('cancelled', 'refunded')
GROUP BY DATE(o.created_at)
ORDER BY sale_date DESC;

COMMENT ON VIEW daily_sales IS '每日销售统计';

-- 9. 分类商品统计视图
CREATE VIEW category_product_stats AS
WITH RECURSIVE category_tree AS (
    SELECT id, name, parent_id, level, 1 AS depth
    FROM categories
    WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.name, c.parent_id, c.level, ct.depth + 1
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT 
    c.id,
    c.name,
    c.level,
    COUNT(DISTINCT p.id) AS product_count,
    COUNT(DISTINCT CASE WHEN p.status = 'active' THEN p.id END) AS active_product_count,
    COALESCE(SUM(p.sold_count), 0) AS total_sold,
    COALESCE(AVG(p.price), 0) AS avg_price
FROM categories c
LEFT JOIN products p ON c.id = p.category_id
GROUP BY c.id;

COMMENT ON VIEW category_product_stats IS '分类商品统计';

-- 10. 优惠券使用统计视图
CREATE VIEW coupon_usage_stats AS
SELECT 
    c.id,
    c.code,
    c.name,
    c.coupon_type,
    c.discount_value,
    c.usage_limit,
    c.usage_count,
    c.is_active,
    c.starts_at,
    c.expires_at,
    COUNT(DISTINCT o.id) AS orders_with_coupon,
    COALESCE(SUM(o.discount_amount), 0) AS total_discount_given,
    COALESCE(SUM(o.total_amount), 0) AS total_order_value
FROM coupons c
LEFT JOIN orders o ON c.id = o.coupon_id AND o.status NOT IN ('cancelled', 'refunded')
GROUP BY c.id;

COMMENT ON VIEW coupon_usage_stats IS '优惠券使用统计';

-- =====================================================
-- 函数 (Functions)
-- =====================================================

-- 生成订单号函数
CREATE OR REPLACE FUNCTION generate_order_number()
RETURNS VARCHAR(30) AS $$
DECLARE
    seq_val BIGINT;
    order_no VARCHAR(30);
BEGIN
    SELECT nextval('orders_id_seq') INTO seq_val;
    order_no := 'ORD' || TO_CHAR(NOW(), 'YYYYMMDD') || LPAD(seq_val::TEXT, 8, '0');
    RETURN order_no;
END;
$$ LANGUAGE plpgsql;

-- 更新商品评分函数
CREATE OR REPLACE FUNCTION update_product_rating()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        UPDATE products SET 
            rating = (SELECT AVG(rating)::DECIMAL(3,2) FROM reviews WHERE product_id = NEW.product_id),
            review_count = (SELECT COUNT(*) FROM reviews WHERE product_id = NEW.product_id)
        WHERE id = NEW.product_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE products SET 
            rating = COALESCE((SELECT AVG(rating)::DECIMAL(3,2) FROM reviews WHERE product_id = OLD.product_id), 0),
            review_count = (SELECT COUNT(*) FROM reviews WHERE product_id = OLD.product_id)
        WHERE id = OLD.product_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 评论触发器
CREATE TRIGGER trigger_update_product_rating
AFTER INSERT OR UPDATE OR DELETE ON reviews
FOR EACH ROW EXECUTE FUNCTION update_product_rating();

-- 更新分类商品计数函数
CREATE OR REPLACE FUNCTION update_category_product_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE categories SET product_count = product_count + 1 WHERE id = NEW.category_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE categories SET product_count = product_count - 1 WHERE id = OLD.category_id;
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' AND OLD.category_id IS DISTINCT FROM NEW.category_id THEN
        UPDATE categories SET product_count = product_count - 1 WHERE id = OLD.category_id;
        UPDATE categories SET product_count = product_count + 1 WHERE id = NEW.category_id;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_category_count
AFTER INSERT OR UPDATE OR DELETE ON products
FOR EACH ROW EXECUTE FUNCTION update_category_product_count();
