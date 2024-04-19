
from pydantic import BaseModel
class Profile(BaseModel):
    user_id:int
    height: int
    weight: int
    calves: int
    tigth: int
    chest: int
    waist: int
    forearm: int
    arm: int
    neck: int
    shoulders: int
    exercise_pr: int
    gender:str
    age:int

    class Config:
        from_attributes = True
class ProfileReturn(Profile):
    id:int
    height: int
    weight: int
    calves: int
    tigth: int
    chest: int
    waist: int
    forearm: int
    arm: int
    neck: int
    shoulders: int
    exercise_pr: int
    gender:str
    age:int
    icm: float
    bodyFat :float

    class Config:
        from_attributes = True