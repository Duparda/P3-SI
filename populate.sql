-- TABLA: genres
INSERT INTO genres (namee, descriptionn) VALUES
('Aventura', 'Historias de aventuras y exploraciones.'),
('Comedia', 'Comedias ligeras y divertidas.'),
('Melodrama Urbano', 'Dramas centrados en relaciones y ciudades ficticias.'),
('Ciencia Ficción', 'Grandes historias épicas en el espacio.'),
('Terror Psicológico', 'Miedos íntimos y atmósferas opresivas.'),
('Documental Fantástico', 'Falsos documentales sobre mitos y leyendas.'),
('Animación Experimental', 'Películas animadas con estética poco convencional.'),
('Noir Moderno', 'Crimen y suspense en ciudades nocturnas.'),
('Romance Retro', 'Historias de amor con estética vintage.'),
('Ciencia Popular', 'Divulgación de ideas científicas imaginarias.'),
('Action', 'Películas de acción y aventuras épicas.');

-- TABLA: actors
INSERT INTO actors (namee, birth_date, origin) VALUES
('Ari Vega', '1987-02-11', 'Española'),
('Bela Mora', '1992-06-05', 'Danesa'),
('Ciro Khan', '1979-12-30', 'Canadiense'),
('Dara Igles', '2000-09-17', 'Australiana'),
('Eloy Quint', '1968-03-22', 'Francesa'),
('Fiona Roux', '1983-11-01', 'Luxemburguesa'),
('Galo Tor', '1995-08-09', 'Rumano'),
('Helia Mendez', '1975-01-25', 'Griega'),
('Iker Paz', '1989-04-14', 'Germana'),
('Juna Bel', '1998-10-02', 'Holandesa'),
('Kaito Rin', '1972-07-13', 'Vietnamita'),
('Lina Oro', '1985-05-06', 'Portuguesa'),
('Miro Santos', '1949-11-20', 'Mexicana'),
('Nora Vale', '1990-03-03', 'Guatemalteca'),
('Orfe Lin', '1963-08-27', 'Japonés'),
('Tom Hardy', '1977-09-15', 'Británico'),
('Keanu Reeves', '1964-09-02', 'Canadiense'),
('Russell Crowe', '1964-04-07', 'Neozelandés');

-- TABLA: movies (SIN DUPLICADOS)
INSERT INTO movies (title, descriptionn, year_release, duration, genre_id, director, avg_score, price, stock) VALUES
('Bruma en Solaria', 'Una exploradora solitaria descubre un planeta cubierto de niebla donde las sombras cobran vida. Una aventura visual sobre el valor de enfrentarse a lo desconocido.', 2023, 112, 1, 'M. Loris', 7.8, 9.99, 10),
('Sonrisa de Cartón', 'Comedia absurda sobre un vendedor de caretas que accidentalmente se vuelve viral. Humor físico y situaciones disparatadas que celebran lo ridículo de la fama instantánea.', 2018, 95, 2, 'V. Rami', 6.4, 6.50, 15),
('Cicatrices de Metro', 'Drama urbano que sigue a tres desconocidos cuyas vidas se entrelazan en el metro de una gran ciudad. Explora la soledad, las conexiones fugaces y las segundas oportunidades.', 2015, 128, 3, 'R. Tane', 8.1, 11.00, 8),
('Reino de Humo', 'Épica de ciencia ficción que narra la lucha de colonos espaciales por sobrevivir en una estación orbital amenazada. Efectos impresionantes y dilemas morales profundos.', 2025, 142, 4, 'S. Quell', 8.9, 15.00, 12),
('Habitantes de Medianoche', 'Thriller psicológico que explora los miedos nocturnos de una comunidad aislada donde los habitantes tienen extrañas pesadillas compartidas. Atmósfera opresiva y giros inesperados.', 2021, 99, 5, 'A. Soler', 7.2, 8.50, 20),
('El Archivo Imaginario', 'Falso documental que examina criaturas mitológicas como si fueran reales. Mezcla de humor seco y fascinación por el folclore mundial.', 2010, 83, 6, 'P. Lema', 7.0, 5.99, 25),
('Rostros en Papel', 'Película de animación experimental que cuenta la historia de personajes dibujados en cuadernos escolares que cobran vida. Estética única y emotiva sobre la creatividad infantil.', 2019, 74, 7, 'N. Gade', 6.8, 4.99, 30),
('Almas de Neón', 'Noir moderno ambientado en calles nocturnas bañadas de luces de neón. Un detective busca a su hermana desaparecida mientras descubre una conspiración criminal. Fotografía impactante.', 2020, 105, 8, 'O. Fier', 8.3, 12.50, 20),
('Verde Retro', 'Romance vintage de los 90 sobre dos jóvenes que se conocen en una tienda de vinilos. Nostalgia, música indie y un amor que trasciende generaciones.', 1996, 118, 9, 'C. Bero', 6.9, 7.00, 18),
('Expedición 7X', 'Aventura espacial sobre una misión a un sistema solar desconocido. Combina ciencia ficción hard con exploración de ideas científicas imaginarias. Visualmente deslumbrante.', 2024, 155, 4, 'Z. Hane', 9.5, 18.00, 14),
('Teoría de los Sombreros', 'Comedia intelectual que divulga conceptos de pensamiento lateral mediante situaciones absurdas. Un científico loco enseña creatividad usando diferentes tipos de sombreros.', 2003, 102, 10, 'L. Petri', 7.6, 9.00, 22),
('Café en la Estación', 'Melodrama íntimo que sigue conversaciones en una cafetería de estación de tren. Historias entrelazadas sobre despedidas, reencuentros y decisiones que cambian vidas.', 2022, 88, 3, 'M. Huan', 7.4, 6.75, 16),
('Última Caja', 'Thriller noir sobre un ladrón que roba una misteriosa caja de seguridad y desata una cadena de eventos peligrosos. Suspense constante y atmósfera oscura.', 2012, 130, 8, 'D. Far', 7.9, 10.00, 19),
('Sueño Tangente', 'Aventura onírica donde los protagonistas viajan entre sueños para rescatar memorias perdidas. Visualmente poética con narrativa no lineal.', 2024, 96, 1, 'R. Almi', 8.0, 11.50, 10),
('The Matrix', 'Un hacker descubre la impactante verdad sobre su realidad y su papel en la guerra contra sus controladores.', 1999, 136, 4, 'Wachowski Sisters', 8.7, 14.99, 25),
('The Matrix Reloaded', 'Neo y sus aliados continúan su lucha contra las máquinas mientras descubren más secretos sobre Matrix.', 2003, 138, 4, 'Wachowski Sisters', 7.2, 13.50, 25),
('The Matrix Revolutions', 'La conclusión épica de la trilogía Matrix donde se decide el destino de la humanidad.', 2003, 129, 4, 'Wachowski Sisters', 6.8, 13.50, 25),
('Gladiator', 'Un general romano traicionado busca venganza como gladiador en el Coliseo de Roma.', 2000, 155, 11, 'Ridley Scott', 8.5, 16.99, 20),
('Inception', 'Un ladrón especializado en extraer secretos del subconsciente debe realizar el trabajo inverso: implantar una idea.', 2010, 148, 4, 'Christopher Nolan', 8.8, 15.99, 20),
('Mad Max Fury Road', 'En un futuro post-apocalíptico, Max se une a Furiosa en una huida desesperada a través del desierto.', 2015, 120, 11, 'George Miller', 8.1, 14.50, 20);

-- TABLA: users
INSERT INTO users (uuid_user, namee, nationality, hash_password, rol, phone, postal_code, balance, discount) VALUES
('826997e2-3bb3-4350-acae-1cee126aa36a', 'admin', 'spain' ,'8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin', '685443697', '28042', 100.0, 10.0),
('ec8de645-46a3-451c-8e52-3abfba955bbb','Lucía Farrell', 'argentina','fc72134bd8067eff3f13a1c95f8df6e68933c3b1f675c02346f1da0ebcd332f4', 'cliente', '600100001', '28010', 40.0, 0.0),
('cf453b39-d6de-413d-bb13-94b2b424fbb3','Marco Bellini', 'italy','f03f5afbfba0d13c77dc2d6817b3a363e60e38b27fbb1b29086c809f252b1c0f','cliente' , '600100002', '08099', 5.2, 0.0),
('81f95c25-c94d-4bf1-90b6-26b45ed6d779','Noa Garrido', 'colombia','dcb36287fb00868fd296b42c0e0c30106ba629bf25740df9f753861b9f33ea1a', 'cliente', '600100003', '41012', 120.0, 0.0),
('75555db5-5a52-48b2-bd85-4a5ebf3c1459','Pablo Estrada', 'france','c385a067ccb93aab7969d40a5be7c04e22a0b6efb280de6fc66eec858d032ccb', 'cliente', '600100004', '46007', 0.0, 0.0),
('c040ac50-857c-4309-8bbe-5a6bb2adff85','Sira Cortes', 'mexico','dae1b6a6db42c08a44ad1147b00a56476f5b7d6d55511e85b227088a7277a1a6', 'cliente', '600100005', '50001', 18.4, 0.0),
('9df68bba-d1b4-4fd0-8c63-7f2e900cb4aa','Tomas Ibarra', 'england','ad511a199b29d87201273963c7a48b68cc48bd9c963ca0b0f51ea47708a3dd16', 'cliente', '600100006', '28011', 250.7, 0.0),
('c6145194-13dc-49c1-bc78-a484726262aa','Uma Rivas', 'andorra','bacf9e601318d7e23e20c52876c5b71787396eb0e6bb2ab341f08f905150c210', 'cliente', '600100007', '08011', 3.0, 0.0),
('c569540b-41a7-40eb-91ad-1108b2a9ce5c','Vera Sol', 'spain','16f40d4e6ddffaf0c182e503c875113d2f2658b2aa945fe4e53d0ab879b6ac3e', 'cliente', '600100008', '29020', 75.0, 0.0);

-- TABLA: movie_actor (REFERENCIAS CORREGIDAS - solo peliculas 1-14)
INSERT INTO movie_actor (movie_id, actor_id, paper, is_lead) VALUES
(1, 1, 'Ari Sol', TRUE),
(1, 8, 'Capitana Hueso', FALSE),
(2, 2, 'Bela la Ríe', TRUE),
(2, 11, 'Maestro Kaito', FALSE),
(3, 3, 'Inspector Ciro', TRUE),
(3, 13, 'Anciano Miro', FALSE),
(4, 4, 'Dara de Humo', TRUE),
(4, 12, 'Lina Coral', FALSE),
(5, 5, 'Eloy Navarro', TRUE),
(5, 14, 'Nora V.', FALSE),
(6, 6, 'Fiona Reportera', TRUE),
(7, 7, 'Galo Dibujante', TRUE),
(8, 9, 'Iker Nocturno', TRUE),
(8, 10, 'Juna B.', FALSE),
(9, 12, 'Lina en Rosa', TRUE),
(10, 1, 'Ari el Capitán', TRUE),
(10, 11, 'Kaito Asistente', FALSE),
(11, 15, 'Orfe', TRUE),
(12, 6, 'Fiona Bibliotecaria', TRUE),
(13, 3, 'Ciro el Detective', TRUE),
(14, 13, 'Miro el Barista', TRUE),
(6, 15, 'Orfe el Camarógrafo', FALSE),
(14, 2, 'Bela la Asistente', FALSE),
(11, 4, 'Dara la Técnica', FALSE),
(9, 1, 'Ari Vintage', FALSE),
(7, 12, 'Lina la Modelo', FALSE),
-- Nuevas películas con actores conocidos
(15, 17, 'Neo', TRUE),
(16, 17, 'Neo', TRUE),
(17, 17, 'Neo', TRUE),
(18, 18, 'Maximus', TRUE),
(19, 17, 'Dom Cobb', TRUE),
(19, 16, 'Eames', FALSE),
(20, 16, 'Max Rockatansky', TRUE);

-- TABLA: ratings (REFERENCIAS CORREGIDAS - solo peliculas 1-14)
INSERT INTO ratings (uuid_user, movie_id, score) VALUES
-- Lucía 
('ec8de645-46a3-451c-8e52-3abfba955bbb', 8, 5),   
('ec8de645-46a3-451c-8e52-3abfba955bbb', 12, 4),  
('ec8de645-46a3-451c-8e52-3abfba955bbb', 4, 5),  
('ec8de645-46a3-451c-8e52-3abfba955bbb', 10, 5),  

-- Marco 
('cf453b39-d6de-413d-bb13-94b2b424fbb3', 2, 3),   
('cf453b39-d6de-413d-bb13-94b2b424fbb3', 7, 3),  

-- Noa 
('81f95c25-c94d-4bf1-90b6-26b45ed6d779', 13, 5), 
('81f95c25-c94d-4bf1-90b6-26b45ed6d779', 3, 5),   
('81f95c25-c94d-4bf1-90b6-26b45ed6d779', 8, 4),   
('81f95c25-c94d-4bf1-90b6-26b45ed6d779', 9, 3),   

-- Pablo 
('75555db5-5a52-48b2-bd85-4a5ebf3c1459', 2, 3),   
('75555db5-5a52-48b2-bd85-4a5ebf3c1459', 6, 4),   

-- Sira 
('c040ac50-857c-4309-8bbe-5a6bb2adff85', 12, 4),  
('c040ac50-857c-4309-8bbe-5a6bb2adff85', 5, 4),   
('c040ac50-857c-4309-8bbe-5a6bb2adff85', 1, 4),   

-- Tomas 
('9df68bba-d1b4-4fd0-8c63-7f2e900cb4aa', 11, 5),  
('9df68bba-d1b4-4fd0-8c63-7f2e900cb4aa', 4, 5),  
('9df68bba-d1b4-4fd0-8c63-7f2e900cb4aa', 10, 5),  
('9df68bba-d1b4-4fd0-8c63-7f2e900cb4aa', 3, 4),   
('9df68bba-d1b4-4fd0-8c63-7f2e900cb4aa', 13, 4),  

-- Uma 
('c6145194-13dc-49c1-bc78-a484726262aa', 5, 4),   
('c6145194-13dc-49c1-bc78-a484726262aa', 7, 2),   

-- Vera 
('c569540b-41a7-40eb-91ad-1108b2a9ce5c', 6, 4),   
('c569540b-41a7-40eb-91ad-1108b2a9ce5c', 9, 4),  
('c569540b-41a7-40eb-91ad-1108b2a9ce5c', 12, 4),  
('c569540b-41a7-40eb-91ad-1108b2a9ce5c', 2, 3);

-- TABLA: shopping_cart
INSERT INTO shopping_cart (uuid_user, movie_id, quantity) VALUES-- Noa 
('81f95c25-c94d-4bf1-90b6-26b45ed6d779', 13, 10), 
('81f95c25-c94d-4bf1-90b6-26b45ed6d779', 3, 9),   
('81f95c25-c94d-4bf1-90b6-26b45ed6d779', 8, 8),   
('81f95c25-c94d-4bf1-90b6-26b45ed6d779', 9, 6),   

-- Pablo 
('75555db5-5a52-48b2-bd85-4a5ebf3c1459', 2, 6),   
('75555db5-5a52-48b2-bd85-4a5ebf3c1459', 6, 7),   

-- Sira 
('c040ac50-857c-4309-8bbe-5a6bb2adff85', 12, 8),  
('c040ac50-857c-4309-8bbe-5a6bb2adff85', 5, 7),   
('c040ac50-857c-4309-8bbe-5a6bb2adff85', 1, 8),   

-- Tomas 
('9df68bba-d1b4-4fd0-8c63-7f2e900cb4aa', 11, 9),  
('9df68bba-d1b4-4fd0-8c63-7f2e900cb4aa', 4, 10),  
('9df68bba-d1b4-4fd0-8c63-7f2e900cb4aa', 10, 9),  
('9df68bba-d1b4-4fd0-8c63-7f2e900cb4aa', 3, 8),   
('9df68bba-d1b4-4fd0-8c63-7f2e900cb4aa', 13, 7),  

-- Uma 
('c6145194-13dc-49c1-bc78-a484726262aa', 5, 7),   
('c6145194-13dc-49c1-bc78-a484726262aa', 7, 4),   

-- Vera 
('c569540b-41a7-40eb-91ad-1108b2a9ce5c', 6, 8),   
('c569540b-41a7-40eb-91ad-1108b2a9ce5c', 9, 7),  
('c569540b-41a7-40eb-91ad-1108b2a9ce5c', 12, 8),  
('c569540b-41a7-40eb-91ad-1108b2a9ce5c', 2, 5);

-- TABLA: shopping_cart
INSERT INTO shopping_cart (uuid_user, movie_id, quantity) VALUES
-- Lucía quiere comprar
('ec8de645-46a3-451c-8e52-3abfba955bbb', 3, 1),   
('ec8de645-46a3-451c-8e52-3abfba955bbb', 7, 1),  

-- Marco quiere comprar
('cf453b39-d6de-413d-bb13-94b2b424fbb3', 4, 1),   
('cf453b39-d6de-413d-bb13-94b2b424fbb3', 10, 1),  
('cf453b39-d6de-413d-bb13-94b2b424fbb3', 8, 1),   

-- Noa quiere comprar
('81f95c25-c94d-4bf1-90b6-26b45ed6d779', 1, 1),   
('81f95c25-c94d-4bf1-90b6-26b45ed6d779', 6, 1),   

-- Pablo quiere comprar
('75555db5-5a52-48b2-bd85-4a5ebf3c1459', 8, 1),   
('75555db5-5a52-48b2-bd85-4a5ebf3c1459', 11, 1),  
('75555db5-5a52-48b2-bd85-4a5ebf3c1459', 13, 1),  

-- Sira quiere comprar
('c040ac50-857c-4309-8bbe-5a6bb2adff85', 4, 1),   
('c040ac50-857c-4309-8bbe-5a6bb2adff85', 10, 1),  

-- Tomas quiere comprar
('9df68bba-d1b4-4fd0-8c63-7f2e900cb4aa', 1, 1),   
('9df68bba-d1b4-4fd0-8c63-7f2e900cb4aa', 6, 1),   
('9df68bba-d1b4-4fd0-8c63-7f2e900cb4aa', 9, 1),   

-- Uma quiere comprar
('c6145194-13dc-49c1-bc78-a484726262aa', 1, 1),   
('c6145194-13dc-49c1-bc78-a484726262aa', 3, 1),   
('c6145194-13dc-49c1-bc78-a484726262aa', 8, 1),   
('c6145194-13dc-49c1-bc78-a484726262aa', 11, 1),  

-- Vera quiere comprar
('c569540b-41a7-40eb-91ad-1108b2a9ce5c', 1, 1),   
('c569540b-41a7-40eb-91ad-1108b2a9ce5c', 4, 1),   
('c569540b-41a7-40eb-91ad-1108b2a9ce5c', 10, 1),  
('c569540b-41a7-40eb-91ad-1108b2a9ce5c', 13, 1);

-- =============================
-- TABLA: orders (compras completadas)
-- =============================
INSERT INTO orders (uuid_user, order_date, payment_date, total) VALUES
-- Pedido 1: Lucía - Octubre 2025
('ec8de645-46a3-451c-8e52-3abfba955bbb', '2025-10-15 14:23:45', NULL, 38.48),

-- Pedido 2: Noa - Septiembre 2025
('81f95c25-c94d-4bf1-90b6-26b45ed6d779', '2025-09-28 18:45:12', NULL, 44.50),

-- Pedido 3: Tomas - Septiembre 2025
('9df68bba-d1b4-4fd0-8c63-7f2e900cb4aa', '2025-09-20 11:30:00', NULL, 64.00),

-- Pedido 4: Sira - Agosto 2025
('c040ac50-857c-4309-8bbe-5a6bb2adff85', '2025-08-12 16:20:30', NULL, 18.49),

-- Pedido 5: Marco - Agosto 2025
('cf453b39-d6de-413d-bb13-94b2b424fbb3', '2025-08-05 10:15:22', NULL, 16.49),

-- Pedido 6: Vera - Julio 2025
('c569540b-41a7-40eb-91ad-1108b2a9ce5c', '2025-07-22 19:40:18', NULL, 24.24),

-- Pedido 7: Pablo - Junio 2025
('75555db5-5a52-48b2-bd85-4a5ebf3c1459', '2025-06-18 13:55:30', NULL, 12.49),

-- Pedido 8: Uma - Mayo 2025
('c6145194-13dc-49c1-bc78-a484726262aa', '2025-05-30 17:22:11', NULL, 13.49),

-- Pedido 9: Lucía - Mayo 2025 (segundo pedido)
('ec8de645-46a3-451c-8e52-3abfba955bbb', '2025-05-10 12:10:45', NULL, 12.50),

-- Pedido 10: Tomas - Abril 2025 (segundo pedido)
('9df68bba-d1b4-4fd0-8c63-7f2e900cb4aa', '2025-04-22 15:33:28', NULL, 27.00);

-- =============================
-- TABLA: order_details
-- =============================
INSERT INTO order_details (order_id, movie_id, quantity, unit_price) VALUES
-- Pedido 1 (Lucía): 4 películas = 38.48€
(1, 8, 1, 12.50),   -- Almas de Neón
(1, 12, 1, 6.75),   -- Café en la Estación
(1, 4, 1, 15.00),   -- Reino de Humo
(1, 10, 1, 18.00),  -- Expedición 7X
-- TOTAL: 52.25 (hay descuento aplicado)

-- Pedido 2 (Noa): 4 películas = 44.50€
(2, 13, 1, 11.50),  -- Sueño Tangente
(2, 3, 1, 11.00),   -- Cicatrices de Metro
(2, 8, 1, 12.50),   -- Almas de Neón
(2, 9, 1, 7.00),    -- Verde Retro

-- Pedido 3 (Tomas): 5 películas = 64.00€
(3, 11, 1, 9.00),   -- Teoría de los Sombreros
(3, 4, 1, 15.00),   -- Reino de Humo
(3, 10, 1, 18.00),  -- Expedición 7X
(3, 3, 1, 11.00),   -- Cicatrices de Metro
(3, 13, 1, 11.50),  -- Sueño Tangente

-- Pedido 4 (Sira): 2 películas = 18.49€
(4, 12, 1, 10.00),  -- Última Caja (precio de entonces)
(4, 5, 1, 8.50),    -- Habitantes de Medianoche

-- Pedido 5 (Marco): 2 películas = 16.49€
(5, 1, 1, 9.99),    -- Bruma en Solaria
(5, 2, 1, 6.50),    -- Sonrisa de Cartón

-- Pedido 6 (Vera): 3 películas = 24.24€
(6, 6, 1, 5.99),    -- El Archivo Imaginario
(6, 9, 1, 7.00),    -- Verde Retro
(6, 12, 1, 6.75),   -- Café en la Estación
(6, 2, 1, 6.50),    -- Sonrisa de Cartón

-- Pedido 7 (Pablo): 2 películas = 12.49€
(7, 2, 1, 6.50),    -- Sonrisa de Cartón
(7, 6, 1, 5.99),    -- El Archivo Imaginario

-- Pedido 8 (Uma): 2 películas = 13.49€
(8, 5, 1, 8.50),    -- Habitantes de Medianoche
(8, 7, 1, 4.99),    -- Rostros en Papel

-- Pedido 9 (Lucía - segundo): 1 película = 12.50€
(9, 8, 1, 12.50),   -- Almas de Neón (compra duplicada para regalo)

-- Pedido 10 (Tomas - segundo): 3 películas = 27.00€
(10, 1, 1, 9.99),   -- Bruma en Solaria
(10, 6, 1, 5.99),   -- El Archivo Imaginario
(10, 9, 1, 7.00);   -- Verde Retro