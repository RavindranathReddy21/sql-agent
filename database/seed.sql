INSERT INTO users (name, email) VALUES
('Alice', 'alice@example.com'),
('Bob', 'bob@example.com'),
('Charlie', 'charlie@example.com');

INSERT INTO products (name, price, stock) VALUES
('Laptop', 1200.00, 10),
('Mouse', 25.00, 100),
('Keyboard', 45.00, 50);

INSERT INTO orders (user_id) VALUES
(1),
(2),
(1);

INSERT INTO order_items (order_id, product_id, quantity) VALUES
(1, 1, 1),
(1, 2, 2),
(2, 3, 1),
(3, 2, 3);

INSERT INTO payments (order_id, amount, status) VALUES
(1, 1250.00, 'SUCCESS'),
(2, 45.00, 'SUCCESS'),
(3, 75.00, 'PENDING');
