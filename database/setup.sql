CREATE TABLE Students(id INTEGER PRIMARY KEY AUTOINCREMENT,
firstname TEXT NOT NULL,
lastname TEXT NOT NULL);

CREATE TABLE Marks(id INTEGER PRIMARY KEY AUTOINCREMENT,
student_id INTEGER,
subject TEXT NOT NULL,
mark INTEGER,
last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

INSERT INTO Students(firstname, lastname) VALUES
('Tim','Martin'),
('Bob','Jane'),
('Sarah','Doe'),
('Jacob','Brooks'),
('Hannah','Lee'),
('Sue','Smith');