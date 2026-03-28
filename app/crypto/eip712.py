import time
from cachetools import TTLCache
from eth_account.messages import encode_typed_data
from eth_account import Account
from app.models import DomainData, MessageData, EIP712VariableData
from app.config import config
from dataclasses import dataclass

ttl = 120
used_jtis = TTLCache(maxsize=10_000, ttl=ttl)


@dataclass
class VerificationResponse:
    valid: bool
    message: str


def verify_signature(
        address: str,
        signature: str,
        message: MessageData,
        domain: DomainData
) -> VerificationResponse:
    """Verify EIP-712 typed data signature"""

    if domain.name != config.APP_NAME:
        return VerificationResponse(valid=False, message=f'Domain name must be "{config.APP_NAME}"')
    if domain.version != config.APP_VERSION:
        return VerificationResponse(valid=False, message=f'Domain version must be "{config.APP_VERSION}"')
    if message.message != config.EIP_MESSAGE:
        return VerificationResponse(valid=False, message=f'Message is incorrect.')
    if (message.timestamp + ttl) < time.time():
        return VerificationResponse(valid=False, message=f'Message timestamp too old.')
    jti_key = message.address + message.jti
    if jti_key in used_jtis:
        return VerificationResponse(valid=False, message=f'JTI already used.')

    try:
        typed_data = generate_typed_data(EIP712VariableData(
            address=message.address,
            timestamp=message.timestamp,
            jti=message.jti
        ))
        encoded_data = encode_typed_data(full_message=typed_data)
        recovered_address = Account.recover_message(
            encoded_data,
            signature=signature
        )
        used_jtis[jti_key] = True
        if recovered_address.lower() != address.lower():
            return VerificationResponse(valid=False, message='Provided address and recovered address don\'t match.')
        return VerificationResponse(valid=True, message='')
    except Exception as e:
        print(f"Signature verification error: {e}")
        return VerificationResponse(valid=False, message='Signature invalid.')


def generate_typed_data(
        variable_data: EIP712VariableData
):
    return {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"}
            ],
            "Authentication": [
                {"name": "message", "type": "string"},
                {"name": "address", "type": "address"},
                {"name": "timestamp", "type": "uint256"},
                {"name": "jti", "type": "string"}
            ]
        },
        "primaryType": "Authentication",
        "domain": {
            "name": config.APP_NAME,
            "version": config.APP_VERSION
        },
        "message": {
            "message": config.EIP_MESSAGE,
            "address": variable_data.address,
            "timestamp": variable_data.timestamp,
            "jti": variable_data.jti
        }
    }