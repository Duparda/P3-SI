CREATE OR REPLACE FUNCTION actualizar_total_carrito(p_uuid VARCHAR)
RETURNS VOID AS $$
DECLARE
    nuevo_total DECIMAL(10,2);
BEGIN
    SELECT COALESCE(SUM(m.price * sc.quantity), 0)
    INTO nuevo_total
    FROM shopping_cart sc
    JOIN movies m ON sc.movie_id = m.movie_id
    WHERE sc.uuid_user = p_uuid;

    UPDATE cart_totals 
    SET total = nuevo_total
    WHERE uuid_user = p_uuid;

END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION ajustar_stock()
RETURNS TRIGGER AS $$
DECLARE
    cantidad_diff INTEGER;
BEGIN
    IF TG_OP = 'INSERT' THEN
        cantidad_diff := NEW.quantity;

        UPDATE movies
        SET stock = stock - cantidad_diff
        WHERE movie_id = NEW.movie_id;

        PERFORM actualizar_total_carrito(NEW.uuid_user);
        RETURN NEW;

    ELSIF TG_OP = 'UPDATE' THEN
        cantidad_diff := NEW.quantity - OLD.quantity;

        UPDATE movies
        SET stock = stock - cantidad_diff
        WHERE movie_id = NEW.movie_id;

        PERFORM actualizar_total_carrito(NEW.uuid_user);
        RETURN NEW;

    ELSIF TG_OP = 'DELETE' THEN
        cantidad_diff := OLD.quantity;

        UPDATE movies
        SET stock = stock + cantidad_diff
        WHERE movie_id = OLD.movie_id;

        PERFORM actualizar_total_carrito(OLD.uuid_user);
        RETURN OLD;
    END IF;

END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_carrito_insert
AFTER INSERT ON shopping_cart
FOR EACH ROW EXECUTE FUNCTION ajustar_stock();

CREATE TRIGGER trg_carrito_update
AFTER UPDATE ON shopping_cart
FOR EACH ROW EXECUTE FUNCTION ajustar_stock();

CREATE TRIGGER trg_carrito_delete
AFTER DELETE ON shopping_cart
FOR EACH ROW EXECUTE FUNCTION ajustar_stock();



CREATE OR REPLACE FUNCTION actualizar_avg_score()
RETURNS TRIGGER AS $$
DECLARE
    nuevo_avg DECIMAL(3,2);
BEGIN
    SELECT COALESCE(AVG(score), 0)
    INTO nuevo_avg
    FROM ratings r 
    WHERE movie_id = COALESCE(NEW.movie_id, OLD.movie_id);

    UPDATE movies
    SET avg_score = nuevo_avg
    WHERE movie_id = COALESCE(NEW.movie_id, OLD.movie_id);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_rating_insert
AFTER INSERT ON ratings
FOR EACH ROW EXECUTE FUNCTION actualizar_avg_score();

CREATE TRIGGER trg_rating_update
AFTER UPDATE ON ratings
FOR EACH ROW EXECUTE FUNCTION actualizar_avg_score();

CREATE TRIGGER trg_rating_delete
AFTER DELETE ON ratings
FOR EACH ROW EXECUTE FUNCTION actualizar_avg_score();


CREATE OR REPLACE FUNCTION procesar_pago()
RETURN TRIGGER AS $$
DECLARE 
    nuevo_saldo DECIMAL(10,2);
    descuento DECIMAL(5,2);
BEGIN 
    SELECT discount INTO descuento
    FROM users WHERE uuid_user = NEW.uuid_user

    precio_final := NEW.total * (1 - descuento/100);

    NEW.payment_date := CURRENT_TIMESTAMP;

    UPDATE users
    SET balance = balance - total_final
    WHERE uuid_user = NEW.uuid_user;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_pago_order
BEFORE INSERT ON orders
FOR EACH ROW EXECUTE FUNCTION procesar_pago();

CREATE OR REPLACE PROCEDURE calcular_media_pelicula(p_movie INTEGER)
LANGUAGE plpgsql AS $$
DECLARE
    media DECIMAL(3,1);
BEGIN
    SELECT ROUND(AVG(score)::NUMERIC, 1)
    INTO media
    FROM ratings
    WHERE movie_id = p_movie;

    UPDATE movies
    SET avg_score = media
    WHERE movie_id = p_movie;
END;
$$;