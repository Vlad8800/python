CREATE DATABASE IF NOT EXISTS LibrarySystem1;
USE LibrarySystem1;

-- 1. Користувачі (Users)
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('Гість', 'Reader', 'Librarian', 'Writer', 'Operator', 'Admin') DEFAULT 'Гість'
);

-- 2. Автори (Authors)
CREATE TABLE Authors (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    country VARCHAR(100),
    birth_year YEAR,
    user_id INT UNIQUE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);
CREATE TABLE Authors (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    country VARCHAR(100),
    birth_year YEAR
);
-- 3. Категорії книг (Categories)
CREATE TABLE Categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- 4. Книги (Books)
CREATE TABLE Books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author_id INT NOT NULL,
    category_id INT,
    year YEAR,
    languages VARCHAR(50),
    quantity INT NOT NULL DEFAULT 1,
    access_type ENUM('Тільки в читальній залі', 'У читальній залі і в дома') DEFAULT 'Тільки в читальній залі',
    FOREIGN KEY (author_id) REFERENCES Authors(author_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id) ON DELETE SET NULL
);

-- 5. Читацькі зали (ReadingRooms)
CREATE TABLE ReadingRooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    access_type ENUM('Тільки читання', 'З дозволом на виніс') DEFAULT 'Тільки читання'
);

-- 6. Розміщення книг (Placements)
CREATE TABLE Placements (
    placement_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    room_id INT NOT NULL,
    shelf VARCHAR(50),
    roww VARCHAR(50),
    FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES ReadingRooms(room_id) ON DELETE CASCADE
);

-- 7. Читачі (Readers)
CREATE TABLE Readers (
    reader_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    user_name VARCHAR(150) NOT NULL,
    address VARCHAR(255),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reader_type ENUM('Студент', 'Викладач', 'Працівник', 'Інше') DEFAULT 'Студент',
    university VARCHAR(255) DEFAULT NULL,
    faculty VARCHAR(255) DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- 8. Видача книг (IssuedBooks)
CREATE TABLE IssuedBooks (
    issue_id INT AUTO_INCREMENT PRIMARY KEY,
    reader_id INT NOT NULL,
    book_id INT NOT NULL,
    issue_date DATE NOT NULL,
    return_date DATE,
    reading_place ENUM('Тільки в читальній залі', 'У читальній залі і в дома'),
    FOREIGN KEY (reader_id) REFERENCES Readers(reader_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE
);

-- 9. Бібліотекарі (Librarians)
CREATE TABLE Librarians (
    librarian_id INT PRIMARY KEY, -- теж user_id
    name VARCHAR(150) NOT NULL,
    reading_room_id INT NULL,
    FOREIGN KEY (librarian_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (reading_room_id) REFERENCES ReadingRooms(room_id) ON DELETE SET NULL
);
USE LibrarySystem;

-- Заповнення Users
INSERT INTO Users (login, password, role) VALUES
('Vlad', '123', 'Reader'),
('Влад', '123', 'Reader');
INSERT INTO Users (login, password, role) VALUES
('oles_gonchar', 'password_hash', 'Writer'),
('taras_shevchenko', 'password_hash', 'Writer'),
('lesya_ukrainka', 'password_hash', 'Writer');
-- Заповнення Authors
ALTER TABLE Authors
MODIFY COLUMN birth_year YEAR;

INSERT INTO Authors (name, surname, country, birth_year, user_id) VALUES
('Олесь', 'Гончар', 'Україна', 1918, 3),
('Тарас', 'Шевченко', 'Україна', 1950, 4),
('Леся', 'Українка', 'Україна', 1940, 5);
ALTER TABLE Users
MODIFY COLUMN role ENUM('Гість', 'Reader', 'Librarian', 'Writer', 'Admin') DEFAULT 'Гість';


-- Заповнення Categories
INSERT INTO Categories (name) VALUES
('Художня література'),
('Наукова література'),
('Технічна література'),
('Дитяча література'),
('Історична література');
SELECT author_id, name, surname FROM authors WHERE author_id IN (1, 2, 3);

-- Заповнення Books
INSERT INTO Books (title, author_id, category_id, year, languages, quantity, access_type) VALUES
('Тіні забутих предків', 1, 1, 1940, 'Українська', 5, 'У читальній залі і в дома'),
('Кобзар', 2, 1, 1940, 'Українська', 10, 'Тільки в читальній залі'),
('Лісова пісня', 3, 1, 1911, 'Українська', 3, 'У читальній залі і в дома');

-- Заповнення ReadingRooms
INSERT INTO ReadingRooms (name, access_type) VALUES
('Головний читальний зал', 'З дозволом на виніс'),
('Міський читальний зал', 'З дозволом на виніс'),
('Науковий зал', 'З дозволом на виніс');

-- Заповнення Placements
INSERT INTO Placements (book_id, room_id, shelf, roww) VALUES
(1, 1, 'A1', '3'),
(2, 1, 'B3', '1'),
(3, 2, 'C2', '2');

-- Заповнення Readers
INSERT INTO Readers (user_id, user_name, address, reader_type, university, faculty) VALUES
(1, 'reader1', 'вул. Шевченка, 10', 'Студент', 'КНУ', 'Факультет філології'),
(2, 'reader2', 'просп. Перемоги, 5', 'Викладач', NULL, NULL);

-- Заповнення IssuedBooks
INSERT INTO IssuedBooks (reader_id, book_id, issue_date, return_date, reading_place) VALUES
(1, 1, '2025-08-01', NULL, 'У читальній залі і в дома'),
(2, 3, '2025-07-28', '2025-08-05', 'Тільки в читальній залі');

-- Заповнення Librarians
INSERT INTO Librarians (librarian_id, name, reading_room_id) VALUES
(3, 'Ірина Петрова', 1);


ALTER TABLE IssuedBooks
ADD CONSTRAINT unique_active_issue 
UNIQUE (reader_id, book_id, return_date);

SELECT issue_id, reader_id, book_id, issue_date, return_date
FROM IssuedBooks
WHERE return_date = '';

DELETE FROM Categories;

ALTER TABLE categories
MODIFY COLUMN name (
('Книги'),
('Журнали'),
('Газети'),
('Збірники статей'),
('Збірники віршів'),
('Дисертації'),
('Реферати'),
('Збірники доповідей і тез доповідей'),
('Збірники')
);
SELECT u.user_id, u.login, a.author_id, a.name, a.surname, a.user_id
FROM Users u
LEFT JOIN Authors a ON u.user_id = a.user_id
WHERE u.login = 'oles_gonchar';  -- заміни на потрібний логін
