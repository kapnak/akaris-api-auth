from pydantic import BaseModel


class EIP712VariableData(BaseModel):
    """
    Represents variable data for EIP-712 typed data generation.
    """
    address: str
    timestamp: int
    jti: str


class MessageData(BaseModel):
    message: str
    address: str
    timestamp: int
    jti: str


class DomainData(BaseModel):
    name: str
    version: str


class EIP712AuthRequest(BaseModel):
    address: str
    signature: str
    message: MessageData
    domain: DomainData


class AuthResponse(BaseModel):
    jwt: str


class EIP712TypeField(BaseModel):
    name: str
    type: str


class EIP712TypedDataResponse(BaseModel):
    types: dict[str, list[EIP712TypeField]]
    primaryType: str
    domain: DomainData
    message: MessageData
