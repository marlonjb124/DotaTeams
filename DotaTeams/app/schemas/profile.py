

from pydantic import BaseModel
class Profile(BaseModel):
    # user_id:int
    nickname:str

    class Config:
        from_attributes = True
class ProfileReturn(Profile):
    user_id:int
    id:int
    nickname:str
    class Config:
        from_attributes = True