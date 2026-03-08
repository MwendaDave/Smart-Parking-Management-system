-- Seed data for testing
USE smart_parking;

-- Insert parking slots
INSERT INTO parking_slots (slot_number, location, hourly_rate) VALUES
('A1', 'Ground Floor - Zone A', 50.00),
('A2', 'Ground Floor - Zone A', 50.00),
('A3', 'Ground Floor - Zone A', 50.00),
('B1', 'First Floor - Zone B', 40.00),
('B2', 'First Floor - Zone B', 40.00),
('C1', 'Basement - Zone C', 60.00);

-- Insert admin (password: admin123)
INSERT INTO users (full_name, email, phone, password_hash, role) VALUES
('System Administrator', 'admin@smartparking.com', '0700000000', 
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G', 'admin');

-- Insert test driver (password: driver123)
INSERT INTO users (full_name, email, phone, password_hash, role) VALUES
('Test Driver', 'driver@test.com', '0712345678', 
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G', 'driver');