CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE loan_request_statuses (
    status_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);


CREATE TABLE loan_types (
    loan_type_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    minimum_amount NUMERIC(12, 2) NOT NULL,
    maximum_amount NUMERIC(12, 2) NOT NULL,
    minimum_term INTEGER NOT NULL,
    maximum_term INTEGER NOT NULL,
    interest_rate NUMERIC(5, 2) NOT NULL,
    automatic_validation BOOLEAN NOT NULL
);


CREATE TABLE loan_requests (
    request_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    amount NUMERIC(12, 2) NOT NULL,
    term INTEGER NOT NULL,
    email VARCHAR(255) NOT NULL,
    status_id INTEGER NOT NULL,
    loan_type_id INTEGER NOT NULL,
    FOREIGN KEY (status_id) REFERENCES loan_request_statuses(status_id),
    FOREIGN KEY (loan_type_id) REFERENCES loan_types(loan_type_id)
);

