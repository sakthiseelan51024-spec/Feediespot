-- =============================================
--  FOODIE SPOT — College Canteen DB Schema
-- =============================================
CREATE DATABASE IF NOT EXISTS canteen_db;
USE canteen_db;

CREATE TABLE IF NOT EXISTS admins (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  username   VARCHAR(50)  NOT NULL UNIQUE,
  password   VARCHAR(255) NOT NULL,
  full_name  VARCHAR(100) DEFAULT 'Canteen Admin',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admin login: username=admin  password=admin123
INSERT IGNORE INTO admins (username, password, full_name)
VALUES ('admin', 'admin123', 'Canteen Admin');

CREATE TABLE IF NOT EXISTS menu_items (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  name         VARCHAR(150) NOT NULL,
  price        DECIMAL(8,2) NOT NULL,
  category     ENUM('morning','break','lunch') NOT NULL,
  description  VARCHAR(255) DEFAULT '',
  is_available TINYINT(1)   DEFAULT 1,
  created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  token_number  VARCHAR(20)  NOT NULL UNIQUE,
  customer_name VARCHAR(100) DEFAULT 'Guest',
  total_amount  DECIMAL(8,2) NOT NULL,
  status        ENUM('pending','preparing','ready','completed','cancelled') DEFAULT 'pending',
  time_slot     ENUM('morning','break','lunch') NOT NULL,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  order_id     INT           NOT NULL,
  menu_item_id INT           NOT NULL,
  item_name    VARCHAR(150)  NOT NULL,
  quantity     INT           NOT NULL DEFAULT 1,
  unit_price   DECIMAL(8,2) NOT NULL,
  FOREIGN KEY (order_id)     REFERENCES orders(id)     ON DELETE CASCADE,
  FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE RESTRICT
);

-- Sample Menu
INSERT IGNORE INTO menu_items (id,name,price,category,description) VALUES
(1,  'Idli (2 pcs)',      20.00,'morning','Soft idli with sambar & coconut chutney'),
(2,  'Plain Dosa',        30.00,'morning','Crispy dosa with sambar & chutney'),
(3,  'Masala Dosa',       40.00,'morning','Dosa with spiced potato filling'),
(4,  'Pongal',            25.00,'morning','Ven pongal with ghee & sambar'),
(5,  'Upma',              20.00,'morning','Rava upma with vegetables'),
(6,  'Tea',               10.00,'morning','Hot kadak chai'),
(7,  'Filter Coffee',     15.00,'morning','South Indian filter coffee'),
(8,  'Vada (2 pcs)',      20.00,'break',  'Crispy medu vada with sambar'),
(9,  'Samosa (2 pcs)',    15.00,'break',  'Crispy vegetable samosa'),
(10, 'Puffs',             15.00,'break',  'Flaky pastry with veg/egg filling'),
(11, 'Bread Omelette',    30.00,'break',  'Egg omelette with toasted bread'),
(12, 'Fruit Juice',       25.00,'break',  'Fresh seasonal fruit juice'),
(13, 'Cool Drink',        20.00,'break',  '250ml cold beverage'),
(14, 'Full Meals',        70.00,'lunch',  'Rice + sambar + rasam + 2 curries + papad + curd'),
(15, 'Mini Meals',        50.00,'lunch',  'Rice + sambar + 1 curry + papad'),
(16, 'Chapati (3 pcs)',   35.00,'lunch',  'Soft chapati with dal / kurma'),
(17, 'Veg Fried Rice',    50.00,'lunch',  'Wok-tossed vegetable fried rice'),
(18, 'Egg Fried Rice',    60.00,'lunch',  'Fried rice with scrambled egg'),
(19, 'Veg Noodles',       45.00,'lunch',  'Stir-fried hakka noodles'),
(20, 'Curd Rice',         30.00,'lunch',  'Creamy curd rice with pickle'),
(21, 'Lemon Rice',        30.00,'lunch',  'Tangy tempered lemon rice');
