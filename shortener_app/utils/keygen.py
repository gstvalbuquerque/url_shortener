import secrets
import string

from sqlalchemy.orm import Session
from ..services import services


def create_unique_random_key(db: Session) -> str:
    key = create_random_key()
    while services.get_db_url_by_key(db, key):
        key = create_random_key()
    return key


def create_random_key(length: int = 5) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def generate_secret_key(key: str) -> str:
    secret_key = f"{key}_{create_random_key(length=8)}"
    return secret_key
