"""
security.py
===========
Utilidades de seguridad para AutoGest, como el hashing de contraseñas.
"""
import bcrypt

def hash_password(password: str) -> str:
    """
    Toma una contraseña en texto plano y retorna un hash seguro usando bcrypt.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica que la contraseña en texto plano coincida con el hash almacenado.
    Tiene un mecanismo de fallback (retrocompatibilidad) para contraseñas 
    antiguas que aún estén en texto plano en la base de datos de Oracle.
    """
    try:
        # Los hashes de bcrypt suelen empezar con $2b$, $2a$ o $2y$
        if hashed_password.startswith("$2"):
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        else:
            # Fallback temporal: si la BD tiene texto plano (ej. "admin123")
            return plain_password == hashed_password
    except Exception:
        return False
