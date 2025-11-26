import requests
from http import HTTPStatus

USERS = "http://127.0.0.1:5050"
CATALOG = "http://127.0.0.1:5051"

def ok(name, cond):
    status = "OK" if cond else "FAIL"
    print(f"[{status}] {name}")
    return cond

def main():

    print("# =======================================================")
    print("# Creación y autenticación de usuarios para el test")
    print("# =======================================================")

    # Usuario administrador por defecto, debe existir
    r = requests.get(f"{USERS}/user", json={"name": "admin", "password": "admin"})
    if ok("Autenticar usuario administrador predefinido", r.status_code == HTTPStatus.OK):
        data = r.json()
        _, token_admin = data["uid"], data["token"]
    else:
        print("\nPruebas incompletas: Fin del test por error crítico")
        exit(-1)

    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    # Se asume que el usuario 'Alice' no existe
    r = requests.put(f"{USERS}/user", json={"name": "alice", "password": "secret"}, headers=headers_admin)
    if ok("Crear usuario 'alice'", r.status_code == HTTPStatus.OK and r.json()):
        data = r.json()
        uid_alice, _ = data["uid"], data["username"]
    else:
        print("\nPruebas incompletas: Fin del test por error crítico")
        exit(-1)

    r = requests.get(f"{USERS}/user", json={"name": "alice", "password": "secret"})
    if ok("Autenticar usuario 'alice'", r.status_code == HTTPStatus.OK and r.json()["uid"] == uid_alice):
        data = r.json()
        _, token_alice = data["uid"], data["token"]
    else:
        print("\nPruebas incompletas: Fin del test por error crítico")

    headers_alice = {"Authorization": f"Bearer {token_alice}"}

    print("# =======================================================")
    print("# Distintas consultas de alice al catálogo de películas")
    print("# =======================================================")

    r = requests.get(f"{CATALOG}/movies", headers=headers_alice)
    if ok("Obtener catálogo de películas completo", r.status_code == HTTPStatus.OK):
        data = r.json()
        if data:
            for movie in data:
                print(f"\t- {movie['title']}\n\t  {movie['description']}")
        else:
            print("\tNo hay películas en el catálogo")
    
    # Se asume que al menos hay una película que cumple la condición. Si no se reciben
    # los datos de ninguna película el test se da por no satisfecho
    r = requests.get(f"{CATALOG}/movies", params={"title": "matrix"}, headers=headers_alice)
    if ok("Buscar películas con 'matrix' en el título", r.status_code == HTTPStatus.OK and r.json()):
        data = r.json()
        if data:
            for movie in data:
                print(f"\t[{movie['movieid']}] {movie['title']}")

    r = requests.get(f"{CATALOG}/movies", params={"title": "No debe haber pelis con este título"}, headers=headers_alice)
    ok("Búsqueda fallida de películas por título", r.status_code == HTTPStatus.OK and not r.json())
    
    # Los ids de estas búsqueda se utilizarán después para las pruebas de la gestión
    # del carrito
    movieids = []
    r = requests.get(f"{CATALOG}/movies", params={"title": "Gladiator", "year": 2000, "genre": "action"}, headers=headers_alice)
    if ok("Buscar películas por varios campos de movie", r.status_code == HTTPStatus.OK):
        data = r.json()
        if data:
            for movie in data:
                print(f"\t[{movie['movieid']}] {movie['title']}")
                movieids.append(movie['movieid'])
            
            r = requests.get(f"{CATALOG}/movies/{movieids[0]}", headers=headers_alice)
            if ok(f"Obtener detalles de la película con ID [{movieids[0]}]", 
                  r.status_code == HTTPStatus.OK and r.json() and r.json()['movieid'] == movieids[0]):
                data = r.json()
                print(f"\t{data['title']} ({data['year']})")
                print(f"\tGénero: {movie['genre']}")
                print(f"\tDescripción: {movie['description']}")
                print(f"\tPrecio: {movie['price']}")
        else:
            print("\tNo se encontraron películas.")
    
    r = requests.get(f"{CATALOG}/movies/99999999", headers=headers_alice)
    ok(f"Obtener detalles de la película con ID no válido", HTTPStatus.NOT_FOUND)
    
    r = requests.get(f"{CATALOG}/movies", params={"actor": "Tom Hardy"}, headers=headers_alice)
    if ok("Buscar películas en las que participa 'Tom Hardy'", r.status_code == HTTPStatus.OK and r.json()):
        data = r.json()
        if data:
            for movie in data:
                print(f"\t[{movie['movieid']}] {movie['title']}")
                movieids.append(movie['movieid'])
    
    # Probar endpoint de top-rated
    r = requests.get(f"{CATALOG}/movies/top-rated", params={"limit": 5}, headers=headers_alice)
    if ok("Obtener top 5 películas mejor valoradas", r.status_code == HTTPStatus.OK):
        data = r.json()
        if data and "movies" in data:
            print(f"\tSe obtuvieron {len(data['movies'])} películas")
    
    # Probar búsqueda combinada: actor + limit (n más votadas de un actor)
    r = requests.get(f"{CATALOG}/movies/top-rated", params={"limit": 3, "title": "matrix"}, headers=headers_alice)
    if ok("Obtener top 3 películas con 'matrix' en el título", r.status_code == HTTPStatus.OK):
        data = r.json()
        if data and "movies" in data and data["movies"]:
            print(f"\tSe obtuvieron {len(data['movies'])} películas con matrix")
            for movie in data["movies"]:
                print(f"\t  [{movie['movieid']}] {movie['title']}")
    
    # Probar búsqueda con filtro de género y limit
    r = requests.get(f"{CATALOG}/movies/top-rated", params={"limit": 2, "genre": "Action"}, headers=headers_alice)
    if ok("Obtener top 2 películas de 'Action'", r.status_code == HTTPStatus.OK):
        data = r.json()
        if data and "movies" in data and data["movies"]:
            print(f"\tSe obtuvieron {len(data['movies'])} películas de acción")

    
    # Probar votación de películas
    if movieids:
        r = requests.post(f"{CATALOG}/movies/{movieids[0]}/vote", json={"score": 5}, headers=headers_alice)
        ok(f"Votar película {movieids[0]} con puntuación 5", r.status_code == HTTPStatus.OK)
        
        # Obtener rating de la película
        r = requests.get(f"{CATALOG}/movies/{movieids[0]}/rating", headers=headers_alice)
        if ok(f"Obtener rating de película {movieids[0]}", r.status_code == HTTPStatus.OK and r.json()):
            data = r.json()
            print(f"\tRating promedio: {data.get('avg', 'N/A')}, Total votos: {data.get('votes', 'N/A')}")
    
    # Probar health check
    r = requests.get(f"{CATALOG}/health")
    ok("Health check del servicio de catálogo", r.status_code == HTTPStatus.OK)
    
    print("# =======================================================")
    print("# Pruebas de gestión de películas (ADMIN)")
    print("# =======================================================")
    
    # Crear una nueva película (requiere admin)
    new_movie_data = {  
        "title": "Test Movie",
        "description": "Una película de prueba",
        "year": 2024,
        "duration": 120,
        "genre_id": 1,
        "director": "Test Director",
        "price": 9.99
    }
    r = requests.post(f"{CATALOG}/movies", json=new_movie_data, headers=headers_admin)
    if ok("Crear nueva película (admin)", r.status_code == HTTPStatus.CREATED and r.json()):
        new_movie_id = r.json().get("movieid")
        print(f"\tPelícula creada con ID: {new_movie_id}")
        
        # Actualizar la película recién creada
        update_data = {"price": 12.99, "description": "Descripción actualizada"}
        r = requests.put(f"{CATALOG}/movies/{new_movie_id}", json=update_data, headers=headers_admin)
        ok(f"Actualizar película {new_movie_id}", r.status_code == HTTPStatus.OK)
        
        # Eliminar la película
        r = requests.delete(f"{CATALOG}/movies/{new_movie_id}", headers=headers_admin)
        ok(f"Eliminar película {new_movie_id}", r.status_code == HTTPStatus.OK)
    
    print("# =======================================================")
    print("# Pruebas de gestión de actores (ADMIN)")
    print("# =======================================================")
    
    # Crear un nuevo actor
    new_actor_data = {
        "name": "Test Actor",
        "birth_date": "1990-01-01",
        "origin": "Test Country"
    }
    r = requests.post(f"{CATALOG}/actors", json=new_actor_data, headers=headers_admin)
    if ok("Crear nuevo actor (admin)", r.status_code == HTTPStatus.CREATED and r.json()):
        new_actor_id = r.json().get("actorid")
        print(f"\tActor creado con ID: {new_actor_id}")
        
        # Obtener información del actor
        r = requests.get(f"{CATALOG}/actors/{new_actor_id}", headers=headers_alice)
        if ok(f"Obtener información del actor {new_actor_id}", r.status_code == HTTPStatus.OK and r.json()):
            actor_data = r.json()
            print(f"\tNombre: {actor_data.get('name')}, Origen: {actor_data.get('origin')}")
        
        # Actualizar el actor
        update_actor_data = {"origin": "Updated Country"}
        r = requests.put(f"{CATALOG}/actors/{new_actor_id}", json=update_actor_data, headers=headers_admin)
        ok(f"Actualizar actor {new_actor_id}", r.status_code == HTTPStatus.OK)
        
        # Eliminar el actor
        r = requests.delete(f"{CATALOG}/actors/{new_actor_id}", headers=headers_admin)
        ok(f"Eliminar actor {new_actor_id}", r.status_code == HTTPStatus.OK)
    
    # Probar búsqueda de películas por actor usando actor_ids
    r = requests.get(f"{CATALOG}/actors/movies", params={"actor_ids": "16,17"}, headers=headers_alice)
    if ok("Buscar películas con actores ID 16 o 17", r.status_code == HTTPStatus.OK):
        data = r.json()
        if data and "movies" in data:
            print(f"\tSe encontraron {len(data['movies'])} películas")
    
    # Probar búsqueda de películas que tengan TODOS los actores especificados
    r = requests.get(f"{CATALOG}/actors/movies", params={"actor_ids": "16,17", "match_all": "true"}, headers=headers_alice)
    if ok("Buscar películas que tengan los actores 16 Y 17 (match_all)", r.status_code == HTTPStatus.OK):
        data = r.json()
        if data and "movies" in data and data["movies"]:
            print(f"\tSe encontraron {len(data['movies'])} películas con ambos actores")
            for movie in data["movies"]:
                print(f"\t  [{movie['movie_id']}] {movie['title']}")
        else:
            print("\tNo hay películas con ambos actores")

    
    print("# =======================================================")
    print("# Pruebas de gestión de usuarios")
    print("# =======================================================")
    
    # Cambiar contraseña de alice
    r = requests.put(f"{USERS}/user/alice/password", 
                     json={"old_password": "secret", "new_password": "newsecret"}, 
                     headers=headers_alice)
    ok("Cambiar contraseña de alice", r.status_code == HTTPStatus.OK)
    
    # Verificar que puede autenticarse con nueva contraseña
    r = requests.get(f"{USERS}/user", json={"name": "alice", "password": "newsecret"})
    ok("Autenticar con nueva contraseña", r.status_code == HTTPStatus.OK)
    
    print("# =======================================================")
    print("# Gestión del carrito de alice")
    print("# =======================================================")


    for movieid in movieids:
        r = requests.put(f"{CATALOG}/cart/{movieid}", headers=headers_alice)
        if ok(f"Añadir película con ID [{movieid}] al carrito", r.status_code == HTTPStatus.OK):
            r = requests.get(f"{CATALOG}/cart", headers=headers_alice)
            if ok("Obtener carrito del usuario con el nuevo contenido", r.status_code == HTTPStatus.OK and r.json()):
                data = r.json()
                if data:
                    for movie in data:
                        print(f"\t[{movie['movieid']}] {movie['title']} - {movie['price']}")
            
    if movieids:
        r = requests.put(f"{CATALOG}/cart/{movieids[0]}", headers=headers_alice)
        ok(f"Añadir película con ID [{movieids[0]}] al carrito más de una vez", r.status_code == HTTPStatus.CONFLICT)

        r = requests.delete(f"{CATALOG}/cart/{movieids[-1]}", headers=headers_alice)
        if ok(f"Elimimar película con ID [{movieids[-1]}] del carrito", r.status_code == HTTPStatus.OK):
            r = requests.get(f"{CATALOG}/cart", headers=headers_alice)
            if ok(f"Obtener carrito del usuario sin la película [{movieids[-1]}]", r.status_code == HTTPStatus.OK):
                data = r.json()
                if data:
                    for movie in data:
                        print(f"\t[{movie['movieid']}] {movie['title']} - {movie['price']}")
                else:
                    print("\tEl carrito está vacío.")
    
    r = requests.post(f"{CATALOG}/cart/checkout", headers=headers_alice)
    ok("Checkout del carrito con saldo insuficiente", r.status_code == HTTPStatus.PAYMENT_REQUIRED)

    r = requests.post(f"{CATALOG}/user/credit", json={"amount": 1200.75}, headers=headers_alice)
    if ok("Aumentar el saldo de alice", r.status_code == HTTPStatus.OK and r.json()):
        saldo = float(r.json()["new_credit"])
        print(f"\tSaldo actualizado a {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    r = requests.post(f"{CATALOG}/user/credit", json={"amount": 1000000}, headers=headers_alice)
    if ok("Aumentar el saldo de alice", r.status_code == HTTPStatus.OK and r.json()):
        saldo = float(r.json()["new_credit"])
        print(f"\tSaldo actualizado a {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    r = requests.post(f"{CATALOG}/cart/checkout", headers=headers_alice)
    if ok("Checkout del carrito", r.status_code == HTTPStatus.OK and r.json()):
        data = r.json()
        print(f"\tPedido {data['orderid']} creado correctamente:")

        r = requests.get(f"{CATALOG}/orders/{data['orderid']}", headers=headers_alice)
        if ok(f"Recuperar datos del pedido {data['orderid']}", r.status_code == HTTPStatus.OK and r.json()):
            order = r.json()
            print(f"\tFecha: {order['date']}\n\tPrecio: {order['total']}")
            print("\tContenidos:")
            for movie in order['movies']:
                    print(f"\t- [{movie['movieid']}] {movie['title']} ({movie['price']})")
        
        r = requests.get(f"{CATALOG}/cart", headers=headers_alice)
        ok("Obtener carrito vacío después de la venta", r.status_code == HTTPStatus.OK and not r.json())

    
    print("# =======================================================")
    print("# Limpiar base de datos")
    print("# =======================================================")
    
    r = requests.delete(f"{USERS}/user/{uid_alice}", headers=headers_admin)
    ok("Borrar usuario alice", r.status_code == HTTPStatus.OK)

    r = requests.delete(f"{USERS}/user/{uid_alice}", headers=headers_admin)
    ok("Borrar usuario inexistente", r.status_code == HTTPStatus.NOT_FOUND)

    print("\nPruebas completadas.")

if __name__ == "__main__":
    main()
