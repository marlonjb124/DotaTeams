import uvicorn
from database.database import Base,engine
from fastapi import FastAPI
from routers.profile import profilerouter
from routers.user import userRouter
from routers.team import teamRouter
app = FastAPI()
app.include_router(profilerouter)
app.include_router(userRouter)
app.include_router(teamRouter)
Base.metadata.create_all(bind=engine)

# if __name__=="__main__" :
#      uvicorn.run(app, port=8000)
