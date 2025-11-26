------------------------------------------------------------
-- OPTIMIZACIÓN /estadisticaVentas/<año>/<pais>
-- Práctica 3 - Si1
------------------------------------------------------------

-- 1. PLAN DE EJECUCIÓN ANTES DE OPTIMIZAR
EXPLAIN ANALYZE
SELECT 
    o.order_id, o.uuid_user, o.order_date, o.total
FROM orders o
JOIN users u ON u.uuid_user = o.uuid_user
WHERE EXTRACT(YEAR FROM o.order_date) = 2024
  AND u.nationality = 'España';

------------------------------------------------------------
-- 2. CREACIÓN DE ÍNDICES
------------------------------------------------------------

-- Acelera filtro por nacionalidad
CREATE INDEX IF NOT EXISTS idx_users_nationality
ON users(nationality);

-- Acelera el JOIN entre orders y users
CREATE INDEX IF NOT EXISTS idx_orders_uuid_user
ON orders(uuid_user);

-- Acelera búsqueda por fecha (para rango)
CREATE INDEX IF NOT EXISTS idx_orders_order_date
ON orders(order_date);

-- Alternativa: índice funcional si no se modifica la consulta
-- CREATE INDEX idx_orders_year
-- ON orders((EXTRACT(YEAR FROM order_date)));


------------------------------------------------------------
-- 3. PLAN DE EJECUCIÓN TRAS OPTIMIZAR
------------------------------------------------------------

EXPLAIN ANALYZE
SELECT 
    o.order_id, o.uuid_user, o.order_date, o.total
FROM orders o
JOIN users u ON u.uuid_user = o.uuid_user
WHERE EXTRACT(YEAR FROM o.order_date) = 2024
  AND u.nationality = 'España';
