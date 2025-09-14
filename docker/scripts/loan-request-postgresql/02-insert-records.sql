INSERT INTO loan_request_statuses (name, description) VALUES
('PENDING', 'Request submitted and pending review'),
('UNDER_REVIEW', 'Request is being evaluated'),
('APPROVED', 'Request has been approved'),
('REJECTED', 'Request has been rejected'),
('DISBURSED', 'Loan amount has been disbursed'),
('CANCELLED', 'Request was cancelled by user'),
('MANUAL_REVIEW', 'Request requires manual review');

INSERT INTO loan_types (name, minimum_amount, maximum_amount, minimum_term, maximum_term, interest_rate, automatic_validation) VALUES
('PERSONAL_LOAN', 1000.00, 50000.00, 6, 60, 0.1250, FALSE),
('HOME_LOAN', 50000.00, 500000.00, 120, 360, 0.0875, FALSE),
('AUTO_LOAN', 5000.00, 100000.00, 12, 84, 0.0950, TRUE),
('BUSINESS_LOAN', 10000.00, 1000000.00, 12, 120, 0.1150, FALSE),
('STUDENT_LOAN', 500.00, 25000.00, 6, 120, 0.0650, TRUE),
('QUICK_LOAN', 100.00, 5000.00, 1, 12, 0.1850, TRUE);