-- 仅在练习实例执行。若库名已存在，脚本在第一句停止。
CREATE DATABASE learn_sql_lab CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE learn_sql_lab;

CREATE TABLE customers (
  customer_id INT PRIMARY KEY,
  name VARCHAR(40) NOT NULL,
  city VARCHAR(40)
) ENGINE=InnoDB;

CREATE TABLE products (
  product_id INT PRIMARY KEY,
  name VARCHAR(60) NOT NULL,
  category VARCHAR(30) NOT NULL,
  price DECIMAL(8,2) NOT NULL,
  listed_on DATE NOT NULL,
  CONSTRAINT ck_products_price CHECK (price >= 0)
) ENGINE=InnoDB;

CREATE TABLE orders (
  order_id INT PRIMARY KEY,
  customer_id INT NOT NULL,
  ordered_on DATE NOT NULL,
  status VARCHAR(12) NOT NULL,
  CONSTRAINT fk_orders_customer
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
) ENGINE=InnoDB;

CREATE TABLE order_items (
  order_id INT NOT NULL,
  product_id INT NOT NULL,
  qty INT NOT NULL CHECK (qty > 0),
  unit_price DECIMAL(8,2) NOT NULL,
  PRIMARY KEY (order_id, product_id),
  CONSTRAINT fk_items_order FOREIGN KEY (order_id) REFERENCES orders (order_id),
  CONSTRAINT fk_items_product
    FOREIGN KEY (product_id) REFERENCES products (product_id)
) ENGINE=InnoDB;

CREATE TABLE docs (
  doc_id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(80) NOT NULL,
  body TEXT NOT NULL,
  FULLTEXT KEY ft_docs_title_body (title, body)
) ENGINE=InnoDB;

INSERT INTO customers (customer_id, name, city) VALUES
  (1, 'Ana', '北京'), (2, 'Bo', '上海'), (3, 'Chen', NULL), (4, 'Dina', '北京');

INSERT INTO products (product_id, name, category, price, listed_on) VALUES
  (1, 'SQL Basics', 'book', 20.00, '2025-01-10'),
  (2, 'SQL Practice', 'book', 30.00, '2025-02-01'),
  (3, 'Notebook', 'stationery', 10.00, '2025-02-01'),
  (4, 'Pen', 'stationery', 5.00, '2025-03-01'),
  (5, 'SQLX', 'book', 30.00, '2025-03-01');

INSERT INTO orders (order_id, customer_id, ordered_on, status) VALUES
  (101, 1, '2025-01-10', 'paid'), (102, 2, '2025-02-01', 'pending'),
  (103, 1, '2025-02-02', 'paid'), (104, 3, '2025-02-02', 'paid');

INSERT INTO order_items (order_id, product_id, qty, unit_price) VALUES
  (101, 1, 2, 20.00), (101, 4, 1, 5.00), (102, 2, 1, 30.00),
  (103, 3, 3, 10.00), (104, 1, 1, 20.00);

INSERT INTO docs (title, body) VALUES
  ('SQL Introduction', 'Database queries and relational tables'),
  ('SQL Workshop', 'Practice joins and database queries'),
  ('Paper Notebook', 'Stationery supplies for handwriting'),
  ('Database Design', 'Relational schemas and primary keys'),
  ('Join Recipe', 'Practice joins with order examples');
