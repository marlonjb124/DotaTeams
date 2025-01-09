import uvicorn
# from database.database import Base,engine
from fastapi import FastAPI
from routers.profile import profilerouter
from routers.user import userRouter
from routers.team import teamRouter
from routers.tournaments import tournament_router
app = FastAPI()
app.include_router(profilerouter)
app.include_router(userRouter)
app.include_router(teamRouter)
app.include_router(tournament_router)
# Base.metadata.create_all(bind=engine)

if __name__=="__main__" :
    uvicorn.run("main:app", port=8000, log_level="info")
