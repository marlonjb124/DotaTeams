import uvicorn
from database.database import Base,engine
from fastapi import FastAPI
from routers.profile import profilerouter
from routers.user import userRouter

app = FastAPI()
app.include_router(profilerouter)
app.include_router(userRouter)
Base.metadata.create_all(bind=engine)

# if __name__=="__main__" :
#      uvicorn.run(app, port=8000)
