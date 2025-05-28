DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;

CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(25) NOT NULL,
    description TEXT
) ENGINE INNODB;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(25) UNIQUE NOT NULL,
    first_name VARCHAR(25) NOT NULL,
    last_name VARCHAR(25) NOT NULL,
    middle_name VARCHAR(25) DEFAULT NULL,
    password_hash VARCHAR(256) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    role_id INTEGER,
    FOREIGN KEY (role_id) REFERENCES roles(id)
) ENGINE INNODB;

CREATE TABLE visit_logs (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    path VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)



INSERT INTO roles (id, name)
VALUES (1, 'admin'),
       (2, 'user');

INSERT INTO users (username, first_name, last_name, password_hash, role_id)
VALUES ('admin', 'Иванова', 'Анастасия', SHA2('S0.0S', 256), 1);

INSERT INTO users (username, first_name, last_name, password_hash, role_id)
VALUES ('nastoika', 'Иванова', 'Анастасия', SHA2('790011', 256), 1);