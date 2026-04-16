"""
Генерация ключей и операции ЭЦП через cryptography (RSA + SHA-256).
Ключи сервера генерируются один раз при старте и живут в памяти.
"""

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature
import base64


def generate_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key, private_key.public_key()


def sign(message: str, private_key) -> str:
    """Подписать сообщение, вернуть подпись в base64."""
    signature = private_key.sign(
        message.encode(),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode()


def verify(message: str, signature_b64: str, public_key) -> bool:
    """Проверить подпись. Вернуть True если валидна."""
    try:
        public_key.verify(
            base64.b64decode(signature_b64),
            message.encode(),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature:
        return False


def public_key_to_pem(public_key) -> str:
    return public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()


def public_key_from_pem(pem: str):
    return serialization.load_pem_public_key(pem.encode())
