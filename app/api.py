# import uvicorn
# from database.database import Base,engine
from fastapi import FastAPI

from app.routers.profile import profilerouter
from app.routers.user import userRouter
from app.routers.team import teamRouter
# from mangum import Mangum
from app.routers.tournaments import tournament_router
# from app.routers.user import userRouter

app = FastAPI()

app.include_router(profilerouter)
app.include_router(userRouter)
app.include_router(teamRouter)
app.include_router(tournament_router)
# handler = Mangum(app)
# Base.metadata.create_all(bind=engine)
@app.get("/")
async def Home():
    return {"message":"Welcome to the API"}
@app.get("/healthz")
async def check_health():
    return{"status":"ok"}

