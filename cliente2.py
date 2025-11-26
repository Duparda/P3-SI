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
    # 4. Obtener catálogo de películas
    # ==========================================================
    print("# Listado general de películas")
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
    r = requests.get(f"{CATALOG}/estadisticaVentas/2024/España", headers=headers)
    ok("Consulta estadística", r.status_code == HTTPStatus.OK)

    # ==========================================================
    # 15. Clientes sin pedidos
    # ==========================================================
    print("\n# Clientes sin pedidos")
    r = requests.get(f"{CATALOG}/clientesSinPedidos", headers=headers)
    ok("Consultar clientes sin pedidos", r.status_code == HTTPStatus.OK)

    print("\n==============================================")
    print("           TESTER COMPLETADO")
    print("==============================================\n")


if __name__ == "__main__":
    main()
