from quart import Quart, request, jsonify
import uuid
import os
from sqlalchemy import String, Float, Boolean, select
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from hashlib import sha256

import config

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://alumnodb:1234@localhost:9999/si1")
app = Quart(__name__)

engine = create_async_engine(DATABASE_URL, echo = False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

class Users(Base):
    __tablename__ = "users"
    uuid_user: Mapped[str] = mapped_column(primary_key=True)
    namee: Mapped[str] = mapped_column(String(200))
    hash_password: Mapped[str] = mapped_column(String(255))
    rol: Mapped[str] = mapped_column(String(20))
    phone: Mapped[str] = mapped_column(String(20))
    postal_code: Mapped[str] = mapped_column(String(20))
    balance: Mapped[float] = mapped_column(Float, default= 0.0)

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


def generate_token(uid: str):
    token_uuid = uuid.uuid5(config.SECRET_UUID, uid)
    return f"{uid}.{token_uuid}"


@app.put("/user")
async def register_user():

    data = await request.get_json()
    name = data.get("name")
    password = data.get("password")

    if not name or not password:
        return jsonify({"error": "Faltan campos"}), 400
    
    if not is_admin(request.headers):
        return jsonify({"error": "No autorizado"}), 403
    
    rol = data.get("rol", "cliente")
    telefono = data.get("telefono", data.get("phone"))
    codigo_postal = data.get("codigo_postal", data.get("postal_code"))
        
            
    async with async_session() as session:
        # Verificar si el usuario ya existe
        result = await session.execute(select(Users).filter_by(namee=name))
        existing_user = result.scalar_one_or_none()
                
        if existing_user:
            return jsonify({"error": "Usuario ya existe"}), 400
                
        # Crear nuevo usuario
        uid = str(uuid.uuid4())
        
        hashed_password = sha256(password.encode()).hexdigest()
                
        nuevo_usuario = Users(
            uuid_user=uid,
            namee=name,
            hash_password=hashed_password,
            rol=rol,
            phone=telefono,
            postal_code=codigo_postal,
            balance=0.0
        )
                
        session.add(nuevo_usuario)
        await session.commit()
        await session.refresh(nuevo_usuario)

        return jsonify({"uid": uid, "username": name}), 200
        


@app.get("/user")
async def login():
    data = await request.get_json(force=True)
    name = data.get("name") if data else None
    password = data.get("password") if data else None

    if not name or not password:
        return jsonify({"error": "Faltan campos"}), 400

    async with async_session() as session:
        result = await session.execute(select(Users).filter_by(namee=name))
        user = result.scalar_one_or_none()

        if user is None or user.hash_password != sha256(password.encode()).hexdigest():
            return jsonify({"error": "Credenciales inválidas"}), 401

        uid = user.uuid_user
        token = generate_token(uid)
        return jsonify({"uid": uid, "token": token}), 200

@app.put("/user/<name>/password")
async def change_password(name):
    
    data = await request.get_json()
    old_password = data["old_password"]
    new_password = data["new_password"]

    if not old_password or not new_password:
        return jsonify({"error": "Faltan campos"}), 400

    async with async_session() as session:
        result = await session.execute(select(Users).filter_by(namee=name))
        user = result.scalar_one_or_none()

        if user is None or user.hash_password != sha256(old_password.encode()).hexdigest():
            return jsonify({"error": "Credenciales inválidas"}), 401

        user.hash_password = sha256(new_password.encode()).hexdigest()
        session.add(user)
        await session.commit()
        await session.refresh(user)

        return jsonify({"message": "Contraseña actualizada correctamente"}), 200

@app.delete("/user/<uid>")
async def delete_user(uid):
    if not is_admin(request.headers):
        return jsonify({"error": "No autorizado"}), 403

    async with async_session() as session:
        # Búscalo primero para decidir 404 vs 200
        result = await session.execute(select(Users).filter_by(uuid_user=uid))
        user = result.scalar_one_or_none()
        if user is None:
            return jsonify({"error": "Usuario no encontrado"}), 404

        await session.delete(user)
       
        await session.commit()
        
        await session.rollback()

        return jsonify({"message": "Usuario borrado"}), 200
    

@app.get("/health")
async def health():
    return {"status": "ok"}, 200