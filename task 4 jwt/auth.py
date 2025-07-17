from passlib.context import CryptContext

# Настройка контекста хеширования
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Хеширование пароля
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Проверка пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
