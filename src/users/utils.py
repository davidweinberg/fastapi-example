from passlib.context import CryptContext


passwd_context = CryptContext(
    schemes=['bcrypt']
)


def generate_passwd_hash(password: str) -> str:
    phash = passwd_context.hash(password)
    return phash


def verify_password(password: str, phash: str) -> bool:
    return passwd_context.verify(password, phash)
