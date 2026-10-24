CREATE DATABASE IF NOT EXISTS `library_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `library_db`;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `reservations`;
DROP TABLE IF EXISTS `borrow_records`;
DROP TABLE IF EXISTS `books`;
DROP TABLE IF EXISTS `categories`;
DROP TABLE IF EXISTS `users`;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id_number` VARCHAR(50) NOT NULL UNIQUE,
    `full_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NOT NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL,
    `role` ENUM('librarian', 'student') NOT NULL DEFAULT 'student',
    `course_year` VARCHAR(100) DEFAULT NULL,
    `contact_number` VARCHAR(30) DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `categories` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL UNIQUE,
    `description` VARCHAR(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `books` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `isbn` VARCHAR(30) NOT NULL UNIQUE,
    `title` VARCHAR(255) NOT NULL,
    `author` VARCHAR(150) NOT NULL,
    `category_id` INT NOT NULL,
    `total_copies` INT NOT NULL DEFAULT 1,
    `available_copies` INT NOT NULL DEFAULT 1,
    `shelf_location` VARCHAR(50) DEFAULT 'Section A-1',
    `description` TEXT DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_books_category` FOREIGN KEY (`category_id`) 
        REFERENCES `categories` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `borrow_records` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `book_id` INT NOT NULL,
    `borrow_date` DATE NOT NULL,
    `due_date` DATE NOT NULL,
    `return_date` DATE DEFAULT NULL,
    `fine_amount` DECIMAL(8, 2) NOT NULL DEFAULT 0.00,
    `fine_paid` TINYINT(1) NOT NULL DEFAULT 0,
    `status` ENUM('borrowed', 'returned', 'overdue') NOT NULL DEFAULT 'borrowed',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_borrow_user` FOREIGN KEY (`user_id`) 
        REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_borrow_book` FOREIGN KEY (`book_id`) 
        REFERENCES `books` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `reservations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `book_id` INT NOT NULL,
    `reservation_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `status` ENUM('pending', 'approved', 'cancelled', 'completed') NOT NULL DEFAULT 'pending',
    CONSTRAINT `fk_reserve_user` FOREIGN KEY (`user_id`) 
        REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_reserve_book` FOREIGN KEY (`book_id`) 
        REFERENCES `books` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `users` (`user_id_number`, `full_name`, `email`, `password`, `role`, `course_year`, `contact_number`) VALUES
('LIB-001', 'Prof. Eleanor Vance', 'librarian@university.edu', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'librarian', 'Head Librarian', '0917-123-4567'),
('STU-2026-001', 'Alex Rivera', 'alex.rivera@student.edu', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'student', 'BS Computer Science - 1st Year', '0928-555-0101'),
('STU-2026-002', 'Samantha Cruz', 'samantha.cruz@student.edu', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'student', 'BS Information Technology - 1st Year', '0939-555-0202');

INSERT INTO `categories` (`name`, `description`) VALUES
('Computer Science', 'Programming, Algorithms, Data Structures, and Systems'),
('Mathematics', 'Calculus, Linear Algebra, and Discrete Math'),
('Information Technology', 'Networking, Web Technologies, and Databases'),
('Literature & Arts', 'Classic Novels, Creative Writing, and Philosophy'),
('General Science', 'Physics, Chemistry, and Scientific Reference');

INSERT INTO `books` (`isbn`, `title`, `author`, `category_id`, `total_copies`, `available_copies`, `shelf_location`, `description`) VALUES
('978-0131103627', 'The C Programming Language', 'Brian W. Kernighan, Dennis M. Ritchie', 1, 5, 4, 'Shelf CS-101', 'The definitive reference guide for ANSI C programming by its original creators.'),
('978-0262033848', 'Introduction to Algorithms (CLRS)', 'Thomas H. Cormen, Charles E. Leiserson', 1, 4, 3, 'Shelf CS-102', 'Comprehensive textbook providing an in-depth survey of modern algorithms and data structures.'),
('978-0134685991', 'Effective Java (3rd Edition)', 'Joshua Bloch', 1, 3, 3, 'Shelf CS-103', 'Best practices and design patterns for modern object-oriented programming in Java.'),
('978-0134093413', 'Computer Networking: A Top-Down Approach', 'James Kurose, Keith Ross', 3, 4, 4, 'Shelf IT-201', 'Foundational text covering OSI layers, IP networking, socket programming, and protocols.'),
('978-0321125217', 'Domain-Driven Design', 'Eric Evans', 3, 2, 1, 'Shelf IT-202', 'Tackling complexity in the heart of modern enterprise software architecture.'),
('978-0132350884', 'Clean Code: A Handbook of Agile Craftsmanship', 'Robert C. Martin', 1, 6, 5, 'Shelf CS-104', 'Even bad code can function. But if code isn’t clean, it can bring a development organization to its knees.'),
('978-0486600889', 'Calculus Made Easy', 'Silvanus P. Thompson', 2, 4, 4, 'Shelf MATH-301', 'A classic introductory guide simplifying differential and integral calculus concepts.'),
('978-0451524935', '1984', 'George Orwell', 4, 3, 2, 'Shelf LIT-401', 'Dystopian masterpiece exploring totalitarianism, surveillance, and personal freedom.');

INSERT INTO `borrow_records` (`user_id`, `book_id`, `borrow_date`, `due_date`, `return_date`, `fine_amount`, `fine_paid`, `status`) VALUES
(2, 5, CURDATE() - INTERVAL 2 DAY, CURDATE() + INTERVAL 5 DAY, NULL, 0.00, 0, 'borrowed'),
(3, 8, CURDATE() - INTERVAL 11 DAY, CURDATE() - INTERVAL 4 DAY, NULL, 40.00, 0, 'overdue');

INSERT INTO `reservations` (`user_id`, `book_id`, `reservation_date`, `status`) VALUES
(2, 2, NOW() - INTERVAL 1 HOUR, 'pending');
