CREATE DATABASE IF NOT EXISTS hms_db;
USE hms_db;

CREATE TABLE `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(50) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `role` ENUM('Admin', 'Doctor', 'Receptionist', 'Pharmacist', 'Lab Tech') NOT NULL
);

CREATE TABLE `doctors` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `specialization` VARCHAR(100),
  `contact` VARCHAR(20),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
);

CREATE TABLE `rooms` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `room_number` VARCHAR(10) NOT NULL UNIQUE,
  `type` ENUM('General', 'Private', 'ICU') NOT NULL,
  `is_available` BOOLEAN DEFAULT TRUE
);

CREATE TABLE `patients` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `age` INT,
  `gender` ENUM('Male', 'Female', 'Other'),
  `address` VARCHAR(255),
  `contact` VARCHAR(20),
  `doctor_id` INT,
  `room_id` INT,
  `admission_date` DATETIME NOT NULL,
  `discharge_date` DATETIME,
  FOREIGN KEY (`doctor_id`) REFERENCES `doctors`(`id`),
  FOREIGN KEY (`room_id`) REFERENCES `rooms`(`id`)
);

CREATE TABLE `appointments` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `patient_id` INT NOT NULL,
  `doctor_id` INT NOT NULL,
  `appointment_time` DATETIME NOT NULL,
  `status` ENUM('Scheduled', 'Completed', 'Canceled') DEFAULT 'Scheduled',
  FOREIGN KEY (`patient_id`) REFERENCES `patients`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`doctor_id`) REFERENCES `doctors`(`id`) ON DELETE CASCADE
);

CREATE TABLE `medicines` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL UNIQUE,
  `smiles` TEXT,
  `image_path` VARCHAR(255),
  `quantity` INT NOT NULL DEFAULT 0,
  `expiry_date` DATE,
  `price` DECIMAL(10, 2) NOT NULL
);

CREATE TABLE `medicine_issued` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `patient_id` INT NOT NULL,
  `medicine_id` INT NOT NULL,
  `quantity` INT NOT NULL,
  `issue_date` DATETIME NOT NULL,
  FOREIGN KEY (`patient_id`) REFERENCES `patients`(`id`),
  FOREIGN KEY (`medicine_id`) REFERENCES `medicines`(`id`)
);

CREATE TABLE `lab_tests` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL UNIQUE,
  `price` DECIMAL(10, 2) NOT NULL
);

-- 9. Lab Reports Table
CREATE TABLE `lab_reports` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `patient_id` INT NOT NULL,
  `test_id` INT NOT NULL,
  `result` TEXT,
  `report_date` DATETIME NOT NULL,
  FOREIGN KEY (`patient_id`) REFERENCES `patients`(`id`),
  FOREIGN KEY (`test_id`) REFERENCES `lab_tests`(`id`)
);

-- 10. Bills Table
CREATE TABLE `bills` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `patient_id` INT NOT NULL,
  `total_amount` DECIMAL(10, 2) NOT NULL,
  `payment_status` ENUM('Paid', 'Unpaid') DEFAULT 'Unpaid',
  `bill_date` DATETIME NOT NULL,
  FOREIGN KEY (`patient_id`) REFERENCES `patients`(`id`)
);

INSERT INTO `users` (`username`, `password_hash`, `role`) VALUES ('admin', '$2b$12$j9webUJQ5jmt5h5US4hUeeavTUsy8WfNlLGcFdt9s0QyPNWmQ63Ja', 'Admin');