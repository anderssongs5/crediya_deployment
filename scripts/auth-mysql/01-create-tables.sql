-- Script to create the users table in MySQL
-- Database: authenticacion_db

CREATE DATABASE IF NOT EXISTS authenticacion_db;
USE authenticacion_db;


CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_name (name)
);

ALTER TABLE roles COMMENT = 'Table that stores roles';


CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    identity_number VARCHAR(50) NOT NULL,
    address TEXT,
    phone_number VARCHAR(20) NOT NULL,
    birth_date DATE NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    base_salary DECIMAL(10,2) NOT NULL CHECK (base_salary >= 0 AND base_salary <= 15000000.00),
    password VARCHAR(200) NOT NULL,
    role_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_email (email),
    INDEX idx_identity_number (identity_number),
    INDEX idx_email_identity_number (email, identity_number),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

-- Comments about the table
ALTER TABLE users COMMENT = 'Table that stores user information for the authentication system';
