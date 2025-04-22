from pydantic import BaseModel, StrictStr

class AuthResponse(BaseModel):
    access_token: StrictStr
    token_type: StrictStr