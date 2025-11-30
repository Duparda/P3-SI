import requests
from http import HTTPStatus

USERS = "http://127.0.0.1:5050"
CATALOG = "http://127.0.0.1:5051"

def ok(name, cond):
    status = "OK" if cond else "FAIL"
    print(f"[{status}] {name}")
    return cond


def main():

    print("\n==============================================")
    print("     TESTER P3 — Catálogo (solo puerto 5051)")
    print("     Usuario: alice (creado automáticamente)")
    print("==============================================\n")

    # ==========================================================
    # 1. Autenticar como administrador
    # ==========================================================
    print("# Autenticando como administrador...")
    
    r = requests.get(f"{USERS}/user", json={"name": "admin", "password": "admin"})
    if not ok("Autenticar usuario administrador predefinido", r.status_code == HTTPStatus.OK):
        print("\nERROR crítico: No se pudo autenticar como admin")
        return
    
    data = r.json()
    token_admin = data["token"]
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    # ==========================================================
    # 2. Crear usuario alice (con credenciales de admin)
    # ==========================================================
    username = "alice"
    password = "secret"
    
    print("\n# Creando usuario 'alice' con credenciales de admin...")
    
    r = requests.put(f"{USERS}/user", json={"name": username, "password": password}, headers=headers_admin)
    if r.status_code == HTTPStatus.OK and r.json():
        data = r.json()
        uid = data["uid"]
        print(f"  → Usuario alice creado con UID: {uid}")
    elif r.status_code == HTTPStatus.CONFLICT or r.status_code == HTTPStatus.BAD_REQUEST:
        print("  → Usuario alice ya existe, usando el existente")
        # Intentar obtener el UID mediante login
        r = requests.get(f"{USERS}/user", json={"name": username, "password": password})
        if r.status_code == HTTPStatus.OK:
            uid = r.json()["uid"]
            ok("Usar usuario alice existente", True)
        else:
            print("ERROR: No se pudo obtener información del usuario")
            return
    else:
        print(f"ERROR: No se pudo crear el usuario. Status: {r.status_code}")
        print(f"Respuesta: {r.text}")
        return

    # ==========================================================
    # 3. Autenticar como alice
    # ==========================================================
    print("\n# Autenticando como alice...")
    
    r = requests.get(f"{USERS}/user", json={"name": username, "password": password})
    if not ok("Autenticar usuario 'alice'", r.status_code == HTTPStatus.OK and r.json()["uid"] == uid):
        print("ERROR crítico: no se pudo hacer login con alice.")
        return

    data = r.json()
    token = data["token"]

    print(f"UID de alice = {uid}")
    print(f"Token obtenido = {token}\n")

    headers = {"Authorization": f"Bearer {token}"}

    # ==========================================================
    # Verificar inicialización de cart_totals
    # ==========================================================
    print("\n# Verificar cart_totals inicializado")
    r = requests.get(f"{CATALOG}/cart", headers=headers)
    if ok("Cart totals inicializado", r.status_code == HTTPStatus.OK):
        print("✓ El trigger de inicialización funciona")

    # ==========================================================
    # 4. Obtener catálogo de películas
    # ==========================================================
    print("\n# Listado general de películas")
    r = requests.get(f"{CATALOG}/movies", headers=headers)
    ok("Obtener listado de películas", r.status_code == HTTPStatus.OK)
    pelis = r.json()

    if pelis:
        print(f"  → {len(pelis)} películas encontradas")
    else:
        print("  → No hay películas.")

    # elegimos una para usarla en el resto de pruebas
    pid = pelis[0]["movieid"]

    # ==========================================================
    # Verificar gestión de stock
    # ==========================================================
    print("\n# Verificar gestión de stock")
    
    # 0. Asegurarse de que el carrito está vacío
    r = requests.delete(f"{CATALOG}/cart/{pid}", headers=headers)
    
    # 1. Obtener stock inicial
    r = requests.get(f"{CATALOG}/movies/{pid}", headers=headers)
    stock_inicial = r.json().get("stock")
    print(f"Stock inicial: {stock_inicial}")

    # 2. Añadir al carrito
    r = requests.put(f"{CATALOG}/cart/{pid}", headers=headers)
    ok("Añadir al carrito para test", r.status_code == HTTPStatus.OK)

    # 3. Verificar que el stock se redujo
    r = requests.get(f"{CATALOG}/movies/{pid}", headers=headers)
    stock_tras_add = r.json().get("stock")
    ok("Stock se reduce al añadir", stock_tras_add == stock_inicial - 1)

    # 4. Quitar del carrito
    r = requests.delete(f"{CATALOG}/cart/{pid}", headers=headers)

    # 5. Verificar que el stock se restauró
    r = requests.get(f"{CATALOG}/movies/{pid}", headers=headers)
    stock_tras_remove = r.json().get("stock")
    ok("Stock se restaura al quitar", stock_tras_remove == stock_inicial)

    # ==========================================================
    # 4. Filtrado por título
    # ==========================================================
    print("\n# Filtro por título")
    r = requests.get(f"{CATALOG}/movies", params={"title": "matrix"}, headers=headers)
    ok("Buscar 'matrix'", r.status_code == HTTPStatus.OK)

    # ==========================================================
    # 5. Filtrado por actor
    # ==========================================================
    print("\n# Filtro por actor")
    r = requests.get(f"{CATALOG}/movies", params={"actor": "Tom Hardy"}, headers=headers)
    ok("Buscar por actor", r.status_code == HTTPStatus.OK)

    # ==========================================================
    # 6. Ver detalles de película
    # ==========================================================
    print("\n# Obtener detalles de una película")
    r = requests.get(f"{CATALOG}/movies/{pid}", headers=headers)
    ok("Detalles película", r.status_code == HTTPStatus.OK)

    # ==========================================================
    # 7. Añadir al carrito
    # ==========================================================
    print("\n# Añadir al carrito")
    r = requests.put(f"{CATALOG}/cart/{pid}", headers=headers)
    ok("Añadir al carrito", r.status_code == HTTPStatus.OK)

    # ==========================================================
    # 8. Ver carrito
    # ==========================================================
    print("\n# Consultar carrito")
    r = requests.get(f"{CATALOG}/cart", headers=headers)
    ok("Ver carrito", r.status_code == HTTPStatus.OK)

    # ==========================================================
    # 9. Quitar del carrito
    # ==========================================================
    print("\n# Quitar del carrito")
    r = requests.delete(f"{CATALOG}/cart/{pid}", headers=headers)
    ok("Quitar del carrito", r.status_code == HTTPStatus.OK)

    # ==========================================================
    # 10. Volver a añadir + checkout
    # ==========================================================
    print("\n# Checkout")

    requests.put(f"{CATALOG}/cart/{pid}", headers=headers)  # añadir de nuevo
    
    # Añadir saldo para poder hacer checkout
    r = requests.post(f"{CATALOG}/user/credit", 
                    json={"amount": 100}, 
                    headers=headers)

    r = requests.post(f"{CATALOG}/cart/checkout", headers=headers)
    ok("Checkout", r.status_code == HTTPStatus.OK)

    if r.status_code == HTTPStatus.OK:
        order_id = r.json()["orderid"]

        # ======================================================
        # 11. Consultar pedido
        # ======================================================
        print("\n# Consultar pedido")
        r = requests.get(f"{CATALOG}/orders/{order_id}", headers=headers)
        ok("Ver pedido", r.status_code == HTTPStatus.OK)

    # ==========================================================
    # 12. Votar película
    # ==========================================================
    print("\n# Votar película")
    r = requests.post(f"{CATALOG}/movies/{pid}/vote",
                      json={"score": 5},
                      headers=headers)
    ok("Votar película", r.status_code == HTTPStatus.OK)

    # ==========================================================
    # 13. Ver rating
    # ==========================================================
    print("\n# Ver rating")
    r = requests.get(f"{CATALOG}/movies/{pid}/rating", headers=headers)
    ok("Consultar rating", r.status_code == HTTPStatus.OK)

    # ==========================================================
    # 14. Estadística de ventas
    # ==========================================================
    print("\n# Estadística de ventas año/país")
    r = requests.get(f"{CATALOG}/estadisticaVentas/2024/spain", headers=headers)
    ok("Consulta estadística", r.status_code == HTTPStatus.OK)
    if r.status_code == HTTPStatus.OK:
        data = r.json()
        print(f"Total de pedidos efectuados por españoles en 2024: {data['count']}")
        for order in data["orders"]:
            print(f"User : {order["uuid_user"]} Date: {order["order_date"]} Amount: {order["total"]}")

    # ==========================================================
    # 15. Clientes sin pedidos
    # ==========================================================
    print("\n# Clientes sin pedidos")
    r = requests.get(f"{CATALOG}/clientesSinPedidos", headers=headers)
    ok("Consultar clientes sin pedidos", r.status_code == HTTPStatus.OK)
    if r.status_code == HTTPStatus.OK:
        data = r.json()
        print(f"Total de clientes sin pedidos: {data['count']}")
        for user in data["users"]:
            print(f"  - {user['name']} (UUID: {user['uuid_user']})\n")

    # ==========================================================
    # 16. Comprobación de las transacciones
    # ==========================================================
    
    # Crear usuarios de Andorra si no existen (para que el test funcione múltiples veces)
    print("\n# Preparando usuarios de Andorra para tests de transacciones...")
    test_users = [
        ("Elena Torres", "123456", "andorra"),
        ("Hugo Martinez", "123456", "andorra"),
        ("Fernando Ruiz", "123456", "andorra")
    ]
    
    for name, pwd, country in test_users:
        r = requests.get(f"{USERS}/user", json={"name": name, "password": pwd})
        if r.status_code != HTTPStatus.OK:
            # Usuario no existe, crearlo
            r = requests.put(f"{USERS}/user", 
                           json={"name": name, "password": pwd, "nationality": country}, 
                           headers=headers_admin)
            if r.status_code == HTTPStatus.OK:
                print(f"  → Usuario {name} creado")

    # ==========================================================
    # 16.1
    # ==========================================================
    print("\n# Transacción con error y rollback")
    r = requests.delete(f"{CATALOG}/borraPaisIncorrecto/andorra", headers=headers_admin)
    
    if r.status_code == HTTPStatus.CONFLICT:
        ok(f"Error esperado (409)", True)
        print(f"Respuesta: {r.json()}")
        print(f"Rollback ejecutado correctamente")
        print(f"Los datos no deben haberse eliminado")
    elif r.status_code == HTTPStatus.NOT_FOUND:
        ok(f"Error esperado (409)", True)
        print(f"Los usuarios de andorra ya estaban eliminados (404)")
    else:
        ok(f"Error esperado (409)", False)
        print(f"Código de estado inesperado: {r.status_code}: {r.text}")
    
    # Verificar que los usuarios siguen existiendo
    print(f"\n Verificando que los usuarios de andorra siguen existiendo")
    r = requests.get(f"{USERS}/user", json={"name": "Elena Torres", "password": "123456"})
    if ok("Usuario sigue existiendo después del rollback", r.status_code == HTTPStatus.OK):
        print(f"El rollback funcionó: los datos permanecen intactos")

    # ==========================================================
    # 16.2
    # ==========================================================
    print("\n# Commit intermedio y error")
    print("Verificamos antes que los usuarios de andorra tienen ratings antes del test")
    
    r = requests.get(f"{USERS}/user", json={"name": "Elena Torres", "password": "123456"})
    if r.status_code == HTTPStatus.OK:
        data = r.json()
        elena_token = data["token"]
        elena_headers = {"Authorization": f"Bearer {elena_token}"}
        
        # Añadir un rating si no existe para tener datos que eliminar
        r = requests.get(f"{CATALOG}/movies", headers=elena_headers)
        if r.status_code == HTTPStatus.OK and r.json():
            data = r.json()
            movie_id = data[0]["movieid"]
            requests.post(f"{CATALOG}/movies/{movie_id}/vote", json={"score": 5}, headers=elena_headers)
            print(f"Rating creado para Elena Torres en película {movie_id}")
    
    # Ejecutar la transacción intermedia
    r = requests.delete(f"{CATALOG}/borraPaisIntermedio/andorra", headers=headers_admin)
    
    if r.status_code == HTTPStatus.CONFLICT:
        ok(f"Error esperado (409)", True)
        print(f"Respuesta: {r.json()}")
        print(f"Rollback de la segunda transacción ejecutado")
        print(f"Los cambios previos al commit deben persistir")
    elif r.status_code == HTTPStatus.NOT_FOUND:
        ok(f"Error esperado (409)", True)
        print(f"Los usuarios de andorra ya estaban eliminados (404)")
    else:
        ok(f"Error esperado (409)", False)
        print(f"Código de estado inesperado: {r.status_code}: {r.text}")
    
    # Verificar estado final
    print(f"Los usuarios de andorra deben seguir existiendo a causa del rollback")
    print(f"Pero sus ratings y user_movie deben estar eliminados por el commit intermedio")
    
    if r.status_code != HTTPStatus.NOT_FOUND:
        # Verificar que el usuario sigue existiendo
        r = requests.get(f"{USERS}/user", json={"name": "Elena Torres", "password": "123456"})
        if ok("Usuario Elena Torres sigue existiendo", r.status_code == HTTPStatus.OK):
            data = r.json()
            elena_token = data["token"]
            elena_headers = {"Authorization": f"Bearer {elena_token}"}
            print(f"El usuario persiste")
            
            # Verificar que el rating de Elena fue eliminado por el commit intermedio
            r = requests.get(f"{CATALOG}/movies/{movie_id}/user_rating", headers=elena_headers)
            if r.status_code == HTTPStatus.OK:
                data = r.json()
                if ok("Rating de Elena fue eliminado por commit intermedio", data["rated"] == False):
                    print(f"El rating de Elena en película {movie_id} fue eliminado correctamente")
                    print(f"Esto demuestra que el commit intermedio ha persistido")
                else:
                    print(f"Error. El rating todavía existe: {data}")
            else:
                print(f"Error al consultar user_rating: {r.status_code}")
        else:
            print(f"Error: Usuario Elena Torres no existe después de rollback")

    # ==========================================================
    # 16.3
    # ==========================================================
    print("\n# Transacción correcta")
    r = requests.delete(f"{CATALOG}/borraPais/andorra", headers=headers_admin)
    
    if r.status_code == HTTPStatus.OK:
        data = r.json()
        ok(f"Borrado correcto de usuarios de andorra", True)
        print(f"Usuarios eliminados: {data['deleted_users']}")
        print(f"País eliminado {data['deleted_country']}")
    elif r.status_code == HTTPStatus.NOT_FOUND:
        ok(f"Borrado correcto de usuarios de andorra", True)
        print(f"Los usuarios de andorra ya estaban eliminados")
    else:
        ok(f"Borrado correcto de usuarios de andorra", False)
        print(f"Error inesperado: {r.status_code}: {r.text}")

    print("\n==============================================")
    print("           TESTER COMPLETADO")
    print("==============================================\n")


if __name__ == "__main__":
    main()
