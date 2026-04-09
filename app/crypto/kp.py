import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


def load(key_b64: str):
    """Load ECDSA private key from base64 DER string."""
    try:
        key_der = base64.b64decode(key_b64)
        return serialization.load_der_private_key(key_der, password=None)
    except Exception as e:
        raise ValueError(f"Failed to load private key: {e}")


def generate():
    """Generate a new SECP256R1 private key and return its base64 DER representation."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    der = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    return base64.b64encode(der).decode('utf-8')


if __name__ == '__main__':
    print(generate())
