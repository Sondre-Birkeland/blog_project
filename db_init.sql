DROP DATABASE IF EXISTS blog;
CREATE DATABASE blog;
USE blog;

CREATE TABLE users (
	id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(30) UNIQUE NOT NULL,
    password CHAR(64) NOT NULL,
    is_admin BOOL DEFAULT FALSE
);

CREATE TABLE posts (
	id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(30) NOT NULL,
    content VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE comments (
	id INT PRIMARY KEY AUTO_INCREMENT,
    content VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    post_id INT,
    user_id INT,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE post_likes (
	id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    post_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (post_id) REFERENCES posts(id),
    CONSTRAINT UNIQUE (user_id, post_id)
);

CREATE TABLE comment_likes (
	id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    comment_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (comment_id) REFERENCES comments(id),
    CONSTRAINT UNIQUE (user_id, comment_id)
);

CREATE TABLE tags (
	id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE
);

CREATE TABLE post_tags (
	post_id INT,
    tag_id INT,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    CONSTRAINT UNIQUE (post_id, tag_id)
);


INSERT INTO users(username, password, is_admin) VALUES
('user1', '78e1ff0deb8d9b3cbaa934b8f1773cd117edea714dcab0e62109233a3e36293b', TRUE),
('user2', '822f2935cd87313ab4900483eb4a24003633efc487241c5ca7f1f5e9dbb76e10', FALSE),
('user3', '51c235b349dd4af59b9f2ae219cae37263dcf084599cb8537beec0cf19d8b82b', FALSE);

INSERT INTO posts(title, content, user_id) VALUES
('First post', 'This is the first post', 1),
('Second post', 'And this is the second post', 1);

INSERT INTO comments(content, post_id, user_id) VALUES
('This is the first comment', 1, 1),
('I can also comment', 1, 2),
('First comment on the second post', 2, 3),
('I can comment multiple times on the same post', 2, 3);

INSERT INTO tags(name) VALUES
('short'), ('long'), ('inane'), ('funny');

INSERT INTO post_tags(post_id, tag_id) VALUES
(1, 1),
(1, 3),
(2, 3);