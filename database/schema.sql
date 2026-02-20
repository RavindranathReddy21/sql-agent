PRAGMA foreign_keys = ON;

-- ─────────────────────────────────────────
-- REFERENCE / LOOKUP TABLES
-- ─────────────────────────────────────────

CREATE TABLE categories (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL UNIQUE,
    parent_id INTEGER REFERENCES categories(id)   -- supports sub-categories
);

CREATE TABLE regions (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL,
    country TEXT NOT NULL
);

-- ─────────────────────────────────────────
-- USERS & ADDRESSES
-- ─────────────────────────────────────────

CREATE TABLE users (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL,
    email        TEXT UNIQUE NOT NULL,
    phone        TEXT,
    region_id    INTEGER REFERENCES regions(id),
    created_at   TEXT DEFAULT CURRENT_TIMESTAMP,
    is_active    INTEGER DEFAULT 1       -- 0 = deactivated
);

CREATE TABLE addresses (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    label      TEXT DEFAULT 'home',      -- home / work / other
    street     TEXT NOT NULL,
    city       TEXT NOT NULL,
    state      TEXT,
    zip        TEXT,
    country    TEXT NOT NULL,
    is_default INTEGER DEFAULT 0
);

-- ─────────────────────────────────────────
-- SELLERS / VENDORS
-- ─────────────────────────────────────────

CREATE TABLE sellers (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    email      TEXT UNIQUE NOT NULL,
    region_id  INTEGER REFERENCES regions(id),
    rating     REAL DEFAULT 5.0,
    joined_at  TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
-- PRODUCTS
-- ─────────────────────────────────────────

CREATE TABLE products (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id    INTEGER NOT NULL REFERENCES sellers(id),
    category_id  INTEGER NOT NULL REFERENCES categories(id),
    name         TEXT NOT NULL,
    description  TEXT,
    price        REAL NOT NULL,
    cost         REAL NOT NULL,           -- for margin analysis
    stock        INTEGER NOT NULL DEFAULT 0,
    sku          TEXT UNIQUE,
    is_active    INTEGER DEFAULT 1,
    created_at   TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE product_reviews (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id  INTEGER NOT NULL REFERENCES products(id),
    user_id     INTEGER NOT NULL REFERENCES users(id),
    rating      INTEGER CHECK(rating BETWEEN 1 AND 5),
    body        TEXT,
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
-- PROMOTIONS / COUPONS
-- ─────────────────────────────────────────

CREATE TABLE promotions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    code            TEXT UNIQUE NOT NULL,
    discount_type   TEXT CHECK(discount_type IN ('PERCENT','FIXED')) NOT NULL,
    discount_value  REAL NOT NULL,
    min_order_value REAL DEFAULT 0,
    valid_from      TEXT NOT NULL,
    valid_until     TEXT NOT NULL,
    usage_limit     INTEGER DEFAULT 100,
    times_used      INTEGER DEFAULT 0
);

-- ─────────────────────────────────────────
-- ORDERS
-- ─────────────────────────────────────────

CREATE TABLE orders (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(id),
    address_id      INTEGER REFERENCES addresses(id),
    promotion_id    INTEGER REFERENCES promotions(id),
    status          TEXT CHECK(status IN ('PENDING','CONFIRMED','SHIPPED','DELIVERED','CANCELLED')) DEFAULT 'PENDING',
    order_date      TEXT DEFAULT CURRENT_TIMESTAMP,
    delivered_at    TEXT,
    notes           TEXT
);

CREATE TABLE order_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id    INTEGER NOT NULL REFERENCES orders(id),
    product_id  INTEGER NOT NULL REFERENCES products(id),
    quantity    INTEGER NOT NULL,
    unit_price  REAL NOT NULL       -- snapshot of price at time of order
);

-- ─────────────────────────────────────────
-- PAYMENTS & REFUNDS
-- ─────────────────────────────────────────

CREATE TABLE payments (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id       INTEGER NOT NULL REFERENCES orders(id),
    method         TEXT CHECK(method IN ('CARD','UPI','WALLET','COD','BANK_TRANSFER')) NOT NULL,
    amount         REAL NOT NULL,
    status         TEXT CHECK(status IN ('PENDING','SUCCESS','FAILED','REFUNDED')) DEFAULT 'PENDING',
    paid_at        TEXT,
    transaction_id TEXT UNIQUE
);

CREATE TABLE refunds (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_id  INTEGER NOT NULL REFERENCES payments(id),
    amount      REAL NOT NULL,
    reason      TEXT,
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
-- SHIPPING
-- ─────────────────────────────────────────

CREATE TABLE shipments (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id       INTEGER NOT NULL REFERENCES orders(id),
    carrier        TEXT,
    tracking_no    TEXT UNIQUE,
    shipped_at     TEXT,
    estimated_at   TEXT,
    delivered_at   TEXT,
    status         TEXT CHECK(status IN ('PREPARING','IN_TRANSIT','DELIVERED','RETURNED')) DEFAULT 'PREPARING'
);

-- ─────────────────────────────────────────
-- SUPPORT TICKETS
-- ─────────────────────────────────────────

CREATE TABLE support_tickets (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    order_id    INTEGER REFERENCES orders(id),
    subject     TEXT NOT NULL,
    status      TEXT CHECK(status IN ('OPEN','IN_PROGRESS','RESOLVED','CLOSED')) DEFAULT 'OPEN',
    priority    TEXT CHECK(priority IN ('LOW','MEDIUM','HIGH')) DEFAULT 'MEDIUM',
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
    resolved_at TEXT
);