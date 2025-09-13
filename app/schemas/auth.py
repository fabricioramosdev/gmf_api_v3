from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str #= "fabricio.ramos.dev@gmail.com"
    password: str #= "admin123"


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"
