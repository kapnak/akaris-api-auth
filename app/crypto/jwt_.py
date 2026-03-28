import jwt
import base64
import logging
from datetime import datetime, timedelta, timezone
from app.config import config
from app.crypto import kp

log = logging.getLogger(__name__)

private_key = kp.load(config.JWT_PRIVATE_KEY_PATH, password=config.JWT_PRIVATE_KEY_PASSWORD)
public_key = private_key.public_key()

log.info(f'Trusted auth public key: {public_key}')


def create_jwt(address: str) -> str:
    """
    Create a JWT token for the authenticated user using ES256
    """
    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=config.JWT_EXPIRATION_HOURS)

    payload = {
        "sub": address.lower(),
        "aud": config.JWT_AUD,
        "exp": int(exp.timestamp()),
        "iat": int(now.timestamp())
    }

    token = jwt.encode(payload, private_key, algorithm='ES256')
    return token


def generate_jwk(pk):
    """Generate the JWK format of a public key."""
    public_numbers = pk.public_numbers()
    x = public_numbers.x.to_bytes(32, byteorder='big')
    y = public_numbers.y.to_bytes(32, byteorder='big')
    x_b64 = base64.urlsafe_b64encode(x).decode('utf-8').rstrip('=')
    y_b64 = base64.urlsafe_b64encode(y).decode('utf-8').rstrip('=')

    return {
        "keys": [
            {
                "kty": "EC",
                "crv": "P-256",
                "x": x_b64,
                "y": y_b64,
                "use": "sig",
                "alg": "ES256",
                "kid": f"{config.APP_NAME}-key-1"
            }
        ]
    }


jwk = generate_jwk(public_key)
