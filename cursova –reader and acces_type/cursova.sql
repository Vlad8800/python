CREATE DATABASE IF NOT EXISTS LibrarySystem;
USE LibrarySystem;

-- Автори
CREATE TABLE Authors (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    country VARCHAR(100),
    birth_year YEAR
);

-- Категорії книг
CREATE TABLE Categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Книги
CREATE TABLE Books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author_id INT NOT NULL,
    category_id ENUM('Жахи', 'Пригоди', 'Роман', 'Оповідання') DEFAULT 'Оповідання',
    year YEAR,
    languages VARCHAR(50),
    inventory_number VARCHAR(50) UNIQUE,
    FOREIGN KEY (author_id) REFERENCES Authors(author_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id) ON DELETE SET NULL
);

-- Читацькі зали
CREATE TABLE ReadingRooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    access_type ENUM('Тільки читання', 'З дозволом на виніс') DEFAULT 'Тільки читання'
);

-- Розміщення книг у залах
CREATE TABLE Placements (
    placement_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    room_id INT NOT NULL,
    shelf VARCHAR(50),
    row VARCHAR(50),
    FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES ReadingRooms(room_id) ON DELETE CASCADE
);

-- Читачі (додаткові дані для ролі Reader)
CREATE TABLE readers (
    reader_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    user_name VARCHAR(150) NOT NULL,
    address VARCHAR(255),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reader_type ENUM('Студент', 'Викладач', 'Працівник', 'Інше') DEFAULT 'Студент',
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- Видача книг читачам
CREATE TABLE IssuedBooks (
    issue_id INT AUTO_INCREMENT PRIMARY KEY,
    reader_id INT NOT NULL,
    book_id INT NOT NULL,
    issue_date DATE NOT NULL,
    return_date DATE,
    FOREIGN KEY (reader_id) REFERENCES Readers(reader_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE
);

-- Користувачі системи (базова таблиця)
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('Гість', 'Reader', 'Librarian', 'Operator', 'Admin') DEFAULT 'Гість'
);

-- Бібліотекарі (розширені дані)
CREATE TABLE Librarians (
    librarian_id INT PRIMARY KEY, -- теж user_id
    name VARCHAR(150) NOT NULL,
    reading_room_id INT  NULL,
    FOREIGN KEY (librarian_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (reading_room_id) REFERENCES ReadingRooms(room_id) ON DELETE SET NULL
);

ALTER TABLE Readers
ADD COLUMN university VARCHAR(255) DEFAULT NULL,
ADD COLUMN faculty VARCHAR(255) DEFAULT NULL;
ALTER TABLE Users
MODIFY COLUMN role ENUM('Гість', 'Reader', 'Librarian', 'Writer', 'Admin') DEFAULT 'Гість';


ALTER TABLE Authors
MODIFY COLUMN birth_year DATE;
DESCRIBE Authors;
ALTER TABLE Authors
ADD COLUMN user_id INT,
ADD FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE;

ALTER TABLE Authors ADD COLUMN user_id INT UNIQUE;

ALTER TABLE Authors MODIFY author_id INT NOT NULL;

ALTER TABLE books DROP FOREIGN KEY books_ibfk_1;
ALTER TABLE authors MODIFY author_id INT NOT NULL AUTO_INCREMENT;
ALTER TABLE Books 
MODIFY COLUMN category_id ENUM(
    'книги',
    'журнали',
    'газети',
    'збірники статей',
    'збірники віршів',
    'дисертації',
    'реферати',
    'збірники доповідей і тез доповідей'
) DEFAULT 'книги';

ALTER TABLE authors
ADD CONSTRAINT fk_authors_users
FOREIGN KEY (user_id) REFERENCES users(user_id)
ON DELETE CASCADE;
INSERT INTO authors (name, surname, user_id)
VALUES ('Олесь', 'Гончар', 5);
INSERT INTO Categories (name) VALUES
('Художня література'),
('Наукова література'),
('Технічна література'),
('Дитяча література'),
('Історична література');
ALTER TABLE Books
ADD COLUMN type ENUM(
    'книги',
    'журнали',
    'газети',
    'збірники статей',
    'збірники віршів',
    'дисертації',
    'реферати',
    'збірники доповідей і тез доповідей'
) DEFAULT 'книги';
-- Видаляємо inventory_number
ALTER TABLE Books
DROP COLUMN inventory_number;

-- Додаємо тип літератури як ENUM
ALTER TABLE Books
ADD COLUMN type ENUM(
    'книги',
    'журнали',
    'газети',
    'збірники статей',
    'збірники віршів',
    'дисертації',
    'реферати',
    'збірники доповідей і тез доповідей'
) DEFAULT 'книги';
-- Видаляємо inventory_number
ALTER TABLE Books
DROP COLUMN inventory_number;

-- Додаємо тип літератури як ENUM
ALTER TABLE Books
ADD COLUMN type ENUM(
    'книги',
    'журнали',
    'газети',
    'збірники статей',
    'збірники віршів',
    'дисертації',
    'реферати',
    'збірники доповідей і тез доповідей'
) DEFAULT 'книги';
ALTER TABLE Books
DROP COLUMN category_id;