PRAGMA foreign_keys = ON;

-- ─────────────────────────────────────────
-- REGIONS
-- ─────────────────────────────────────────
INSERT INTO regions (name, country) VALUES
('North America', 'USA'),
('South Asia',    'India'),
('Europe',        'Germany'),
('East Asia',     'Japan'),
('Middle East',   'UAE');

-- ─────────────────────────────────────────
-- CATEGORIES  (parent → child)
-- ─────────────────────────────────────────
INSERT INTO categories (name, parent_id) VALUES
('Electronics',      NULL),   -- 1
('Computers',        1),      -- 2
('Mobile Phones',    1),      -- 3
('Accessories',      1),      -- 4
('Home & Kitchen',   NULL),   -- 5
('Appliances',       5),      -- 6
('Cookware',         5),      -- 7
('Sports',           NULL),   -- 8
('Fitness',          8),      -- 9
('Outdoor',          8),      -- 10
('Books',            NULL),   -- 11
('Fiction',          11),     -- 12
('Non-Fiction',      11);     -- 13

-- ─────────────────────────────────────────
-- SELLERS
-- ─────────────────────────────────────────
INSERT INTO sellers (name, email, region_id, rating, joined_at) VALUES
('TechZone Inc.',      'techzone@seller.com',   1, 4.8, '2022-01-10'),
('GadgetHub',          'gadgethub@seller.com',  2, 4.5, '2022-03-15'),
('HomeEssentials',     'home@seller.com',       3, 4.2, '2021-11-20'),
('SportsPro',          'sport@seller.com',      1, 4.7, '2022-06-01'),
('BookWave',           'books@seller.com',      4, 4.9, '2020-08-25'),
('MobileMart',         'mobile@seller.com',     2, 4.3, '2023-01-05'),
('KitchenKing',        'kitchen@seller.com',    5, 4.6, '2021-07-18');

-- ─────────────────────────────────────────
-- USERS
-- ─────────────────────────────────────────
INSERT INTO users (name, email, phone, region_id, created_at, is_active) VALUES
('Alice Johnson',   'alice@example.com',   '+1-555-1001', 1, '2023-01-15', 1),
('Bob Smith',       'bob@example.com',     '+1-555-1002', 1, '2023-02-20', 1),
('Charlie Lee',     'charlie@example.com', '+91-98001',   2, '2023-03-10', 1),
('Diana Müller',    'diana@example.com',   '+49-30-001',  3, '2023-04-05', 1),
('Ethan Tanaka',    'ethan@example.com',   '+81-3-001',   4, '2023-05-12', 1),
('Fiona Patel',     'fiona@example.com',   '+91-98002',   2, '2023-06-18', 1),
('George Hassan',   'george@example.com',  '+971-50001',  5, '2023-07-22', 1),
('Hannah Kim',      'hannah@example.com',  '+82-2-001',   4, '2023-08-30', 1),
('Ivan Petrov',     'ivan@example.com',    '+49-30-002',  3, '2023-09-14', 1),
('Julia Adams',     'julia@example.com',   '+1-555-1010', 1, '2023-10-01', 1),
('Kevin Okafor',    'kevin@example.com',   '+971-50002',  5, '2024-01-10', 1),
('Laura Chen',      'laura@example.com',   '+1-555-1012', 1, '2024-02-14', 1),
('Mark Wilson',     'mark@example.com',    '+91-98003',   2, '2024-03-08', 0),  -- deactivated
('Nina Rossi',      'nina@example.com',    '+49-30-003',  3, '2024-04-22', 1),
('Oscar Yamamoto',  'oscar@example.com',   '+81-3-002',   4, '2024-05-30', 1);

-- ─────────────────────────────────────────
-- ADDRESSES
-- ─────────────────────────────────────────
INSERT INTO addresses (user_id, label, street, city, state, zip, country, is_default) VALUES
(1,  'home',  '12 Maple St',     'New York',    'NY', '10001', 'USA',     1),
(1,  'work',  '99 Office Blvd',  'New York',    'NY', '10002', 'USA',     0),
(2,  'home',  '45 Oak Ave',      'Los Angeles', 'CA', '90001', 'USA',     1),
(3,  'home',  '7 Gandhi Nagar',  'Mumbai',      'MH', '400001','India',   1),
(4,  'home',  'Berliner Str 3',  'Berlin',      NULL, '10115', 'Germany', 1),
(5,  'home',  '2-3 Shinjuku',    'Tokyo',       NULL, '160-0022','Japan', 1),
(6,  'home',  '14 MG Road',      'Bangalore',   'KA', '560001','India',   1),
(7,  'home',  'Sheikh Zayed Rd', 'Dubai',       NULL, '00000', 'UAE',     1),
(8,  'home',  '55 Gangnam-gu',   'Seoul',       NULL, '06000', 'South Korea', 1),
(9,  'home',  'Hauptstr 10',     'Munich',      NULL, '80331', 'Germany', 1),
(10, 'home',  '301 Elm St',      'Chicago',     'IL', '60601', 'USA',     1),
(11, 'home',  'Al Wasl Rd 7',    'Dubai',       NULL, '00000', 'UAE',     1),
(12, 'home',  '88 Sunset Blvd',  'Seattle',     'WA', '98101', 'USA',     1),
(14, 'home',  'Via Roma 22',     'Rome',        NULL, '00100', 'Italy',   1),
(15, 'home',  '9 Shibuya',       'Tokyo',       NULL, '150-0002','Japan', 1);

-- ─────────────────────────────────────────
-- PRODUCTS
-- ─────────────────────────────────────────
INSERT INTO products (seller_id, category_id, name, description, price, cost, stock, sku, created_at) VALUES
-- Computers
(1, 2,  'ProBook Laptop 14"',     '14-inch laptop, 16GB RAM, 512GB SSD',        1199.99, 850.00, 30,  'SKU-LP-001', '2023-01-01'),
(1, 2,  'UltraBook Pro 15"',      '15-inch laptop, 32GB RAM, 1TB SSD',          1799.99,1200.00, 15,  'SKU-LP-002', '2023-02-01'),
(1, 2,  'BudgetBook 11"',         'Entry-level laptop, 8GB RAM, 256GB SSD',      499.99, 300.00, 50,  'SKU-LP-003', '2023-03-01'),
-- Mobile Phones
(6, 3,  'Galaxy X20',             '6.5-inch AMOLED, 128GB storage',              799.99, 500.00, 60,  'SKU-PH-001', '2023-01-15'),
(6, 3,  'Galaxy X20 Pro',         '6.7-inch AMOLED, 256GB, 108MP camera',       1099.99, 720.00, 40,  'SKU-PH-002', '2023-02-15'),
(6, 3,  'NovaPhone 5G',           'Budget 5G phone, 64GB',                       349.99, 200.00, 80,  'SKU-PH-003', '2023-04-01'),
-- Accessories
(2, 4,  'Wireless Mouse',         'Ergonomic wireless mouse',                     29.99,  12.00,200,  'SKU-AC-001', '2023-01-05'),
(2, 4,  'Mechanical Keyboard',    'RGB mechanical keyboard, TKL',                 89.99,  45.00,120,  'SKU-AC-002', '2023-01-05'),
(2, 4,  'USB-C Hub 7-in-1',       'Multiport USB-C hub',                          49.99,  22.00,150,  'SKU-AC-003', '2023-03-10'),
(2, 4,  'Noise Cancelling Headphones','Over-ear ANC headphones',                 199.99, 110.00, 75,  'SKU-AC-004', '2023-05-01'),
-- Appliances
(3, 6,  'Smart Air Purifier',     'HEPA filter, 500 sq ft coverage',             249.99, 140.00, 25,  'SKU-AP-001', '2023-02-20'),
(3, 6,  'Robot Vacuum Pro',       'LiDAR navigation, 3000Pa suction',            399.99, 230.00, 20,  'SKU-AP-002', '2023-03-15'),
-- Cookware
(7, 7,  'Cast Iron Skillet 12"',  'Pre-seasoned cast iron, oven-safe',            59.99,  28.00, 90,  'SKU-CW-001', '2023-01-20'),
(7, 7,  'Non-Stick Pan Set 5pc',  '5-piece non-stick cookware set',               99.99,  50.00, 60,  'SKU-CW-002', '2023-02-10'),
-- Fitness
(4, 9,  'Yoga Mat Premium',       '6mm thick, non-slip, eco-friendly',            39.99,  15.00,200,  'SKU-FT-001', '2023-01-10'),
(4, 9,  'Adjustable Dumbbells',   '5-52.5 lbs per dumbbell',                     299.99, 170.00, 30,  'SKU-FT-002', '2023-02-25'),
(4, 9,  'Resistance Band Set',    '5-band set, various resistance levels',         19.99,   7.00,300,  'SKU-FT-003', '2023-03-05'),
-- Outdoor
(4, 10, 'Camping Tent 4-Person',  'Waterproof, easy setup',                      149.99,  85.00, 40,  'SKU-OT-001', '2023-04-10'),
(4, 10, 'Hiking Backpack 50L',    'Ergonomic, rain cover included',              119.99,  65.00, 55,  'SKU-OT-002', '2023-05-15'),
-- Books
(5, 12, 'The Silent Forest',      'A mystery thriller novel',                     14.99,   5.00,500,  'SKU-BK-001', '2022-12-01'),
(5, 12, 'Galaxy''s Edge',         'Sci-fi space opera',                           12.99,   4.50,400,  'SKU-BK-002', '2022-12-15'),
(5, 13, 'Atomic Habits',          'Habit-building guide',                          16.99,   6.00,600,  'SKU-BK-003', '2023-01-01'),
(5, 13, 'Zero to One',            'Startup and innovation book',                   18.99,   7.00,350,  'SKU-BK-004', '2023-01-15');

-- ─────────────────────────────────────────
-- PROMOTIONS
-- ─────────────────────────────────────────
INSERT INTO promotions (code, discount_type, discount_value, min_order_value, valid_from, valid_until, usage_limit, times_used) VALUES
('WELCOME10',  'PERCENT', 10,  0,    '2023-01-01', '2024-12-31', 1000, 320),
('SAVE50',     'FIXED',   50,  300,  '2023-06-01', '2023-12-31', 200,  198),
('SUMMER20',   'PERCENT', 20,  100,  '2023-07-01', '2023-08-31', 500,  412),
('FLASH15',    'PERCENT', 15,  0,    '2024-01-01', '2024-01-31', 300,  288),
('FREESHIP',   'FIXED',   0,   0,    '2023-01-01', '2025-12-31', 9999, 874),
('TECH100',    'FIXED',   100, 500,  '2023-09-01', '2023-11-30', 150,  143),
('NEWYEAR25',  'PERCENT', 25,  200,  '2024-01-01', '2024-01-07', 500,  499);

-- ─────────────────────────────────────────
-- ORDERS  (spread across ~14 months)
-- ─────────────────────────────────────────
INSERT INTO orders (user_id, address_id, promotion_id, status, order_date, delivered_at) VALUES
-- 2023 Q1
( 1,  1, 1,    'DELIVERED', '2023-01-20 10:00', '2023-01-25 14:00'),
( 2,  3, NULL, 'DELIVERED', '2023-01-28 11:30', '2023-02-02 10:00'),
( 3,  4, 1,    'DELIVERED', '2023-02-05 09:00', '2023-02-10 16:00'),
( 4,  5, NULL, 'DELIVERED', '2023-02-14 14:00', '2023-02-19 12:00'),
( 5,  6, 1,    'DELIVERED', '2023-02-22 08:00', '2023-02-28 10:00'),
-- 2023 Q2
( 1,  1, NULL, 'DELIVERED', '2023-04-03 12:00', '2023-04-08 11:00'),
( 6,  7, 1,    'DELIVERED', '2023-04-15 15:00', '2023-04-20 13:00'),
( 7,  8, NULL, 'DELIVERED', '2023-05-01 10:00', '2023-05-06 14:00'),
( 8,  9, 1,    'DELIVERED', '2023-05-18 09:30', '2023-05-23 11:00'),
( 2,  3, NULL, 'DELIVERED', '2023-06-10 16:00', '2023-06-15 10:00'),
-- 2023 Q3
( 9, 10, 2,    'DELIVERED', '2023-07-04 10:00', '2023-07-10 15:00'),
(10, 11, 3,    'DELIVERED', '2023-07-22 11:00', '2023-07-28 09:00'),
( 1,  1, 3,    'DELIVERED', '2023-08-08 09:00', '2023-08-14 12:00'),
( 3,  4, 3,    'DELIVERED', '2023-08-20 14:00', '2023-08-26 10:00'),
( 5,  6, NULL, 'DELIVERED', '2023-09-05 10:30', '2023-09-11 14:00'),
-- 2023 Q4
( 4,  5, 6,    'DELIVERED', '2023-10-10 12:00', '2023-10-16 11:00'),
( 6,  7, 6,    'DELIVERED', '2023-10-25 09:00', '2023-10-31 10:00'),
(11, 12, NULL, 'DELIVERED', '2023-11-08 15:00', '2023-11-14 13:00'),
(12, 13, 1,    'DELIVERED', '2023-11-20 10:00', '2023-11-26 14:00'),
( 2,  3, 1,    'DELIVERED', '2023-12-02 11:00', '2023-12-08 10:00'),
( 7,  8, 7,    'DELIVERED', '2023-12-15 09:00', '2023-12-21 16:00'),
( 9, 10, 7,    'DELIVERED', '2023-12-28 14:00', '2024-01-03 11:00'),
-- 2024 Q1
( 1,  1, 4,    'DELIVERED', '2024-01-05 10:00', '2024-01-11 14:00'),
(10, 11, 4,    'DELIVERED', '2024-01-18 09:00', '2024-01-24 10:00'),
(13, NULL,NULL,'CANCELLED', '2024-01-22 11:00',  NULL),
( 3,  4, NULL, 'DELIVERED', '2024-02-06 14:00', '2024-02-12 11:00'),
(14, 14, 1,    'DELIVERED', '2024-02-18 10:00', '2024-02-24 15:00'),
(15, 15, NULL, 'DELIVERED', '2024-03-07 09:30', '2024-03-13 12:00'),
( 5,  6, NULL, 'DELIVERED', '2024-03-20 15:00', '2024-03-26 10:00'),
-- 2024 Q2
( 8,  9, 1,    'DELIVERED', '2024-04-03 11:00', '2024-04-09 14:00'),
(11, 12, NULL, 'DELIVERED', '2024-04-18 10:00', '2024-04-24 11:00'),
( 1,  1, NULL, 'DELIVERED', '2024-05-02 09:00', '2024-05-08 13:00'),
(12, 13, 1,    'DELIVERED', '2024-05-15 14:00', '2024-05-21 10:00'),
( 6,  7, NULL, 'DELIVERED', '2024-06-01 10:30', '2024-06-07 12:00'),
( 2,  3, 1,    'DELIVERED', '2024-06-20 11:00', '2024-06-26 15:00'),
-- 2024 Q3 — recent months for "past 1 month" queries
( 4,  5, NULL, 'DELIVERED', '2024-07-05 09:00', '2024-07-11 10:00'),
(10, 11, 1,    'DELIVERED', '2024-07-19 14:00', '2024-07-25 11:00'),
( 7,  8, NULL, 'DELIVERED', '2024-08-02 10:00', '2024-08-08 14:00'),
( 9, 10, 1,    'SHIPPED',   '2024-08-15 11:00',  NULL),
(15, 15, NULL, 'CONFIRMED', '2024-08-20 09:30',  NULL),
(14, 14, NULL, 'PENDING',   '2024-08-22 10:00',  NULL);

-- ─────────────────────────────────────────
-- ORDER ITEMS
-- ─────────────────────────────────────────
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
-- Order 1 (Alice, Jan 2023)
(1, 1, 1, 1199.99),(1, 7, 1, 29.99),
-- Order 2 (Bob)
(2, 8, 1, 89.99),(2, 9, 2, 49.99),
-- Order 3 (Charlie)
(3, 4, 1, 799.99),(3, 7, 1, 29.99),
-- Order 4 (Diana)
(4, 11, 1, 249.99),
-- Order 5 (Ethan)
(5, 10, 1, 199.99),(5, 22, 1, 16.99),
-- Order 6 (Alice, Apr 2023)
(6, 2, 1, 1799.99),
-- Order 7 (Fiona)
(7, 5, 1, 1099.99),
-- Order 8 (George)
(8, 12, 1, 399.99),(8, 15, 2, 39.99),
-- Order 9 (Hannah)
(9, 13, 1, 59.99),(9, 14, 1, 99.99),
-- Order 10 (Bob)
(10, 16, 1, 299.99),(10, 17, 3, 19.99),
-- Order 11 (Ivan)
(11, 18, 1, 149.99),(11, 19, 1, 119.99),
-- Order 12 (Julia)
(12, 20, 2, 14.99),(12, 21, 1, 12.99),(12, 22, 1, 16.99),
-- Order 13 (Alice, Aug 2023)
(13, 3, 1, 499.99),(13, 8, 1, 89.99),
-- Order 14 (Charlie)
(14, 6, 2, 349.99),(14, 9, 1, 49.99),
-- Order 15 (Ethan)
(15, 10, 1, 199.99),
-- Order 16 (Diana)
(16, 1, 1, 1199.99),(16, 8, 1, 89.99),
-- Order 17 (Fiona)
(17, 5, 1, 1099.99),(17, 9, 2, 49.99),
-- Order 18 (Kevin)
(18, 11, 1, 249.99),(18, 12, 1, 399.99),
-- Order 19 (Laura)
(19, 4, 1, 799.99),(19, 7, 2, 29.99),
-- Order 20 (Bob)
(20, 16, 1, 299.99),(20, 17, 2, 19.99),
-- Order 21 (George)
(21, 2, 1, 1799.99),
-- Order 22 (Ivan)
(22, 23, 2, 18.99),(22, 20, 3, 14.99),
-- Order 23 (Alice, Jan 2024)
(23, 1, 1, 1199.99),(23, 10, 1, 199.99),
-- Order 24 (Julia)
(24, 5, 1, 1099.99),(24, 22, 2, 16.99),
-- Order 25 (Mark - cancelled)
(25, 4, 1, 799.99),
-- Order 26 (Charlie)
(26, 6, 1, 349.99),(26, 15, 1, 39.99),
-- Order 27 (Nina)
(27, 13, 2, 59.99),(27, 14, 1, 99.99),
-- Order 28 (Oscar)
(28, 18, 1, 149.99),(28, 19, 1, 119.99),
-- Order 29 (Ethan)
(29, 3, 1, 499.99),(29, 7, 1, 29.99),
-- Order 30 (Hannah)
(30, 11, 1, 249.99),
-- Order 31 (Kevin)
(31, 12, 1, 399.99),(31, 15, 2, 39.99),
-- Order 32 (Alice)
(32, 2, 1, 1799.99),(32, 9, 1, 49.99),
-- Order 33 (Laura)
(33, 4, 1, 799.99),(33, 10, 1, 199.99),
-- Order 34 (Fiona)
(34, 5, 1, 1099.99),
-- Order 35 (Bob)
(35, 1, 1, 1199.99),(35, 8, 1, 89.99),
-- Order 36 (Diana)
(36, 16, 1, 299.99),(36, 17, 2, 19.99),
-- Order 37 (Julia)
(37, 18, 1, 149.99),(37, 19, 1, 119.99),
-- Order 38 (George)
(38, 11, 1, 249.99),(38, 13, 1, 59.99),
-- Order 39 (Ivan, shipped)
(39, 2, 1, 1799.99),
-- Order 40 (Oscar, confirmed)
(40, 5, 1, 1099.99),(40, 22, 1, 16.99),
-- Order 41 (Nina, pending)
(41, 3, 1, 499.99);

-- ─────────────────────────────────────────
-- PAYMENTS
-- ─────────────────────────────────────────
INSERT INTO payments (order_id, method, amount, status, paid_at, transaction_id) VALUES
(1,  'CARD',          1229.98, 'SUCCESS', '2023-01-20 10:05', 'TXN-0001'),
(2,  'UPI',            189.97, 'SUCCESS', '2023-01-28 11:35', 'TXN-0002'),
(3,  'CARD',           719.99, 'SUCCESS', '2023-02-05 09:10', 'TXN-0003'),
(4,  'WALLET',         249.99, 'SUCCESS', '2023-02-14 14:05', 'TXN-0004'),
(5,  'CARD',           216.98, 'SUCCESS', '2023-02-22 08:10', 'TXN-0005'),
(6,  'CARD',          1799.99, 'SUCCESS', '2023-04-03 12:05', 'TXN-0006'),
(7,  'BANK_TRANSFER', 1099.99, 'SUCCESS', '2023-04-15 15:10', 'TXN-0007'),
(8,  'CARD',           479.97, 'SUCCESS', '2023-05-01 10:05', 'TXN-0008'),
(9,  'UPI',            159.98, 'SUCCESS', '2023-05-18 09:35', 'TXN-0009'),
(10, 'CARD',           359.97, 'SUCCESS', '2023-06-10 16:05', 'TXN-0010'),
(11, 'WALLET',         269.98, 'SUCCESS', '2023-07-04 10:05', 'TXN-0011'),
(12, 'CARD',            59.96, 'SUCCESS', '2023-07-22 11:05', 'TXN-0012'),
(13, 'CARD',           589.98, 'SUCCESS', '2023-08-08 09:05', 'TXN-0013'),
(14, 'UPI',            749.97, 'SUCCESS', '2023-08-20 14:05', 'TXN-0014'),
(15, 'CARD',           199.99, 'SUCCESS', '2023-09-05 10:35', 'TXN-0015'),
(16, 'CARD',          1289.98, 'SUCCESS', '2023-10-10 12:05', 'TXN-0016'),
(17, 'BANK_TRANSFER', 1199.97, 'SUCCESS', '2023-10-25 09:05', 'TXN-0017'),
(18, 'CARD',           649.98, 'SUCCESS', '2023-11-08 15:05', 'TXN-0018'),
(19, 'WALLET',         859.97, 'SUCCESS', '2023-11-20 10:05', 'TXN-0019'),
(20, 'UPI',            339.97, 'SUCCESS', '2023-12-02 11:05', 'TXN-0020'),
(21, 'CARD',          1799.99, 'SUCCESS', '2023-12-15 09:05', 'TXN-0021'),
(22, 'CARD',            82.95, 'SUCCESS', '2023-12-28 14:05', 'TXN-0022'),
(23, 'CARD',          1399.98, 'SUCCESS', '2024-01-05 10:05', 'TXN-0023'),
(24, 'BANK_TRANSFER', 1133.97, 'SUCCESS', '2024-01-18 09:05', 'TXN-0024'),
(25, 'CARD',           799.99, 'FAILED',  '2024-01-22 11:05', 'TXN-0025'),
(26, 'UPI',            389.98, 'SUCCESS', '2024-02-06 14:05', 'TXN-0026'),
(27, 'CARD',           219.97, 'SUCCESS', '2024-02-18 10:05', 'TXN-0027'),
(28, 'WALLET',         269.98, 'SUCCESS', '2024-03-07 09:35', 'TXN-0028'),
(29, 'CARD',           529.98, 'SUCCESS', '2024-03-20 15:05', 'TXN-0029'),
(30, 'UPI',            249.99, 'SUCCESS', '2024-04-03 11:05', 'TXN-0030'),
(31, 'CARD',           479.97, 'SUCCESS', '2024-04-18 10:05', 'TXN-0031'),
(32, 'CARD',          1849.98, 'SUCCESS', '2024-05-02 09:05', 'TXN-0032'),
(33, 'BANK_TRANSFER',  999.98, 'SUCCESS', '2024-05-15 14:05', 'TXN-0033'),
(34, 'UPI',           1099.99, 'SUCCESS', '2024-06-01 10:35', 'TXN-0034'),
(35, 'CARD',          1289.98, 'SUCCESS', '2024-06-20 11:05', 'TXN-0035'),
(36, 'WALLET',         339.97, 'SUCCESS', '2024-07-05 09:05', 'TXN-0036'),
(37, 'CARD',           269.98, 'SUCCESS', '2024-07-19 14:05', 'TXN-0037'),
(38, 'UPI',            309.98, 'SUCCESS', '2024-08-02 10:05', 'TXN-0038'),
(39, 'CARD',          1799.99, 'PENDING', NULL,               'TXN-0039'),
(40, 'BANK_TRANSFER', 1116.98, 'PENDING', NULL,               'TXN-0040'),
(41, 'COD',            499.99, 'PENDING', NULL,               'TXN-0041');

-- ─────────────────────────────────────────
-- REFUNDS  (a few realistic refunds)
-- ─────────────────────────────────────────
INSERT INTO refunds (payment_id, amount, reason, created_at) VALUES
(3,  799.99, 'Customer changed mind',         '2023-02-12 10:00'),
(9,  159.98, 'Item arrived damaged',          '2023-05-25 14:00'),
(14, 349.99, 'Wrong item shipped',            '2023-08-28 09:00'),
(25, 799.99, 'Payment failed, auto-refund',   '2024-01-23 08:00');

-- ─────────────────────────────────────────
-- SHIPMENTS
-- ─────────────────────────────────────────
INSERT INTO shipments (order_id, carrier, tracking_no, shipped_at, estimated_at, delivered_at, status) VALUES
(1,  'FedEx',  'FX-00001', '2023-01-21', '2023-01-25', '2023-01-25', 'DELIVERED'),
(2,  'UPS',    'UP-00002', '2023-01-29', '2023-02-02', '2023-02-02', 'DELIVERED'),
(3,  'DHL',    'DH-00003', '2023-02-06', '2023-02-10', '2023-02-10', 'DELIVERED'),
(4,  'FedEx',  'FX-00004', '2023-02-15', '2023-02-19', '2023-02-19', 'DELIVERED'),
(5,  'UPS',    'UP-00005', '2023-02-23', '2023-02-28', '2023-02-28', 'DELIVERED'),
(6,  'FedEx',  'FX-00006', '2023-04-04', '2023-04-08', '2023-04-08', 'DELIVERED'),
(7,  'DHL',    'DH-00007', '2023-04-16', '2023-04-20', '2023-04-20', 'DELIVERED'),
(8,  'FedEx',  'FX-00008', '2023-05-02', '2023-05-06', '2023-05-06', 'DELIVERED'),
(9,  'UPS',    'UP-00009', '2023-05-19', '2023-05-23', '2023-05-23', 'DELIVERED'),
(10, 'FedEx',  'FX-00010', '2023-06-11', '2023-06-15', '2023-06-15', 'DELIVERED'),
(11, 'DHL',    'DH-00011', '2023-07-05', '2023-07-10', '2023-07-10', 'DELIVERED'),
(12, 'FedEx',  'FX-00012', '2023-07-23', '2023-07-28', '2023-07-28', 'DELIVERED'),
(13, 'UPS',    'UP-00013', '2023-08-09', '2023-08-14', '2023-08-14', 'DELIVERED'),
(14, 'FedEx',  'FX-00014', '2023-08-21', '2023-08-26', '2023-08-26', 'DELIVERED'),
(15, 'DHL',    'DH-00015', '2023-09-06', '2023-09-11', '2023-09-11', 'DELIVERED'),
(16, 'FedEx',  'FX-00016', '2023-10-11', '2023-10-16', '2023-10-16', 'DELIVERED'),
(17, 'UPS',    'UP-00017', '2023-10-26', '2023-10-31', '2023-10-31', 'DELIVERED'),
(18, 'DHL',    'DH-00018', '2023-11-09', '2023-11-14', '2023-11-14', 'DELIVERED'),
(19, 'FedEx',  'FX-00019', '2023-11-21', '2023-11-26', '2023-11-26', 'DELIVERED'),
(20, 'UPS',    'UP-00020', '2023-12-03', '2023-12-08', '2023-12-08', 'DELIVERED'),
(21, 'FedEx',  'FX-00021', '2023-12-16', '2023-12-21', '2023-12-21', 'DELIVERED'),
(22, 'DHL',    'DH-00022', '2023-12-29', '2024-01-03', '2024-01-03', 'DELIVERED'),
(23, 'FedEx',  'FX-00023', '2024-01-06', '2024-01-11', '2024-01-11', 'DELIVERED'),
(24, 'UPS',    'UP-00024', '2024-01-19', '2024-01-24', '2024-01-24', 'DELIVERED'),
(26, 'DHL',    'DH-00026', '2024-02-07', '2024-02-12', '2024-02-12', 'DELIVERED'),
(27, 'FedEx',  'FX-00027', '2024-02-19', '2024-02-24', '2024-02-24', 'DELIVERED'),
(28, 'UPS',    'UP-00028', '2024-03-08', '2024-03-13', '2024-03-13', 'DELIVERED'),
(29, 'FedEx',  'FX-00029', '2024-03-21', '2024-03-26', '2024-03-26', 'DELIVERED'),
(30, 'DHL',    'DH-00030', '2024-04-04', '2024-04-09', '2024-04-09', 'DELIVERED'),
(31, 'FedEx',  'FX-00031', '2024-04-19', '2024-04-24', '2024-04-24', 'DELIVERED'),
(32, 'UPS',    'UP-00032', '2024-05-03', '2024-05-08', '2024-05-08', 'DELIVERED'),
(33, 'FedEx',  'FX-00033', '2024-05-16', '2024-05-21', '2024-05-21', 'DELIVERED'),
(34, 'DHL',    'DH-00034', '2024-06-02', '2024-06-07', '2024-06-07', 'DELIVERED'),
(35, 'FedEx',  'FX-00035', '2024-06-21', '2024-06-26', '2024-06-26', 'DELIVERED'),
(36, 'UPS',    'UP-00036', '2024-07-06', '2024-07-11', '2024-07-11', 'DELIVERED'),
(37, 'DHL',    'DH-00037', '2024-07-20', '2024-07-25', '2024-07-25', 'DELIVERED'),
(38, 'FedEx',  'FX-00038', '2024-08-03', '2024-08-08', '2024-08-08', 'DELIVERED'),
(39, 'UPS',    'UP-00039', '2024-08-16', '2024-08-22',  NULL,        'IN_TRANSIT'),
(40, 'DHL',    'DH-00040',  NULL,         NULL,          NULL,        'PREPARING');

-- ─────────────────────────────────────────
-- PRODUCT REVIEWS
-- ─────────────────────────────────────────
INSERT INTO product_reviews (product_id, user_id, rating, body, created_at) VALUES
(1,  1, 5, 'Excellent laptop, super fast!',            '2023-01-30'),
(1,  2, 4, 'Great value but runs warm.',               '2023-07-01'),
(2,  6, 5, 'Best laptop I have ever owned.',           '2023-05-01'),
(4,  3, 4, 'Good phone, camera is impressive.',        '2023-02-15'),
(4,  8, 3, 'Battery drains faster than expected.',     '2023-06-20'),
(7,  1, 5, 'Perfect wireless mouse!',                  '2023-02-01'),
(8,  2, 4, 'Great keyboard, a bit loud.',              '2023-02-10'),
(10, 5, 5, 'Amazing noise cancellation.',              '2023-03-05'),
(11, 4, 4, 'Works great, easy to set up.',             '2023-02-25'),
(12, 7, 5, 'Worth every penny.',                       '2023-05-10'),
(15, 9, 5, 'Best yoga mat, great grip.',               '2024-01-15'),
(16, 2, 4, 'Heavy but effective.',                     '2023-06-25'),
(18, 9, 5, 'Tent set up in 10 minutes!',               '2023-07-15'),
(20, 12, 4,'Great story, a bit slow start.',           '2023-08-05'),
(22, 5, 5, 'Life changing book.',                      '2023-03-10'),
(23, 9, 4, 'Insightful and concise.',                  '2024-01-05');

-- ─────────────────────────────────────────
-- SUPPORT TICKETS
-- ─────────────────────────────────────────
INSERT INTO support_tickets (user_id, order_id, subject, status, priority, created_at, resolved_at) VALUES
(3,  3,  'Wrong item shipped',            'RESOLVED', 'HIGH',   '2023-02-11', '2023-02-13'),
(5,  9,  'Item arrived damaged',          'RESOLVED', 'HIGH',   '2023-05-24', '2023-05-26'),
(9, 14,  'Refund not received',           'RESOLVED', 'MEDIUM', '2023-08-27', '2023-08-30'),
(1, 13,  'Where is my order?',            'RESOLVED', 'LOW',    '2023-08-12', '2023-08-13'),
(13,25,  'Payment failed but charged',    'RESOLVED', 'HIGH',   '2024-01-23', '2024-01-24'),
(7, 21,  'Delivery took too long',        'CLOSED',   'LOW',    '2023-12-22', '2023-12-28'),
(11,31,  'Product stopped working',       'IN_PROGRESS','HIGH', '2024-04-25',  NULL),
(14,27,  'Wrong size delivered',          'OPEN',     'MEDIUM', '2024-02-25',  NULL),
(15,28,  'Tracking not updating',         'OPEN',     'LOW',    '2024-03-09',  NULL),
(8, 39,  'Payment still pending',         'OPEN',     'HIGH',   '2024-08-17',  NULL);