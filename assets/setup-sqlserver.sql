-- 先创建空的 SQLNotesLab 数据库，再用 sqlcmd -b -d SQLNotesLab -f i:65001 -i assets/setup-sqlserver.sql。
SET NOCOUNT ON;
SET XACT_ABORT ON;
IF DB_NAME() <> N'SQLNotesLab'
    THROW 50001, N'请连接专用的 SQLNotesLab 练习数据库。', 1;
IF OBJECT_ID(N'dbo.customers', N'U') IS NOT NULL
    THROW 50002, N'练习表已存在。请先确认现有数据。', 1;

BEGIN TRANSACTION;
CREATE TABLE dbo.customers (
  customer_id int PRIMARY KEY,
  name nvarchar(40) NOT NULL,
  city nvarchar(40)
);

CREATE TABLE dbo.products (
  product_id int PRIMARY KEY,
  name nvarchar(60) NOT NULL,
  category varchar(30) NOT NULL,
  price decimal(8,2) NOT NULL CHECK (price >= 0),
  listed_on date NOT NULL
);

CREATE TABLE dbo.orders (
  order_id int PRIMARY KEY,
  customer_id int NOT NULL REFERENCES dbo.customers (customer_id),
  ordered_on date NOT NULL,
  status varchar(12) NOT NULL
);

CREATE TABLE dbo.order_items (
  order_id int NOT NULL REFERENCES dbo.orders (order_id),
  product_id int NOT NULL REFERENCES dbo.products (product_id),
  qty int NOT NULL CHECK (qty > 0),
  unit_price decimal(8,2) NOT NULL,
  PRIMARY KEY (order_id, product_id)
);

CREATE TABLE dbo.docs (
  doc_id int IDENTITY(1,1) CONSTRAINT pk_notes_docs PRIMARY KEY,
  title nvarchar(80) NOT NULL,
  body nvarchar(max) NOT NULL
);

INSERT INTO dbo.customers (customer_id, name, city) VALUES
  (1, N'Ana', N'北京'), (2, N'Bo', N'上海'), (3, N'Chen', NULL), (4, N'Dina', N'北京');

INSERT INTO dbo.products (product_id, name, category, price, listed_on) VALUES
  (1, N'SQL Basics', 'book', 20.00, '20250110'),
  (2, N'SQL Practice', 'book', 30.00, '20250201'),
  (3, N'Notebook', 'stationery', 10.00, '20250201'),
  (4, N'Pen', 'stationery', 5.00, '20250301'),
  (5, N'SQLX', 'book', 30.00, '20250301');

INSERT INTO dbo.orders (order_id, customer_id, ordered_on, status) VALUES
  (101, 1, '20250110', 'paid'), (102, 2, '20250201', 'pending'),
  (103, 1, '20250202', 'paid'), (104, 3, '20250202', 'paid');

INSERT INTO dbo.order_items (order_id, product_id, qty, unit_price) VALUES
  (101, 1, 2, 20.00), (101, 4, 1, 5.00), (102, 2, 1, 30.00),
  (103, 3, 3, 10.00), (104, 1, 1, 20.00);

INSERT INTO dbo.docs (title, body) VALUES
  (N'SQL Introduction', N'Database queries and relational tables'),
  (N'SQL Workshop', N'Practice joins and database queries'),
  (N'Paper Notebook', N'Stationery supplies for handwriting'),
  (N'Database Design', N'Relational schemas and primary keys'),
  (N'Join Recipe', N'Practice joins with order examples');
COMMIT TRANSACTION;
