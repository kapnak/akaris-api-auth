import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
from app.crypto import eip712
from app.crypto.jwt_ import create_jwt, jwk
from app.models import EIP712VariableData, EIP712AuthRequest, AuthResponse, EIP712TypedDataResponse
from app.config import config
from app.logger import setup_logging


# Setup logger
setup_logging(
    app_name=config.APP_NAME,
    log_level=config.LOG_LEVEL,
    log_dir=config.LOG_DIR,
    max_bytes=100 * 1024 * 1024,     # 100 MB
    backup_count=100
)


app = FastAPI(title=config.APP_NAME, version=config.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: configure to frontend url
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "ok"}


@app.get("/eip712", response_model=EIP712TypedDataResponse)
async def get_eip712_typed_data(
        eip712_variable_data: EIP712VariableData = Depends()
):
    return eip712.generate_typed_data(eip712_variable_data)


@app.post("/eip712", response_model=AuthResponse)
async def auth_eip712(
        auth_request: EIP712AuthRequest
):
    """
    Authenticate a user by verifying their EIP-712 signature and return a JWT token
    """
    if auth_request.message.address.lower() != auth_request.address.lower():
        raise HTTPException(status_code=400, detail="Message address does not match claimed address")

    verification = eip712.verify_signature(
        address=auth_request.address,
        signature=auth_request.signature,
        message=auth_request.message,
        domain=auth_request.domain
    )

    if not verification.valid:
        raise HTTPException(status_code=401, detail=verification.message)

    return AuthResponse(jwt=create_jwt(address=auth_request.address))


@app.get("/.well-known/jwks.json")
async def jwks():
    """
    JSON Web Key Set endpoint for JWT public key
    This allows clients to verify JWT signatures
    """
    return jwk


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=config.PORT, access_log=False)
