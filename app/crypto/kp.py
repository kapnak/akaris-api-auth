import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from app.config import config


def load(path: str, password: str):
    """Load ECDSA private key from PEM file."""

    if not os.path.exists(path):
        raise FileNotFoundError(f'Unable to read "{path}" private key.')

    with open(path, 'rb') as f:
        private_key = serialization.load_pem_private_key(f.read(), password=password.encode())

    return private_key


def generate(path: str, password: str):
    """Generate a new SECP256R1 private key."""

    private_key = ec.generate_private_key(ec.SECP256R1())
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode())
    )
    with open(path, 'wb') as f:
        f.write(pem)


if __name__ == '__main__':
    generate(config.JWT_PRIVATE_KEY_PATH, config.JWT_PRIVATE_KEY_PASSWORD)
