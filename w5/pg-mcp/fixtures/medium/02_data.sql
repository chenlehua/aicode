-- =====================================================
-- Medium Test Database: E-Commerce Platform - Test Data
-- 电商平台测试数据
-- =====================================================

-- =====================================================
-- 用户数据 (500 users)
-- =====================================================

-- 管理员和运营用户
INSERT INTO users (email, password_hash, phone, first_name, last_name, role, status, email_verified, login_count) VALUES
('admin@shop.com', '$2b$12$hash_admin', '13800000001', 'Admin', 'User', 'admin', 'active', TRUE, 100),
('support1@shop.com', '$2b$12$hash_support1', '13800000002', 'Support', 'One', 'support', 'active', TRUE, 50),
('support2@shop.com', '$2b$12$hash_support2', '13800000003', 'Support', 'Two', 'support', 'active', TRUE, 45);

-- 商家用户
INSERT INTO users (email, password_hash, phone, first_name, last_name, role, status, email_verified, login_count)
SELECT 
    'seller' || generate_series || '@shop.com',
    '$2b$12$hash_seller_' || generate_series,
    '138' || LPAD(generate_series::TEXT, 8, '0'),
    CASE (generate_series % 5)
        WHEN 0 THEN '张'
        WHEN 1 THEN '李'
        WHEN 2 THEN '王'
        WHEN 3 THEN '刘'
        ELSE '陈'
    END,
    CASE (generate_series % 8)
        WHEN 0 THEN '伟'
        WHEN 1 THEN '芳'
        WHEN 2 THEN '明'
        WHEN 3 THEN '华'
        WHEN 4 THEN '强'
        WHEN 5 THEN '丽'
        WHEN 6 THEN '军'
        ELSE '敏'
    END,
    'seller',
    'active',
    TRUE,
    floor(random() * 100)::int
FROM generate_series(1, 30);

-- 普通客户用户
INSERT INTO users (email, password_hash, phone, first_name, last_name, role, status, email_verified, phone_verified, login_count, last_login_at)
SELECT 
    'customer' || generate_series || '@' || 
    CASE (generate_series % 5)
        WHEN 0 THEN 'gmail.com'
        WHEN 1 THEN 'qq.com'
        WHEN 2 THEN '163.com'
        WHEN 3 THEN 'outlook.com'
        ELSE 'yahoo.com'
    END,
    '$2b$12$hash_customer_' || generate_series,
    '139' || LPAD(generate_series::TEXT, 8, '0'),
    CASE (generate_series % 10)
        WHEN 0 THEN '张'
        WHEN 1 THEN '李'
        WHEN 2 THEN '王'
        WHEN 3 THEN '刘'
        WHEN 4 THEN '陈'
        WHEN 5 THEN '杨'
        WHEN 6 THEN '赵'
        WHEN 7 THEN '黄'
        WHEN 8 THEN '周'
        ELSE '吴'
    END,
    CASE (generate_series % 12)
        WHEN 0 THEN '伟'
        WHEN 1 THEN '芳'
        WHEN 2 THEN '明'
        WHEN 3 THEN '华'
        WHEN 4 THEN '强'
        WHEN 5 THEN '丽'
        WHEN 6 THEN '军'
        WHEN 7 THEN '敏'
        WHEN 8 THEN '磊'
        WHEN 9 THEN '娜'
        WHEN 10 THEN '静'
        ELSE '杰'
    END,
    'customer',
    (CASE WHEN generate_series % 20 = 0 THEN 'inactive' 
         WHEN generate_series % 50 = 0 THEN 'suspended'
         ELSE 'active' END)::account_status,
    generate_series % 3 != 0,
    generate_series % 5 != 0,
    floor(random() * 50)::int,
    NOW() - (random() * 90 || ' days')::interval
FROM generate_series(1, 467);

-- =====================================================
-- 用户地址数据 (800+ addresses)
-- =====================================================

INSERT INTO user_addresses (user_id, address_type, recipient_name, phone, province, city, district, street_address, postal_code, is_default)
SELECT 
    u.id,
    (CASE WHEN row_number() OVER (PARTITION BY u.id ORDER BY random()) = 1 THEN 'both' 
         WHEN random() < 0.5 THEN 'shipping' 
         ELSE 'billing' END)::address_type,
    CONCAT(u.first_name, u.last_name),
    u.phone,
    CASE (floor(random() * 10)::int)
        WHEN 0 THEN '北京市'
        WHEN 1 THEN '上海市'
        WHEN 2 THEN '广东省'
        WHEN 3 THEN '浙江省'
        WHEN 4 THEN '江苏省'
        WHEN 5 THEN '四川省'
        WHEN 6 THEN '湖北省'
        WHEN 7 THEN '山东省'
        WHEN 8 THEN '河南省'
        ELSE '福建省'
    END,
    CASE (floor(random() * 10)::int)
        WHEN 0 THEN '北京'
        WHEN 1 THEN '上海'
        WHEN 2 THEN '广州'
        WHEN 3 THEN '深圳'
        WHEN 4 THEN '杭州'
        WHEN 5 THEN '南京'
        WHEN 6 THEN '成都'
        WHEN 7 THEN '武汉'
        WHEN 8 THEN '青岛'
        ELSE '厦门'
    END,
    '某区',
    '某街道' || floor(random() * 100)::int || '号',
    LPAD(floor(random() * 999999)::TEXT, 6, '0'),
    row_number() OVER (PARTITION BY u.id ORDER BY random()) = 1
FROM users u
CROSS JOIN generate_series(1, 2) AS addr_count
WHERE u.role = 'customer' AND random() < 0.9;

-- =====================================================
-- 店铺数据 (30 stores)
-- =====================================================

INSERT INTO stores (owner_id, name, slug, description, contact_email, contact_phone, rating, review_count, is_verified, is_featured)
SELECT 
    id,
    CASE (row_number() OVER () % 10)
        WHEN 1 THEN '优品数码旗舰店'
        WHEN 2 THEN '潮流服饰专营店'
        WHEN 3 THEN '家居生活馆'
        WHEN 4 THEN '美食天地'
        WHEN 5 THEN '运动健身器材店'
        WHEN 6 THEN '母婴用品专卖'
        WHEN 7 THEN '图书音像店'
        WHEN 8 THEN '美妆护肤店'
        WHEN 9 THEN '户外探险装备'
        ELSE '办公用品批发'
    END || '-' || row_number() OVER (),
    'store-' || row_number() OVER (),
    '专业销售优质商品，诚信经营多年，品质保证！',
    email,
    phone,
    (3.5 + random() * 1.5)::DECIMAL(3,2),
    floor(random() * 1000)::int,
    random() < 0.8,
    random() < 0.2
FROM users
WHERE role = 'seller'
LIMIT 30;

-- =====================================================
-- 分类数据 (60 categories, 3 levels)
-- =====================================================

-- 一级分类
INSERT INTO categories (name, slug, description, level, sort_order) VALUES
('数码电子', 'electronics', '手机、电脑、数码配件等', 1, 1),
('服装服饰', 'clothing', '男装、女装、童装等', 1, 2),
('家居家装', 'home', '家具、家纺、装饰等', 1, 3),
('食品生鲜', 'food', '零食、生鲜、酒水等', 1, 4),
('美妆个护', 'beauty', '护肤、彩妆、个人护理', 1, 5),
('运动户外', 'sports', '运动器材、户外装备', 1, 6),
('母婴用品', 'baby', '婴儿用品、孕妇用品', 1, 7),
('图书音像', 'books', '图书、音乐、影视', 1, 8),
('办公用品', 'office', '文具、办公设备', 1, 9),
('汽车用品', 'auto', '汽车配件、装饰', 1, 10);

-- 二级分类
INSERT INTO categories (parent_id, name, slug, description, level, sort_order) VALUES
-- 数码电子
(1, '手机通讯', 'phones', '智能手机、配件', 2, 1),
(1, '电脑整机', 'computers', '笔记本、台式机', 2, 2),
(1, '电脑配件', 'pc-parts', '显卡、内存、硬盘', 2, 3),
(1, '数码配件', 'accessories', '充电器、数据线', 2, 4),
(1, '摄影摄像', 'camera', '相机、镜头', 2, 5),
-- 服装服饰
(2, '男装', 'mens-wear', '男士服装', 2, 1),
(2, '女装', 'womens-wear', '女士服装', 2, 2),
(2, '童装', 'kids-wear', '儿童服装', 2, 3),
(2, '鞋靴', 'shoes', '各类鞋靴', 2, 4),
(2, '箱包', 'bags', '背包、手提包', 2, 5),
-- 家居家装
(3, '家具', 'furniture', '桌椅、沙发、床', 2, 1),
(3, '家纺', 'textiles', '床品、窗帘', 2, 2),
(3, '厨具', 'kitchen', '锅具、餐具', 2, 3),
(3, '灯具', 'lighting', '吊灯、台灯', 2, 4),
(3, '收纳', 'storage', '收纳盒、置物架', 2, 5),
-- 食品生鲜
(4, '休闲零食', 'snacks', '饼干、糖果、坚果', 2, 1),
(4, '粮油调味', 'groceries', '米面、食用油', 2, 2),
(4, '饮料冲调', 'beverages', '茶、咖啡、饮料', 2, 3),
(4, '生鲜水果', 'fresh', '蔬菜、水果、肉类', 2, 4),
(4, '酒水', 'alcohol', '白酒、红酒、啤酒', 2, 5),
-- 美妆个护
(5, '面部护肤', 'skincare', '洁面、面膜、精华', 2, 1),
(5, '彩妆', 'makeup', '口红、眼影、粉底', 2, 2),
(5, '身体护理', 'bodycare', '沐浴、身体乳', 2, 3),
(5, '香水', 'perfume', '男士香水、女士香水', 2, 4),
(5, '美发护发', 'haircare', '洗发水、护发素', 2, 5);

-- 三级分类（部分）
INSERT INTO categories (parent_id, name, slug, description, level, sort_order) VALUES
(11, '苹果手机', 'iphone', 'iPhone 系列', 3, 1),
(11, '安卓手机', 'android-phones', '三星、华为、小米等', 3, 2),
(11, '手机配件', 'phone-accessories', '手机壳、贴膜', 3, 3),
(12, '笔记本电脑', 'laptops', '各品牌笔记本', 3, 1),
(12, '台式电脑', 'desktops', '组装机、品牌机', 3, 2),
(12, '游戏本', 'gaming-laptops', '游戏笔记本', 3, 3),
(16, 'T恤衬衫', 'mens-shirts', '男士上装', 3, 1),
(16, '裤装', 'mens-pants', '男士裤子', 3, 2),
(16, '外套', 'mens-jackets', '男士外套', 3, 3),
(17, '连衣裙', 'dresses', '女士裙装', 3, 1),
(17, '上衣', 'womens-tops', '女士上装', 3, 2),
(17, '裤子', 'womens-pants', '女士裤装', 3, 3);

-- 更新分类路径
UPDATE categories SET path = '/' || id || '/' WHERE parent_id IS NULL;
UPDATE categories c SET path = (SELECT path FROM categories p WHERE p.id = c.parent_id) || c.id || '/' WHERE c.level = 2;
UPDATE categories c SET path = (SELECT path FROM categories p WHERE p.id = c.parent_id) || c.id || '/' WHERE c.level = 3;

-- =====================================================
-- 品牌数据 (50 brands)
-- =====================================================

INSERT INTO brands (name, slug, description, country, is_featured) VALUES
('Apple', 'apple', '美国科技巨头', '美国', TRUE),
('Samsung', 'samsung', '韩国电子品牌', '韩国', TRUE),
('Huawei', 'huawei', '中国科技公司', '中国', TRUE),
('Xiaomi', 'xiaomi', '小米科技', '中国', TRUE),
('Nike', 'nike', '运动品牌', '美国', TRUE),
('Adidas', 'adidas', '运动品牌', '德国', TRUE),
('Sony', 'sony', '电子产品', '日本', TRUE),
('Dell', 'dell', '电脑品牌', '美国', FALSE),
('Lenovo', 'lenovo', '联想电脑', '中国', FALSE),
('ASUS', 'asus', '华硕电脑', '台湾', FALSE),
('LG', 'lg', '电子产品', '韩国', FALSE),
('Canon', 'canon', '相机品牌', '日本', FALSE),
('Nikon', 'nikon', '相机品牌', '日本', FALSE),
('Dyson', 'dyson', '家电品牌', '英国', TRUE),
('Philips', 'philips', '电子电器', '荷兰', FALSE),
('Estee Lauder', 'estee-lauder', '美妆品牌', '美国', TRUE),
('L''Oreal', 'loreal', '美妆品牌', '法国', TRUE),
('Uniqlo', 'uniqlo', '服装品牌', '日本', TRUE),
('Zara', 'zara', '快时尚品牌', '西班牙', TRUE),
('H&M', 'hm', '快时尚品牌', '瑞典', FALSE),
('Muji', 'muji', '无印良品', '日本', TRUE),
('IKEA', 'ikea', '家居品牌', '瑞典', TRUE),
('Nestle', 'nestle', '食品饮料', '瑞士', FALSE),
('Coca-Cola', 'coca-cola', '饮料品牌', '美国', FALSE),
('P&G', 'pg', '日用品', '美国', FALSE),
('Pampers', 'pampers', '母婴品牌', '美国', FALSE),
('Johnson & Johnson', 'jnj', '个护品牌', '美国', FALSE),
('Rolex', 'rolex', '手表品牌', '瑞士', TRUE),
('Omega', 'omega', '手表品牌', '瑞士', FALSE),
('Seiko', 'seiko', '手表品牌', '日本', FALSE),
('New Balance', 'new-balance', '运动品牌', '美国', FALSE),
('Puma', 'puma', '运动品牌', '德国', FALSE),
('Under Armour', 'under-armour', '运动品牌', '美国', FALSE),
('The North Face', 'north-face', '户外品牌', '美国', FALSE),
('Columbia', 'columbia', '户外品牌', '美国', FALSE),
('Levi''s', 'levis', '牛仔品牌', '美国', FALSE),
('Calvin Klein', 'ck', '时尚品牌', '美国', FALSE),
('Tommy Hilfiger', 'tommy', '时尚品牌', '美国', FALSE),
('Coach', 'coach', '箱包品牌', '美国', FALSE),
('Michael Kors', 'mk', '时尚品牌', '美国', FALSE),
('Chanel', 'chanel', '奢侈品牌', '法国', TRUE),
('Dior', 'dior', '奢侈品牌', '法国', TRUE),
('Gucci', 'gucci', '奢侈品牌', '意大利', TRUE),
('LV', 'louis-vuitton', '奢侈品牌', '法国', TRUE),
('Hermes', 'hermes', '奢侈品牌', '法国', TRUE),
('MSI', 'msi', '电脑品牌', '台湾', FALSE),
('Logitech', 'logitech', '外设品牌', '瑞士', FALSE),
('Razer', 'razer', '游戏外设', '美国', FALSE),
('Bose', 'bose', '音频品牌', '美国', FALSE),
('JBL', 'jbl', '音频品牌', '美国', FALSE);

-- =====================================================
-- 商品数据 (500 products)
-- =====================================================

-- 插入商品
INSERT INTO products (store_id, category_id, brand_id, sku, name, slug, short_description, description, price, compare_at_price, cost_price, status, stock_quantity, low_stock_threshold, weight, is_featured, view_count, sold_count, rating, review_count)
SELECT 
    1 + (gs % 30),
    1 + (gs % 47),
    1 + (gs % 50),
    'SKU-' || LPAD(gs::TEXT, 6, '0'),
    CASE (gs % 20)
        WHEN 0 THEN 'iPhone 15 Pro Max 256GB'
        WHEN 1 THEN 'MacBook Pro 14寸 M3'
        WHEN 2 THEN 'Samsung Galaxy S24 Ultra'
        WHEN 3 THEN '华为 Mate 60 Pro'
        WHEN 4 THEN '小米14 Ultra'
        WHEN 5 THEN 'Nike Air Max 270'
        WHEN 6 THEN 'Adidas Ultraboost 23'
        WHEN 7 THEN '戴森 V15 无线吸尘器'
        WHEN 8 THEN '雅诗兰黛小棕瓶精华'
        WHEN 9 THEN '兰蔻持妆粉底液'
        WHEN 10 THEN '优衣库纯棉T恤'
        WHEN 11 THEN 'ZARA 连衣裙'
        WHEN 12 THEN '宜家 BILLY 书架'
        WHEN 13 THEN '索尼 WH-1000XM5 耳机'
        WHEN 14 THEN '佳能 EOS R6 相机'
        WHEN 15 THEN 'Dell XPS 15 笔记本'
        WHEN 16 THEN '联想拯救者 Y9000P'
        WHEN 17 THEN '新百伦 574 经典款'
        WHEN 18 THEN '帮宝适超薄纸尿裤'
        ELSE '三只松鼠坚果礼盒'
    END || ' #' || gs,
    'product-' || gs,
    '高品质商品，品牌直供，正品保障',
    '## 商品详情\n\n这是一款高品质的产品。\n\n### 产品特点\n- 优质材料\n- 精良工艺\n- 品质保障\n\n### 规格参数\n详见商品规格',
    CASE (gs % 10)
        WHEN 0 THEN 9999.00
        WHEN 1 THEN 12999.00
        WHEN 2 THEN 6999.00
        WHEN 3 THEN 5999.00
        WHEN 4 THEN 4999.00
        WHEN 5 THEN 899.00
        WHEN 6 THEN 1299.00
        WHEN 7 THEN 3999.00
        WHEN 8 THEN 999.00
        ELSE 199.00
    END + (random() * 500)::int,
    CASE WHEN random() < 0.6 THEN 
        (CASE (gs % 10)
            WHEN 0 THEN 10999.00
            WHEN 1 THEN 14999.00
            WHEN 2 THEN 7999.00
            ELSE 1299.00
        END + (random() * 500)::int)
    END,
    (random() * 1000 + 100)::DECIMAL(12,2),
    (CASE WHEN gs % 15 = 0 THEN 'out_of_stock'
         WHEN gs % 25 = 0 THEN 'draft'
         ELSE 'active' END)::product_status,
    floor(random() * 500)::int,
    10,
    (random() * 5)::DECIMAL(10,3),
    gs % 10 = 0,
    floor(random() * 10000)::int,
    floor(random() * 1000)::int,
    (3 + random() * 2)::DECIMAL(3,2),
    floor(random() * 200)::int
FROM generate_series(1, 500) AS gs;

-- =====================================================
-- 商品图片数据 (1500+ images)
-- =====================================================

INSERT INTO product_images (product_id, url, alt_text, sort_order, is_primary)
SELECT 
    p.id,
    'https://picsum.photos/800/800?random=' || p.id || '-' || img_num,
    p.name || ' 图片 ' || img_num,
    img_num,
    img_num = 1
FROM products p
CROSS JOIN generate_series(1, 3) AS img_num;

-- =====================================================
-- 商品变体数据 (1000+ variants)
-- =====================================================

INSERT INTO product_variants (product_id, sku, name, price, stock_quantity, option1_name, option1_value, option2_name, option2_value, is_active)
SELECT 
    p.id,
    p.sku || '-' || 
    CASE (v % 4)
        WHEN 0 THEN 'S'
        WHEN 1 THEN 'M'
        WHEN 2 THEN 'L'
        ELSE 'XL'
    END || '-' ||
    CASE ((v / 4) % 4)
        WHEN 0 THEN 'BLK'
        WHEN 1 THEN 'WHT'
        WHEN 2 THEN 'BLU'
        ELSE 'RED'
    END,
    CASE (v % 4)
        WHEN 0 THEN 'S码-'
        WHEN 1 THEN 'M码-'
        WHEN 2 THEN 'L码-'
        ELSE 'XL码-'
    END ||
    CASE ((v / 4) % 4)
        WHEN 0 THEN '黑色'
        WHEN 1 THEN '白色'
        WHEN 2 THEN '蓝色'
        ELSE '红色'
    END,
    p.price + (v % 3) * 50,
    floor(random() * 100)::int,
    '尺码',
    CASE (v % 4)
        WHEN 0 THEN 'S'
        WHEN 1 THEN 'M'
        WHEN 2 THEN 'L'
        ELSE 'XL'
    END,
    '颜色',
    CASE ((v / 4) % 4)
        WHEN 0 THEN '黑色'
        WHEN 1 THEN '白色'
        WHEN 2 THEN '蓝色'
        ELSE '红色'
    END,
    random() > 0.1
FROM products p
CROSS JOIN generate_series(1, 4) AS v
WHERE p.category_id BETWEEN 16 AND 25;

-- =====================================================
-- 商品标签数据
-- =====================================================

INSERT INTO product_tags (name, slug) VALUES
('新品上市', 'new-arrival'),
('热销', 'bestseller'),
('限时特惠', 'flash-sale'),
('包邮', 'free-shipping'),
('正品保障', 'authentic'),
('品牌直供', 'brand-direct'),
('爆款', 'hot'),
('清仓', 'clearance'),
('预售', 'pre-order'),
('独家', 'exclusive');

-- 关联商品标签
INSERT INTO product_tag_relations (product_id, tag_id)
SELECT DISTINCT product_id, tag_id FROM (
    SELECT 
        gs AS product_id,
        1 + (floor(random() * 10))::int AS tag_id
    FROM generate_series(1, 500) AS gs
    UNION ALL
    SELECT 
        gs AS product_id,
        1 + (floor(random() * 10))::int AS tag_id
    FROM generate_series(1, 300) AS gs
) t
ON CONFLICT DO NOTHING;

-- =====================================================
-- 购物车数据 (200 carts)
-- =====================================================

INSERT INTO carts (user_id, total_items, subtotal)
SELECT 
    id,
    0,
    0
FROM users
WHERE role = 'customer'
ORDER BY random()
LIMIT 200;

-- 购物车商品
INSERT INTO cart_items (cart_id, product_id, quantity, unit_price)
SELECT 
    c.id,
    p.id,
    1 + floor(random() * 3)::int,
    p.price
FROM carts c
CROSS JOIN LATERAL (
    SELECT id, price FROM products WHERE status = 'active' ORDER BY random() LIMIT (1 + floor(random() * 5)::int)
) p;

-- 更新购物车统计
UPDATE carts SET 
    total_items = (SELECT COALESCE(SUM(quantity), 0) FROM cart_items WHERE cart_id = carts.id),
    subtotal = (SELECT COALESCE(SUM(quantity * unit_price), 0) FROM cart_items WHERE cart_id = carts.id);

-- =====================================================
-- 优惠券数据 (20 coupons)
-- =====================================================

INSERT INTO coupons (code, name, description, coupon_type, discount_value, minimum_order_amount, maximum_discount, usage_limit, per_user_limit, starts_at, expires_at, is_active) VALUES
('WELCOME10', '新用户满减', '新用户专享10元优惠', 'fixed_amount', 10.00, 50.00, NULL, 10000, 1, NOW() - INTERVAL '30 days', NOW() + INTERVAL '180 days', TRUE),
('SAVE20', '满200减20', '满200元立减20元', 'fixed_amount', 20.00, 200.00, NULL, 5000, 3, NOW() - INTERVAL '15 days', NOW() + INTERVAL '90 days', TRUE),
('PERCENT15', '85折优惠', '全场商品85折', 'percentage', 15.00, 100.00, 100.00, 3000, 2, NOW() - INTERVAL '7 days', NOW() + INTERVAL '60 days', TRUE),
('FREESHIP', '免运费', '订单满99免运费', 'free_shipping', 0.00, 99.00, NULL, 10000, 5, NOW() - INTERVAL '30 days', NOW() + INTERVAL '365 days', TRUE),
('VIP50', 'VIP专享50元券', 'VIP会员专享优惠', 'fixed_amount', 50.00, 300.00, NULL, 1000, 1, NOW() - INTERVAL '10 days', NOW() + INTERVAL '30 days', TRUE),
('FLASH30', '限时闪购', '限时满300减30', 'fixed_amount', 30.00, 300.00, NULL, 500, 1, NOW(), NOW() + INTERVAL '3 days', TRUE),
('PERCENT20', '8折特惠', '全场8折限时优惠', 'percentage', 20.00, 150.00, 150.00, 2000, 1, NOW() - INTERVAL '5 days', NOW() + INTERVAL '15 days', TRUE),
('DOUBLE11', '双十一大促', '双十一满500减100', 'fixed_amount', 100.00, 500.00, NULL, 50000, 2, NOW() - INTERVAL '20 days', NOW() + INTERVAL '10 days', TRUE),
('SUMMER25', '夏日特惠', '夏季商品75折', 'percentage', 25.00, 200.00, 200.00, 3000, 2, NOW() - INTERVAL '60 days', NOW() + INTERVAL '30 days', TRUE),
('OLDUSER', '老用户回馈', '老用户专享满减', 'fixed_amount', 15.00, 100.00, NULL, 5000, 1, NOW() - INTERVAL '45 days', NOW() + INTERVAL '120 days', TRUE),
('EXPIRED1', '过期券1', '已过期优惠券', 'fixed_amount', 10.00, 50.00, NULL, 1000, 1, NOW() - INTERVAL '90 days', NOW() - INTERVAL '30 days', FALSE),
('EXPIRED2', '过期券2', '已过期优惠券', 'percentage', 10.00, 100.00, 50.00, 1000, 1, NOW() - INTERVAL '60 days', NOW() - INTERVAL '15 days', FALSE),
('BEAUTY10', '美妆专享', '美妆品类满200减10', 'fixed_amount', 10.00, 200.00, NULL, 2000, 2, NOW() - INTERVAL '10 days', NOW() + INTERVAL '60 days', TRUE),
('TECH50', '数码专场', '数码产品满1000减50', 'fixed_amount', 50.00, 1000.00, NULL, 1500, 1, NOW() - INTERVAL '7 days', NOW() + INTERVAL '45 days', TRUE),
('FASHION15', '时尚优惠', '服装鞋包85折', 'percentage', 15.00, 150.00, 80.00, 3000, 2, NOW() - INTERVAL '3 days', NOW() + INTERVAL '30 days', TRUE),
('HOME20', '家居特惠', '家居用品满500减20', 'fixed_amount', 20.00, 500.00, NULL, 2000, 1, NOW() - INTERVAL '20 days', NOW() + INTERVAL '40 days', TRUE),
('FOOD5', '食品专享', '食品满100减5', 'fixed_amount', 5.00, 100.00, NULL, 5000, 3, NOW() - INTERVAL '15 days', NOW() + INTERVAL '90 days', TRUE),
('SPORTS10', '运动专区', '运动用品9折', 'percentage', 10.00, 200.00, 100.00, 2500, 2, NOW() - INTERVAL '12 days', NOW() + INTERVAL '60 days', TRUE),
('BABY15', '母婴优惠', '母婴产品满300减15', 'fixed_amount', 15.00, 300.00, NULL, 2000, 2, NOW() - INTERVAL '8 days', NOW() + INTERVAL '75 days', TRUE),
('BOOK10', '图书特惠', '图书满100减10', 'fixed_amount', 10.00, 100.00, NULL, 3000, 3, NOW() - INTERVAL '5 days', NOW() + INTERVAL '120 days', TRUE);

-- 用户领取优惠券
INSERT INTO user_coupons (user_id, coupon_id)
SELECT DISTINCT u.id, c.id
FROM users u
CROSS JOIN coupons c
WHERE u.role = 'customer' AND random() < 0.15
ON CONFLICT DO NOTHING;

-- =====================================================
-- 订单数据 (2000+ orders)
-- =====================================================

-- 生成订单
INSERT INTO orders (order_number, user_id, store_id, status, subtotal, discount_amount, shipping_fee, tax_amount, total_amount, shipping_name, shipping_phone, shipping_address, paid_at, shipped_at, delivered_at, created_at)
SELECT 
    'ORD' || TO_CHAR(NOW() - (gs || ' days')::interval, 'YYYYMMDD') || LPAD(gs::TEXT, 6, '0'),
    u.id,
    1 + (gs % 30),
    CASE (gs % 10)
        WHEN 0 THEN 'pending'
        WHEN 1 THEN 'paid'
        WHEN 2 THEN 'processing'
        WHEN 3 THEN 'shipped'
        WHEN 8 THEN 'cancelled'
        WHEN 9 THEN 'refunded'
        ELSE 'delivered'
    END::order_status,
    (random() * 2000 + 100)::DECIMAL(12,2),
    CASE WHEN random() < 0.3 THEN (random() * 50)::DECIMAL(12,2) ELSE 0 END,
    CASE WHEN random() < 0.7 THEN 0 ELSE (random() * 15)::DECIMAL(12,2) END,
    0,
    0,
    CONCAT(u.first_name, u.last_name),
    u.phone,
    '某省某市某区某街道某号',
    CASE WHEN gs % 10 NOT IN (0) THEN NOW() - ((gs - 1) || ' days')::interval END,
    CASE WHEN gs % 10 IN (3,4,5,6,7) THEN NOW() - ((gs - 2) || ' days')::interval END,
    CASE WHEN gs % 10 IN (4,5,6,7) THEN NOW() - ((gs - 3) || ' days')::interval END,
    NOW() - (gs || ' days')::interval
FROM generate_series(1, 2000) AS gs
CROSS JOIN LATERAL (
    SELECT id, first_name, last_name, phone FROM users WHERE role = 'customer' ORDER BY random() LIMIT 1
) u;

-- 更新订单总额
UPDATE orders SET total_amount = subtotal - discount_amount + shipping_fee + tax_amount;

-- 订单商品项
INSERT INTO order_items (order_id, product_id, product_name, sku, quantity, unit_price, total_price)
SELECT 
    o.id,
    p.id,
    p.name,
    p.sku,
    1 + floor(random() * 3)::int,
    p.price,
    p.price * (1 + floor(random() * 3)::int)
FROM orders o
CROSS JOIN LATERAL (
    SELECT id, name, sku, price FROM products WHERE status = 'active' ORDER BY random() LIMIT (1 + floor(random() * 4)::int)
) p;

-- =====================================================
-- 支付数据 (1800+ payments)
-- =====================================================

INSERT INTO payments (order_id, payment_number, payment_method, amount, status, paid_at)
SELECT 
    id,
    'PAY' || order_number,
    (ARRAY['credit_card', 'alipay', 'wechat_pay', 'debit_card', 'bank_transfer'])[1 + floor(random() * 5)::int]::payment_method,
    total_amount,
    CASE 
        WHEN status IN ('paid', 'processing', 'shipped', 'delivered') THEN 'completed'
        WHEN status = 'refunded' THEN 'refunded'
        WHEN status = 'cancelled' THEN 'cancelled'
        ELSE 'pending'
    END::payment_status,
    paid_at
FROM orders
WHERE status != 'pending';

-- =====================================================
-- 评论数据 (3000+ reviews)
-- =====================================================

INSERT INTO reviews (product_id, user_id, rating, title, content, is_verified_purchase, helpful_count, created_at)
SELECT 
    p.id,
    u.id,
    3 + floor(random() * 3)::int,
    CASE (floor(random() * 10)::int)
        WHEN 0 THEN '非常满意'
        WHEN 1 THEN '物超所值'
        WHEN 2 THEN '质量很好'
        WHEN 3 THEN '推荐购买'
        WHEN 4 THEN '还不错'
        WHEN 5 THEN '性价比高'
        WHEN 6 THEN '发货快'
        WHEN 7 THEN '包装完好'
        WHEN 8 THEN '符合预期'
        ELSE '回购用户'
    END,
    CASE (floor(random() * 10)::int)
        WHEN 0 THEN '商品质量非常好，和描述一致，物流也很快，非常满意的一次购物体验！'
        WHEN 1 THEN '价格实惠，性价比很高，下次还会再来购买。'
        WHEN 2 THEN '包装很仔细，没有破损，产品质量也不错。'
        WHEN 3 THEN '客服服务态度很好，有问必答，购物愉快。'
        WHEN 4 THEN '使用了一段时间了，质量稳定，推荐购买。'
        WHEN 5 THEN '物流速度快，两天就到了，商品也很好。'
        WHEN 6 THEN '做工精细，材质上乘，值得购买。'
        WHEN 7 THEN '第二次购买了，一如既往的好！'
        WHEN 8 THEN '颜色和图片一样，尺寸合适，很满意。'
        ELSE '总体来说还不错，可以推荐给朋友。'
    END,
    random() < 0.7,
    floor(random() * 50)::int,
    NOW() - (random() * 180 || ' days')::interval
FROM generate_series(1, 3000) AS gs
CROSS JOIN LATERAL (
    SELECT id FROM products WHERE status = 'active' ORDER BY random() LIMIT 1
) p
CROSS JOIN LATERAL (
    SELECT id FROM users WHERE role = 'customer' ORDER BY random() LIMIT 1
) u;

-- =====================================================
-- 收藏数据 (2000+ wishlists)
-- =====================================================

INSERT INTO wishlists (user_id, product_id)
SELECT DISTINCT u.id, p.id FROM (
    SELECT 
        (SELECT id FROM users WHERE role = 'customer' ORDER BY random() LIMIT 1) AS user_id,
        (SELECT id FROM products WHERE status = 'active' ORDER BY random() LIMIT 1) AS product_id
    FROM generate_series(1, 2500)
) t
CROSS JOIN LATERAL (SELECT id FROM users WHERE id = t.user_id) u
CROSS JOIN LATERAL (SELECT id FROM products WHERE id = t.product_id) p
ON CONFLICT DO NOTHING;

-- =====================================================
-- 浏览历史数据 (10000+ records)
-- =====================================================

INSERT INTO browse_history (user_id, product_id, viewed_at)
SELECT 
    (SELECT id FROM users WHERE role = 'customer' ORDER BY random() LIMIT 1),
    (SELECT id FROM products ORDER BY random() LIMIT 1),
    NOW() - (random() * 30 || ' days')::interval
FROM generate_series(1, 10000);

-- =====================================================
-- 促销活动数据
-- =====================================================

INSERT INTO promotions (name, description, promotion_type, discount_type, discount_value, minimum_purchase, starts_at, ends_at, is_active, priority) VALUES
('新年大促', '新年期间全场优惠', 'sitewide', 'percentage', 10.00, 100.00, NOW() - INTERVAL '10 days', NOW() + INTERVAL '20 days', TRUE, 10),
('数码专场', '数码产品限时特惠', 'category', 'percentage', 15.00, 500.00, NOW() - INTERVAL '5 days', NOW() + INTERVAL '10 days', TRUE, 8),
('品牌特卖', '指定品牌商品优惠', 'brand', 'fixed_amount', 50.00, 300.00, NOW() - INTERVAL '3 days', NOW() + INTERVAL '7 days', TRUE, 5),
('清仓促销', '库存清理大甩卖', 'clearance', 'percentage', 30.00, 0.00, NOW() - INTERVAL '15 days', NOW() + INTERVAL '15 days', TRUE, 3),
('会员日', '会员专享优惠', 'member', 'percentage', 20.00, 200.00, NOW() - INTERVAL '1 day', NOW() + INTERVAL '1 day', TRUE, 15);

-- 关联促销商品
INSERT INTO promotion_products (promotion_id, product_id)
SELECT DISTINCT ON (promotion_id, product_id)
    promotion_id,
    product_id
FROM (
    SELECT 
        p.id AS promotion_id,
        (SELECT id FROM products WHERE status = 'active' ORDER BY random() LIMIT 1) AS product_id
    FROM promotions p
    CROSS JOIN generate_series(1, 20)
) t
ON CONFLICT DO NOTHING;

-- =====================================================
-- 系统配置数据
-- =====================================================

INSERT INTO settings (key, value, value_type, description, is_public) VALUES
('site_name', '优品商城', 'string', '网站名称', TRUE),
('site_description', '您的一站式购物平台', 'string', '网站描述', TRUE),
('currency', 'CNY', 'string', '默认货币', TRUE),
('tax_rate', '0.13', 'decimal', '默认税率', FALSE),
('free_shipping_threshold', '99', 'decimal', '免运费门槛', TRUE),
('default_shipping_fee', '10', 'decimal', '默认运费', TRUE),
('max_cart_items', '50', 'integer', '购物车最大商品数', FALSE),
('order_expire_minutes', '30', 'integer', '未支付订单过期时间（分钟）', FALSE),
('review_auto_approve', 'true', 'boolean', '评论自动审核', FALSE),
('maintenance_mode', 'false', 'boolean', '维护模式', FALSE);

-- =====================================================
-- 更新统计数据
-- =====================================================

-- 更新品牌商品计数
UPDATE brands SET product_count = (
    SELECT COUNT(*) FROM products WHERE brand_id = brands.id
);

-- 更新分类商品计数
UPDATE categories SET product_count = (
    SELECT COUNT(*) FROM products WHERE category_id = categories.id
);

-- 更新标签商品计数
UPDATE product_tags SET product_count = (
    SELECT COUNT(*) FROM product_tag_relations WHERE tag_id = product_tags.id
);

-- 更新商品售出数量
UPDATE products SET sold_count = COALESCE((
    SELECT SUM(quantity) FROM order_items WHERE product_id = products.id
), sold_count);
