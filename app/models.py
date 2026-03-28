from pydantic import BaseModel


class EIP712VariableData(BaseModel):
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
