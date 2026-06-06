CREATE DATABASE IF NOT EXISTS telesupport_hub;
USE telesupport_hub;

CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    mobile VARCHAR(20) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(120) NOT NULL,
    address VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS agents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(120) NOT NULL
);

CREATE TABLE IF NOT EXISTS purchases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    description TEXT NOT NULL,
    plan_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    status VARCHAR(30) DEFAULT 'Open',
    date_raised TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- Default agent account
INSERT INTO agents (name, email, password)
SELECT 'Support Agent', 'agent@telesupport.com', 'agent123'
WHERE NOT EXISTS (SELECT 1 FROM agents WHERE email = 'agent@telesupport.com');

-- Default customer account - Prajyot
INSERT INTO customers (name, mobile, email, password, address)
SELECT 'Prajyot', '9876543210', 'prajyot2017@gmail.com', 'pass123', 'Pune, Maharashtra'
WHERE NOT EXISTS (SELECT 1 FROM customers WHERE email = 'prajyot2017@gmail.com');
