from datetime import date
from quart import Quart, request, jsonify
import uuid
import os
from hashlib import sha256
from sqlalchemy import String, Float, Boolean, select, insert, update, delete, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import IntegrityError
import config

# Configuración de la base de datos
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://alumnodb:1234@localhost:9999/si1")
app = Quart(__name__)

# Engine asíncrono
engine = create_async_engine(DATABASE_URL, echo=False)

def parse_iso_date_or_none(value):
    if not value:
        return None
    try:
        # Acepta 'YYYY-MM-DD'
        return date.fromisoformat(value)
    except Exception:
        return None

def get_bearer_token(headers):
    auth = headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    return auth.split(" ", 1)[1].strip()

def is_admin(headers):
    token = get_bearer_token(headers)
    if not token:
        return False
    expected = f"{config.ADMIN_UUID}.{uuid.uuid5(config.SECRET_UUID, config.ADMIN_UUID)}"
    return token == expected

def get_token(headers):
    auth_header = headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ", 1)[1].strip()

def parse_uid_from_token(token: str) -> str | None:
    try:
        return token.split(".", 1)[0]
    except Exception:
        return None


def validate_token(token):
    uid = parse_uid_from_token(token)
    if not uid:
        return False
    expected = f"{uid}.{uuid.uuid5(config.SECRET_UUID, uid)}"
    return token == expected

async def fetch_all(engine, query, params={}):
    async with engine.connect() as conn:
        result = await conn.execute(text(query), params)
        rows = result.all()
        keys = result.keys()
        data = [dict(zip(keys, row)) for row in rows]

    return data

@app.get("/movies")
async def show_movies():
    token = get_token(request.headers)
    if not validate_token(token):
        return jsonify({"error": "No autorizado"}), 401
    uid = parse_uid_from_token(token)

    
    title = request.args.get("title")
    year = request.args.get("year", type=int)
    genre = request.args.get("genre")
    actor = request.args.get("actor")

    base = """ SELECT m.movie_id AS movieid, m.title, m.year_release AS year, g.namee as genre, m.price, m.descriptionn AS description FROM movies m LEFT JOIN genres g ON m.genre_id = g.genre_id """
    where = []
    params = {}

    if actor:
        base += """
        JOIN movie_actor ma ON ma.movie_id = m.movie_id
        JOIN actors a ON a.actor_id = ma.actor_id
        """
        where.append("a.namee ILIKE :actor")
        params["actor"] = f"%{actor}%"

    if title:
        where.append("m.title ILIKE :title")
        params["title"] = f"%{title}%"

    if year is not None:
        where.append("m.year_release = :year")
        params["year"] = year

    if genre:
        where.append("g.namee ILIKE :genre")
        params["genre"] = f"%{genre}%"

    query = base + (" WHERE " + " AND ".join(where) if where else "")

    data = await fetch_all(engine, query, params)
    return jsonify(data), 200

#añadir al carrito
@app.put("/cart/<int:id_pelicula>")
async def add_to_cart(id_pelicula: int):
    token = get_token(request.headers)
    if not validate_token(token):
        return jsonify({"error": "No autorizado"}), 401

    uid = parse_uid_from_token(token)

    async with engine.begin() as conn:

        peli = await conn.execute(text("SELECT movie_id FROM movies WHERE movie_id = :id"), {"id": id_pelicula})
        
        if not peli.first():
            return jsonify({"error": "Película no encontrada"}), 404

        exists = await conn.execute(text(""" SELECT 1 FROM shopping_cart WHERE uuid_user = :uid AND movie_id = :id """),
                                    {"uid": uid, "id": id_pelicula})
        
        if not exists.first():
            await conn.execute(text(""" INSERT INTO shopping_cart (uuid_user, movie_id, quantity) VALUES (:uid, :id, 1)"""),
                {"uid": uid, "id": id_pelicula})

    return jsonify({"added": id_pelicula}), 200

#ver el carrito
@app.get("/cart")
async def get_cart():
    token = get_token(request.headers)
    if not validate_token(token):
        return jsonify({"error": "No autorizado"}), 401

    uid = parse_uid_from_token(token)

    query = """
        SELECT 
            c.movie_id       AS movieid,
            m.title            AS title,
            m.price            AS price,
            c.quantity          AS quantity
        FROM shopping_cart c
        JOIN movies m ON m.movie_id = c.movie_id
        WHERE c.uuid_user = :uid
    """
    data = await fetch_all(engine, query, {"uid": uid})

    return jsonify(data), 200

#quitar del carrito
@app.delete("/cart/<int:id_pelicula>")
async def remove_from_cart(id_pelicula: int):
    token = get_token(request.headers)
    if not validate_token(token):
        return jsonify({"error": "No autorizado"}), 401

    uid = parse_uid_from_token(token)

    async with engine.begin() as conn:
        await conn.execute( text(""" DELETE FROM shopping_cart WHERE uuid_user = :uid AND movie_id = :id"""),
            {"uid": uid, "id": id_pelicula})

    return jsonify({"removed": id_pelicula}), 200

#añadir saldo 
@app.post("/user/credit")
async def add_credit():
    token = get_token(request.headers)
    if not validate_token(token):
        return jsonify({"error": "No autorizado"}), 401

    uid = parse_uid_from_token(token)

    data = await request.get_json()
    amount = data.get("amount")

    if amount is None or amount <= 0:
        return jsonify({"error": "Cantidad inválida"}), 400

    async with engine.begin() as conn:
        result = await conn.execute(
            text(""" 
                UPDATE users 
                SET balance = balance + :amount 
                WHERE uuid_user = :uid
                RETURNING balance
            """),
            {"amount": amount, "uid": uid})
        new_balance = result.scalar()

    return jsonify({"added_credit": amount, "new_credit": float(new_balance)}), 200


@app.post("/cart/checkout")
async def checkout():
    token = get_token(request.headers)
    if not validate_token(token):
        return jsonify({"error": "No autorizado"}), 401
    uid = parse_uid_from_token(token)

    async with engine.begin() as conn:
        
        total = await conn.execute(
            text("""
                SELECT COALESCE(SUM(c.quantity * m.price), 0)
                FROM shopping_cart c
                JOIN movies m ON m.movie_id = c.movie_id
                WHERE c.uuid_user = :uid"""), {"uid": uid})
        
        total = float(total.scalar() or 0.0)
        if total <= 0:
            return jsonify({"error": "El carrito está vacío"}), 400

        
        saldo = await conn.execute(text("SELECT balance FROM users WHERE uuid_user = :uid"), {"uid": uid})
        saldo = saldo.scalar()
        if saldo is None:
            return jsonify({"error": "Usuario no encontrado"}), 404
        if float(saldo) < total:
            return jsonify({"error": "Saldo insuficiente", "total": total, "saldo": float(saldo)}), 402
        
        pedido = await conn.execute(
            text("""
                INSERT INTO orders (uuid_user, total)
                VALUES (:uid, :total)
                RETURNING order_id, order_date"""),{"uid": uid, "total": total})
        
        id_pedido, fecha_pedido = pedido.first()

        await conn.execute(
            text("""
                INSERT INTO order_details (order_id, movie_id, quantity, unit_price)
                SELECT :id_pedido, c.movie_id, c.quantity, m.price
                FROM shopping_cart c
                JOIN movies m ON m.movie_id = c.movie_id
                WHERE c.uuid_user = :uid"""), {"id_pedido": id_pedido, "uid": uid})

        await conn.execute(
            text("""
                UPDATE shopping_cart
                SET purchased = TRUE
                WHERE uuid_user = :uid"""), {"uid": uid})

        await conn.execute(
            text("DELETE FROM shopping_cart WHERE uuid_user = :uid"),
            {"uid": uid})

    return jsonify({"orderid": int(id_pedido)}), 200
            


@app.get("/orders/<int:orderid>")
async def get_order(orderid: int):
    token = get_token(request.headers)
    if not validate_token(token):
        return jsonify({"error": "No autorizado"}), 401
    uid = parse_uid_from_token(token)

    async with engine.connect() as conn:
        head = await conn.execute(
            text("""
                SELECT order_id, uuid_user, order_date, total
                FROM orders
                WHERE order_id = :id AND uuid_user = :uid """), {"id": orderid, "uid": uid})
        
        h = head.first()
        if not h:
            return jsonify({"error": "Pedido no encontrado"}), 404

        items = await conn.execute(
            text("""
                SELECT 
                    od.movie_id          AS movieid,
                    m.title                AS title,
                    od.unit_price      AS price,
                    od.quantity             AS quantity
                FROM order_details od
                JOIN movies m ON m.movie_id = od.movie_id
                WHERE od.order_id = :id"""), {"id": orderid})
        
        movies = [dict(row) for row in items.mappings().all()]

        fecha = h[2]
        return jsonify({
            "orderid": int(h[0]),
            "date":    (fecha.isoformat() if hasattr(fecha, "isoformat") else str(fecha)),
            "total":   float(h[3]),
            "movies":  movies}), 200


@app.get("/health")
async def health():
    return {"status": "ok"}, 200

# votar una película
@app.post("/movies/<int:id_pelicula>/vote")
async def vote_movie(id_pelicula: int):
    token = get_token(request.headers)
    if not validate_token(token):
        return jsonify({"error": "No autorizado"}), 401
    uid = parse_uid_from_token(token)

    data = await request.get_json()
    score = data.get("score")

    # Validación de score
    score = int(score)
    if not (1 <= score <= 5):
        return jsonify({"error": "score debe estar entre 1 y 5"}), 400

    async with engine.begin() as conn:
        exists = await conn.execute(
            text("SELECT 1 FROM movies WHERE movie_id = :id"),
            {"id": id_pelicula})
        
        if not exists.first():
            return jsonify({"error": "Película no encontrada"}), 404

        # UPSERT del voto (un voto por usuario/película)
        await conn.execute(
            text("""
                INSERT INTO ratings (uuid_user, movie_id, score)
                VALUES (:uid, :id, :score)
                ON CONFLICT (uuid_user, movie_id)
                DO UPDATE SET score = EXCLUDED.score """), {"uid": uid, "id": id_pelicula, "score": score})

        return jsonify({"movieid": id_pelicula, "score": score}), 200

# ver puntuación de una película
@app.get("/movies/<int:id_pelicula>/rating")
async def get_movie_rating(id_pelicula: int):
    token = get_token(request.headers)
    if not validate_token(token):
        return jsonify({"error": "No autorizado"}), 401

    async with engine.connect() as conn:
        
        exists = await conn.execute(
            text("SELECT 1 FROM movies WHERE movie_id = :id"),{"id": id_pelicula})
        if not exists.first():
            return jsonify({"error": "Película no encontrada"}), 404

        row = await conn.execute(
            text("""
                SELECT COUNT(*) AS votes, AVG(score)::float AS avg
                FROM ratings
                WHERE movie_id = :id """), {"id": id_pelicula})
        stats = row.mappings().first() or {"votes": 0, "avg": None}

    return jsonify({
        "movieid": id_pelicula,
        "votes": int(stats["votes"]),
        "avg": (float(stats["avg"]) if stats["avg"] is not None else None)
    }), 200

# ver si un usuario ha valorado una película y qué puntuación le dio
@app.get("/movies/<int:id_pelicula>/user_rating")
async def get_user_movie_rating(id_pelicula: int):
    token = get_token(request.headers)
    if not validate_token(token):
        return jsonify({"error": "No autorizado"}), 401
    uid = parse_uid_from_token(token)

    async with engine.connect() as conn:
        # Verificar que la película existe
        exists = await conn.execute(
            text("SELECT 1 FROM movies WHERE movie_id = :id"),
            {"id": id_pelicula}
        )
        if not exists.first():
            return jsonify({"error": "Película no encontrada"}), 404

        # Buscar si el usuario ha valorado la película
        row = await conn.execute(
            text("""
                SELECT score
                FROM ratings
                WHERE movie_id = :movie_id AND uuid_user = :uid
            """),
            {"movie_id": id_pelicula, "uid": uid}
        )
        rating = row.first()

        if rating is None:
            return jsonify({
                "movieid": id_pelicula,
                "uuid_user": uid,
                "rated": False,
                "score": None
            }), 200
        
        return jsonify({
            "movieid": id_pelicula,
            "uuid_user": uid,
            "rated": True,
            "score": rating[0]
        }), 200

#crear pelicula
@app.post("/movies")
async def create_movie():
    if not is_admin(request.headers):
        return jsonify({"error": "No autorizado"}), 403

    data = await request.get_json()
    titulo = data.get("title")
    precio = data.get("price")
    genero = data.get("genre")
    descripcion = data.get("description")

    if not titulo or precio is None:
        return jsonify({"error": "Faltan campos obligatorios: title, price"}), 400
    if precio < 0:
        return jsonify({"error": "El precio no puede ser negativo"}), 400

    async with engine.begin() as conn:
        query = text("""
            INSERT INTO movies (title, descriptionn, price)
            VALUES (:title, :description, :price)
            RETURNING movie_id, title, descriptionn, price""")
        row = await conn.execute(query, {
            "title": titulo,
            "description": descripcion,
            "price": precio
        })
        m = row.mappings().first()

    return jsonify({
        "movieid": m["movie_id"],
        "title": m["title"],
        "description": m["descriptionn"],
        "price": float(m["price"])}), 201
#ver pelicula
@app.get("/movies/<int:id_pelicula>")
async def get_movie(id_pelicula: int):
    token = get_token(request.headers)
    if not validate_token(token):
        return jsonify({"error": "No autorizado"}), 401

    async with engine.connect() as conn:
        row = await conn.execute(
            text("""
                SELECT m.movie_id, m.title, m.descriptionn, m.price, m.year_release, m.stock, g.namee as genre
                FROM movies m
                LEFT JOIN genres g ON m.genre_id = g.genre_id
                WHERE m.movie_id = :id """), {"id": id_pelicula})
        m = row.mappings().first()
        if not m:
            return jsonify({"error": "Película no encontrada"}), 404

    return jsonify({
        "movieid": m["movie_id"],
        "title": m["title"],
        "description": m["descriptionn"],
        "price": float(m["price"]),
        "year": m["year_release"],
        "stock": m["stock"],
        "genre": m["genre"]}), 200

#obtener las n películas más votadas
@app.get("/movies/top-rated")
async def get_top_rated_movies():
    """
    Obtiene las n películas más votadas según los votos de los usuarios.
    Parámetros:
    - limit: número de películas a devolver (default: 10, máximo: 100)
    - min_votes: número mínimo de votos requeridos para considerar una película (default: 1)
    - title: filtro opcional por título (búsqueda parcial)
    - genre: filtro opcional por género (búsqueda parcial)
    - year: filtro opcional por año
    """
    token = get_token(request.headers)
    if not validate_token(token):
        return jsonify({"error": "No autorizado"}), 401

    # Parámetros de consulta
    limit = request.args.get("limit", default=10, type=int)
    min_votes = request.args.get("min_votes", default=1, type=int)
    title = request.args.get("title")
    genre = request.args.get("genre")
    year = request.args.get("year", type=int)

    # Validaciones
    if limit < 1 or limit > 100:
        return jsonify({"error": "El límite debe estar entre 1 y 100"}), 400
    
    if min_votes < 0:
        return jsonify({"error": "min_votes debe ser mayor o igual a 0"}), 400

    # Construcción de la consulta
    where_conditions = []
    params = {
        "limit": limit,
        "min_votes": min_votes
    }

    if title:
        where_conditions.append("m.title ILIKE :title")
        params["title"] = f"%{title}%"
    
    if genre:
        where_conditions.append("g.namee ILIKE :genre")
        params["genre"] = f"%{genre}%"
    
    if year is not None:
        where_conditions.append("m.year_release = :year")
        params["year"] = year

    where_clause = ""
    if where_conditions:
        where_clause = "WHERE " + " AND ".join(where_conditions)

    query = text(f"""
        SELECT 
            m.movie_id,
            m.title,
            m.year_release,
            g.namee as genre,
            m.price,
            m.descriptionn,
            m.director,
            m.duration,
            COUNT(r.uuid_user) as vote_count,
            COALESCE(AVG(r.score), 0)::DECIMAL(3,2) as avg_rating
        FROM movies m
        LEFT JOIN genres g ON m.genre_id = g.genre_id
        LEFT JOIN ratings r ON m.movie_id = r.movie_id
        {where_clause}
        GROUP BY m.movie_id, g.namee
        HAVING COUNT(r.uuid_user) >= :min_votes
        ORDER BY avg_rating DESC, vote_count DESC, m.title ASC
        LIMIT :limit
    """)

    async with engine.connect() as conn:
        result = await conn.execute(query, params)
        movies = result.mappings().all()

        movies_data = []
        for movie in movies:
            movies_data.append({
                "movie_id": movie["movie_id"],
                "title": movie["title"],
                "year_release": movie["year_release"],
                "genre": movie["genre"],
                "price": float(movie["price"]) if movie["price"] else None,
                "description": movie["descriptionn"],
                "director": movie["director"],
                "duration": movie["duration"],
                "vote_count": movie["vote_count"],
                "avg_rating": float(movie["avg_rating"])
            })

    return jsonify({
        "count": len(movies_data),
        "limit": limit,
        "min_votes": min_votes,
        "movies": movies_data
    }), 200

#actualizar pelicula
@app.put("/movies/<int:id_pelicula>")
async def update_movie(id_pelicula: int):
    if not is_admin(request.headers):
        return jsonify({"error": "No autorizado"}), 403

    data = await request.get_json()
    titulo = data.get("title")
    precio = data.get("price")
    genero = data.get("genre")
    descripcion = data.get("description")

    async with engine.begin() as conn:
        exists = await conn.execute(
            text("SELECT 1 FROM movies WHERE movie_id = :id"), {"id": id_pelicula})
        if not exists.first():
            return jsonify({"error": "Película no encontrada"}), 404

        update_fields = {}
        if titulo is not None:
            update_fields["title"] = titulo
        if precio is not None:
            if precio < 0:
                return jsonify({"error": "El precio no puede ser negativo"}), 400
            update_fields["price"] = precio
        if genero is not None:
            update_fields["genre_id"] = genero
        if descripcion is not None:
            update_fields["descriptionn"] = descripcion

        if not update_fields:
            return jsonify({"error": "No hay campos para actualizar"}), 400

        set_clause = ", ".join([f"{key} = :{key}" for key in update_fields.keys()])
        update_fields["id"] = id_pelicula

        await conn.execute(text(f"UPDATE movies SET {set_clause} WHERE movie_id = :id"), update_fields)

    return jsonify({"updated": id_pelicula}), 200

#eliminar pelicula
@app.delete("/movies/<int:id_pelicula>")
async def delete_movie(id_pelicula: int):
    if not is_admin(request.headers):
        return jsonify({"error": "No autorizado"}), 403

    async with engine.begin() as conn:
        exists = await conn.execute(
            text("SELECT 1 FROM movies WHERE movie_id = :id"), {"id": id_pelicula})
        if not exists.first():
            return jsonify({"error": "Película no encontrada"}), 404

        try:
            await conn.execute(
                text("DELETE FROM movies WHERE movie_id = :id"),
                {"id": id_pelicula})
        except IntegrityError:
            return jsonify({"error": "No se puede borrar: tiene dependencias"}), 409

    return jsonify({"deleted": id_pelicula}), 200

#añadir actor 
@app.post("/actors")
async def create_actor():
    if not is_admin(request.headers):
        return jsonify({"error": "No autorizado"}), 403

    data = await request.get_json(silent=True) or {}
    nombre = data.get("name")
    fecha_nac = parse_iso_date_or_none(data.get("birth_date"))
    nacionalidad = data.get("origin")

    if not nombre:
        return jsonify({"error": "Faltan campos obligatorios: name"}), 400
    if data.get("birth_date") and not fecha_nac:
        return jsonify({"error": "birth_date debe tener formato YYYY-MM-DD"}), 400

    async with engine.begin() as conn:
        row = await conn.execute(
            text("""
                INSERT INTO actors (namee, birth_date, origin)
                VALUES (:name, :birth_date, :origin)
                RETURNING actor_id, namee, birth_date, origin """),
            {
                "name": nombre,
                "birth_date": fecha_nac,
                "origin": nacionalidad
            }
        )
        a = row.mappings().first()

    return jsonify({
        "actorid": a["actor_id"],
        "name": a["namee"],
        "birth_date": (a["birth_date"].isoformat() if a["birth_date"] else None),
        "origin": a["origin"]
    }), 201

#actualizar actor 
@app.put("/actors/<int:actorid>")
async def update_actor(actorid: int):
    if not is_admin(request.headers):
        return jsonify({"error": "No autorizado"}), 403

    data = await request.get_json(silent=True) or {}
    nombre = data.get("name")
    fecha_nac = parse_iso_date_or_none(data.get("birth_date"))
    nacionalidad = data.get("origin")

    async with engine.begin() as conn:
        exists = await conn.execute(
            text("SELECT 1 FROM actors WHERE actor_id = :id"), {"id": actorid})
        if not exists.first():
            return jsonify({"error": "Actor no encontrado"}), 404

        update_fields = {}
        if nombre is not None:
            update_fields["namee"] = nombre
        if data.get("birth_date") is not None:
            if fecha_nac is None:
                return jsonify({"error": "birth_date debe tener formato YYYY-MM-DD"}), 400
            update_fields["birth_date"] = fecha_nac
        if nacionalidad is not None:
            update_fields["origin"] = nacionalidad

        if not update_fields:
            return jsonify({"error": "No hay campos para actualizar"}), 400

        set_clause = ", ".join([f"{key} = :{key}" for key in update_fields.keys()])
        update_fields["id"] = actorid

        await conn.execute(text(f"UPDATE actors SET {set_clause} WHERE actor_id = :id"), update_fields)

    return jsonify({"updated": actorid}), 200

#borrar actor
@app.delete("/actors/<int:id_actor>")
async def delete_actor(id_actor: int):
    if not is_admin(request.headers):
        return jsonify({"error": "No autorizado"}), 403

    async with engine.begin() as conn:
        exists = await conn.execute(
            text("SELECT 1 FROM actors WHERE actor_id = :id"),
            {"id": id_actor})
        if not exists.first():
            return jsonify({"error": "Actor no encontrado"}), 404

        try:
            await conn.execute(
                text("DELETE FROM actors WHERE actor_id = :id"),
                {"id": id_actor}
            )
        except IntegrityError:
            return jsonify({"error": "No se puede borrar: tiene dependencias"}), 409

    return jsonify({"deleted": id_actor}), 200

#ver actor  
@app.get("/actors/<int:id_actor>")
async def get_actor(id_actor: int):
    token = get_token(request.headers)
    if not validate_token(token):
        return jsonify({"error": "No autorizado"}), 401

    async with engine.connect() as conn:
        row = await conn.execute(
            text("""
                SELECT actor_id, namee, birth_date, origin
                FROM actors
                WHERE actor_id = :id """), {"id": id_actor})
        a = row.mappings().first()
        if not a:
            return jsonify({"error": "Actor no encontrado"}), 404

    return jsonify({
        "actorid": a["actor_id"],
        "name": a["namee"],
        "birth_date": (a["birth_date"].isoformat() if a["birth_date"] else None),
        "origin": a["origin"]
    }), 200

#ver películas por actores
@app.get("/actors/movies")
async def get_movies_by_actors():
    """
    Obtiene películas en las que participan uno o varios actores.
    Parámetros:
    - actor_ids: IDs de actores separados por comas (ej: "1,2,3")
    - match_all: si es 'true', solo devuelve películas con TODOS los actores.
                 si es 'false' (default), devuelve películas con AL MENOS UNO de los actores.
    """
    token = get_token(request.headers)
    if not validate_token(token):
        return jsonify({"error": "No autorizado"}), 401

    actor_ids_param = request.args.get("actor_ids")
    match_all = request.args.get("match_all", "false").lower() == "true"
    
    if not actor_ids_param:
        return jsonify({"error": "Debe proporcionar al menos un actor_id"}), 400
    
    try:
        actor_ids = [int(aid.strip()) for aid in actor_ids_param.split(",")]
    except ValueError:
        return jsonify({"error": "Los actor_ids deben ser números enteros separados por comas"}), 400
    
    if not actor_ids:
        return jsonify({"error": "Debe proporcionar al menos un actor_id"}), 400

    async with engine.connect() as conn:
        # Verificar que todos los actores existen
        for actor_id in actor_ids:
            exists = await conn.execute(
                text("SELECT 1 FROM actors WHERE actor_id = :id"),
                {"id": actor_id})
            if not exists.first():
                return jsonify({"error": f"Actor con ID {actor_id} no encontrado"}), 404

        if match_all:
            # Películas que tienen TODOS los actores especificados
            query = text("""
                SELECT DISTINCT 
                    m.movie_id,
                    m.title,
                    m.year_release,
                    g.namee as genre,
                    m.price,
                    m.descriptionn,
                    m.director,
                    m.duration
                FROM movies m
                LEFT JOIN genres g ON m.genre_id = g.genre_id
                WHERE m.movie_id IN (
                    SELECT movie_id
                    FROM movie_actor
                    WHERE actor_id = ANY(:actor_ids)
                    GROUP BY movie_id
                    HAVING COUNT(DISTINCT actor_id) = :count
                )
                ORDER BY m.title
            """)
            result = await conn.execute(query, {"actor_ids": actor_ids, "count": len(actor_ids)})
        else:
            # Películas que tienen AL MENOS UNO de los actores especificados
            query = text("""
                SELECT DISTINCT 
                    m.movie_id,
                    m.title,
                    m.year_release,
                    g.namee as genre,
                    m.price,
                    m.descriptionn,
                    m.director,
                    m.duration
                FROM movies m
                LEFT JOIN genres g ON m.genre_id = g.genre_id
                INNER JOIN movie_actor ma ON m.movie_id = ma.movie_id
                WHERE ma.actor_id = ANY(:actor_ids)
                ORDER BY m.title
            """)
            result = await conn.execute(query, {"actor_ids": actor_ids})
        
        movies = result.mappings().all()
        
        # Para cada película, obtener la lista de actores que participan
        movies_data = []
        for movie in movies:
            actors_result = await conn.execute(
                text("""
                    SELECT 
                        a.actor_id,
                        a.namee,
                        ma.paper,
                        ma.is_lead
                    FROM actors a
                    INNER JOIN movie_actor ma ON a.actor_id = ma.actor_id
                    WHERE ma.movie_id = :movie_id
                    ORDER BY ma.is_lead DESC, a.namee
                """),
                {"movie_id": movie["movie_id"]}
            )
            actors_list = [
                {
                    "actor_id": actor["actor_id"],
                    "name": actor["namee"],
                    "paper": actor["paper"],
                    "is_lead": actor["is_lead"]
                }
                for actor in actors_result.mappings().all()
            ]
            
            movies_data.append({
                "movie_id": movie["movie_id"],
                "title": movie["title"],
                "year_release": movie["year_release"],
                "genre": movie["genre"],
                "price": float(movie["price"]) if movie["price"] else None,
                "description": movie["descriptionn"],
                "director": movie["director"],
                "duration": movie["duration"],
                "actors": actors_list
            })

    return jsonify({
        "count": len(movies_data),
        "movies": movies_data
    }), 200

# permita recuperar todas las ventas que se han
@app.get("/estadisticaVentas/<int:year>/<string:country>/")
async def get_sales_statistics(year: int, country: str):
    token = get_token(request.headers)
    if not validate_token(token):
        return jsonify({"error": "No autorizado"}), 401

    async with engine.connect() as conn:
        # Consulta para obtener todas las ventas del año y país especificados
        query = text("""
            SELECT 
                o.order_id,
                o.uuid_user,
                o.order_date,
                o.total
                FROM orders o
                JOIN users u ON o.uuid_user = u.uuid_user
                WHERE EXTRACT(YEAR FROM o.order_date) = :year
                AND LOWER(u.nationality) = LOWER(:country)
                ORDER BY o.order_date DESC;
        """)
        
        result = await conn.execute(query, {"year": year, "country": country})
        orders = result.mappings().all()
        #convertimos fechas a strings
        result = []
        for r in orders:
            result.append({
                "order_id": r["order_id"],
                "uuid_user": r["uuid_user"],
                "order_date": r["order_date"].isoformat(),
                "total": float(r["total"])
            })

    return jsonify({
        "year": year,
        "country": country,
        "count": len(result),
        "orders": result
    }), 200

@app.get("/clientesSinPedidos/")
async def get_customers_without_orders():
    token = get_token(request.headers)
    if not validate_token(token):
        return jsonify({"error": "No autorizado"}), 401

    async with engine.connect() as conn:
        query = text(""" 
            SELECT u.uuid_user, u.namee
            FROM users u
            LEFT JOIN orders o ON u.uuid_user = o.uuid_user
            WHERE o.order_id IS NULL
        """)
        result = await conn.execute(query)
        users = result.mappings().all()

    result = []
    for u in users:
        result.append({
            "uuid_user": u["uuid_user"],
            "name": u["namee"]
        })
    return jsonify({
        "count": len(result),
        "users": result
    }), 200

@app.delete("/borraPais/<pais>")
async def delete_user_country(pais):
    if not is_admin(request.headers):
        return jsonify({"error": "No autorizado"}), 403

    async with engine.begin() as conn:
        # Verificar que existen usuarios del país
        exists = await conn.execute(
            text("SELECT COUNT(*) FROM users WHERE LOWER(nationality) = LOWER(:pais)"),
            {"pais": pais})
        count = exists.scalar()

        if count == 0:
            return jsonify({"error": f"No hay usuarios del país {pais}"}), 404
        
        try:
            # Orden correcto: eliminar primero las tablas que tienen FK a users
            await conn.execute(
                text("DELETE FROM shopping_cart WHERE uuid_user IN (SELECT uuid_user FROM users WHERE LOWER(nationality) = LOWER(:pais))"),
                {"pais": pais})
            
            await conn.execute(
                text("DELETE FROM cart_totals WHERE uuid_user IN (SELECT uuid_user FROM users WHERE LOWER(nationality) = LOWER(:pais))"),
                {"pais": pais})
            
            await conn.execute(
                text("DELETE FROM ratings WHERE uuid_user IN (SELECT uuid_user FROM users WHERE LOWER(nationality) = LOWER(:pais))"),
                {"pais": pais})
            
            await conn.execute(
                text("DELETE FROM order_details WHERE order_id IN (SELECT order_id FROM orders WHERE uuid_user IN (SELECT uuid_user FROM users WHERE LOWER(nationality) = LOWER(:pais)))"),
                {"pais": pais})
            
            await conn.execute(
                text("DELETE FROM orders WHERE uuid_user IN (SELECT uuid_user FROM users WHERE LOWER(nationality) = LOWER(:pais))"),
                {"pais": pais})
            
            # Finalmente eliminamos los usuarios
            await conn.execute(
                text("DELETE FROM users WHERE LOWER(nationality) = LOWER(:pais)"),
                {"pais": pais})
            
            # El commit es automático al salir de engine.begin()
            
        except Exception as e:
            # El rollback es automático si hay excepción
            return jsonify({"error": f"Error al eliminar usuarios: {str(e)}"}), 500
    
    return jsonify({"deleted_country": pais, "deleted_users": count}), 200

@app.delete("/borraPaisIncorrecto/<pais>")
async def delete_user_country_incorrect(pais):
    """
    Transacción incorrecta: intenta eliminar users antes que las tablas dependientes.
    Esto genera un error de foreign key y hace rollback completo.
    """
    if not is_admin(request.headers):
        return jsonify({"error": "No autorizado"}), 403

    async with engine.begin() as conn:
        # Verificar que existen usuarios del país
        exists = await conn.execute(
            text("SELECT COUNT(*) FROM users WHERE LOWER(nationality) = LOWER(:pais)"),
            {"pais": pais})
        count = exists.scalar()

        if count == 0:
            return jsonify({"error": f"No hay usuarios del país {pais}"}), 404
        
        try:
            # Eliminamos solo algunas tablas dependientes (no todas)
            await conn.execute(
                text("DELETE FROM shopping_cart WHERE uuid_user IN (SELECT uuid_user FROM users WHERE LOWER(nationality) = LOWER(:pais))"),
                {"pais": pais})
            
            await conn.execute(
                text("DELETE FROM cart_totals WHERE uuid_user IN (SELECT uuid_user FROM users WHERE LOWER(nationality) = LOWER(:pais))"),
                {"pais": pais})
            
            # ERROR: Intentamos borrar users mientras aún tienen referencias en orders, ratings, etc.
            # Esto causará un error de foreign key porque orders tiene foreign key a users
            await conn.execute(
                text("DELETE FROM users WHERE LOWER(nationality) = LOWER(:pais)"),
                {"pais": pais})
            
        except IntegrityError as e:
            # El rollback es automático con engine.begin()
            print(f"Error de clave foránea esperado: {e}")
            return jsonify({"error": "Error de foreign key. Rollback realizado"}), 409
        except Exception as e:
            print(f"Error inesperado: {e}")
            return jsonify({"error": f"Error inesperado: {str(e)}"}), 500
    
    # Esta línea nunca debería ejecutarse si todo funciona correctamente
    return jsonify({"deleted_country": pais, "deleted_users": count}), 200

@app.delete("/borraPaisIntermedio/<pais>")
async def delete_user_country_intermediate(pais):
    """
    Transacción con commit intermedio: hace commit de ratings y user_movie,
    luego intenta una segunda transacción que falla. El primer commit persiste,
    pero el segundo hace rollback.
    """
    if not is_admin(request.headers):
        return jsonify({"error": "No autorizado"}), 403

    # verificar existencia
    async with engine.connect() as conn:
        exists = await conn.execute(
            text("SELECT COUNT(*) FROM users WHERE LOWER(nationality) = LOWER(:pais)"),
            {"pais": pais})
        count = exists.scalar()

        if count == 0:
            return jsonify({"error": f"No hay usuarios del país {pais}"}), 404
    
    # primera transacción (se commitea)
    try:
        async with engine.begin() as conn:
            # Eliminamos ratings y user_movie
            await conn.execute(
                text("DELETE FROM ratings WHERE uuid_user IN (SELECT uuid_user FROM users WHERE LOWER(nationality) = LOWER(:pais))"),
                {"pais": pais})
            
            # Al salir de este bloque, se hace COMMIT automático
        
        # segunda transacción (fallará y hará rollback)
        async with engine.begin() as conn:
            # ERROR: Intentamos borrar users mientras aún tienen referencias en orders
            await conn.execute(
                text("DELETE FROM users WHERE LOWER(nationality) = LOWER(:pais)"),
                {"pais": pais})
            
            # Estas líneas no se ejecutarán debido al error
            await conn.execute(
                text("DELETE FROM shopping_cart WHERE uuid_user IN (SELECT uuid_user FROM users WHERE LOWER(nationality) = LOWER(:pais))"),
                {"pais": pais})
            
            await conn.execute(
                text("DELETE FROM cart_totals WHERE uuid_user IN (SELECT uuid_user FROM users WHERE LOWER(nationality) = LOWER(:pais))"),
                {"pais": pais})
            
            await conn.execute(
                text("DELETE FROM order_details WHERE order_id IN (SELECT order_id FROM orders WHERE uuid_user IN (SELECT uuid_user FROM users WHERE LOWER(nationality) = LOWER(:pais)))"),
                {"pais": pais})
            
            await conn.execute(
                text("DELETE FROM orders WHERE uuid_user IN (SELECT uuid_user FROM users WHERE LOWER(nationality) = LOWER(:pais))"),
                {"pais": pais})
    
    except IntegrityError as e:
        # El rollback es automático solo para la segunda transacción
        # La primera transacción sí se commiteó
        print(f"Error de clave foránea en segunda transacción: {e}")
        return jsonify({"error": "Error de foreign key. Rollback de segunda transacción realizado. Primer commit persiste."}), 409
    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

    # Esta línea nunca debería ejecutarse
    return jsonify({"deleted_country": pais, "deleted_users": count}), 200