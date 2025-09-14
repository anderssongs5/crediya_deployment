USE authenticacion_db;

INSERT INTO roles (name, description) VALUES
    ('ADMIN', 'Administrator with full system access.'),
    ('ADVISOR', 'Advises clients on a variety of topics.'),
    ('CLIENT', 'Client');

INSERT INTO users (id, name, last_name, identity_number, address, phone_number, birth_date, email, base_salary, password, role_id) 
VALUES (UUID(), 'Andersson', 'Garcia Sotelo', '123456789', 'Cra 60 # 30-12', '78385750', '1992-10-22', 'admin@gmail.com', 10500000, '$2a$12$mTYs31CPYB9e44dqqW5BJ.8POkTMJm61WA2TzLCGYt0QqtsWiE1iK', '1');