-- Eliminar tablas si existen (para poder recrear el esquema)
DROP TABLE IF EXISTS shopping_cart CASCADE;
DROP TABLE IF EXISTS user_movie CASCADE;
DROP TABLE IF EXISTS movie_actor CASCADE;
DROP TABLE IF EXISTS movies CASCADE;
DROP TABLE IF EXISTS actors CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS genres CASCADE;
DROP TABLE IF EXISTS cart_totals CASCADE;

-- TABLA: actores
CREATE TABLE actors (
    actor_id SERIAL PRIMARY KEY,
    namee VARCHAR(200) NOT NULL,
    birth_date DATE,
    origin VARCHAR(50)
);

-- TABLA: generos
CREATE TABLE genres (
    genre_id SERIAL PRIMARY KEY,
    namee VARCHAR(100) NOT NULL UNIQUE,
    descriptionn TEXT
);

-- TABLA: peliculas
CREATE TABLE movies (
    movie_id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    descriptionn TEXT,
    year_release INTEGER CHECK (year_release >= 1888 AND year_release <= 2025),
    duration INTEGER CHECK (duration > 0),
    genre_id INTEGER REFERENCES genres(genre_id),
    director VARCHAR(150),
    avg_score DECIMAL(3,1) CHECK (avg_score >= 0 AND avg_score <= 10),
    price DECIMAL(5,2) CHECK (price >= 0),
    stock INTEGER CHECK (stock >= 0)
);

-- TABLA: usuarios
CREATE TABLE users (
    uuid_user VARCHAR(100) PRIMARY KEY,
    namee VARCHAR(200) NOT NULL,
    nationality VARCHAR(50),
    hash_password VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL,
    phone VARCHAR(20),
    postal_code VARCHAR(10),
    balance DECIMAL(8,1) DEFAULT 0.0 CHECK (balance >= 0),
    discount DECIMAL(5,2) DEFAULT 0.0 CHECK (discount >= 0 AND discount <= 100) 
);

-- TABLA: movie_actor
CREATE TABLE movie_actor (
    movie_id INTEGER REFERENCES movies(movie_id) ON DELETE CASCADE,
    actor_id INTEGER REFERENCES actors(actor_id) ON DELETE CASCADE,
    paper VARCHAR(100),
    is_lead BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (movie_id, actor_id)
);

-- TABLA: user_movie
CREATE TABLE user_movie (
    uuid_user VARCHAR(100) REFERENCES users(uuid_user),
    movie_id INTEGER REFERENCES movies(movie_id) ON DELETE CASCADE,
    score INTEGER CHECK (score >= 1 AND score <= 10),
    PRIMARY KEY (uuid_user, movie_id)
);

-- TABLA: shopping_cart
CREATE TABLE shopping_cart (
    uuid_user VARCHAR(100) REFERENCES users(uuid_user),
    movie_id INTEGER REFERENCES movies(movie_id) ON DELETE CASCADE,
    quantity INTEGER CHECK (quantity > 0),
    PRIMARY KEY (uuid_user, movie_id)
);

-- TABLA: orders
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    uuid_user VARCHAR(100) REFERENCES users(uuid_user),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_date TIMESTAMP,
    total DECIMAL(10,2) CHECK (total >= 0)
);

-- TABLA: order_details
CREATE TABLE order_details (
    order_id INTEGER REFERENCES orders(order_id),
    movie_id INTEGER REFERENCES movies(movie_id) ON DELETE CASCADE,
    quantity INTEGER CHECK (quantity > 0),
    unit_price DECIMAL(5,2) CHECK (unit_price >= 0),
    PRIMARY KEY (order_id, movie_id)
);

CREATE TABLE IF NOT EXISTS ratings (
  uuid_user  VARCHAR(100) REFERENCES users(uuid_user),
  movie_id   INTEGER      REFERENCES movies(movie_id) ON DELETE CASCADE,
  score      INTEGER      NOT NULL CHECK (score BETWEEN 1 AND 5),
  PRIMARY KEY (uuid_user, movie_id)
);

CREATE TABLE cart_totals (
    uuid_user VARCHAR(100) PRIMARY KEY REFERENCES users(uuid_user),
    total NUMERIC(10,2) DEFAULT 0 CHECK (total >= 0)
);
