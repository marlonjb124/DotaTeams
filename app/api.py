# import uvicorn
# from database.database import Base,engine
from fastapi import FastAPI,Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.routers.profile import profilerouter
from app.routers.user import userRouter
from app.routers.team import teamRouter
from fastapi.middleware.cors import CORSMiddleware
# from mangum import Mangum
from app.routers.tournaments import tournament_router
# from app.routers.user import userRouter

# Import v1 routers
from app.routers.v1.user import userRouter as v1_user_router
from app.routers.v1.team import teamRouter as v1_team_router
from app.routers.v1.tournaments import tournament_router as v1_tournament_router
from app.routers.v1.profile import profile_router as v1_profile_router

limiter = Limiter(key_func=get_remote_address,default_limits=["10 per minute"])
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Manejador de excepciones para cuando se excede el límite de solicitudes
@app.exception_handler(RateLimitExceeded)
async def ratelimit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        content={"detail": "Rate limit exceeded. Try again later."},
        status_code=429 )   
        
# Include existing routers (for backward compatibility during transition)
# app.include_router(profilerouter)
# app.include_router(userRouter)
# app.include_router(teamRouter)
# app.include_router(tournament_router)

# Include v1 routers (new RESTful API with versioning)
app.include_router(v1_user_router)
app.include_router(v1_team_router)
app.include_router(v1_tournament_router)
app.include_router(v1_profile_router)

# handler = Mangum(app)
# Base.metadata.create_all(bind=engine)
@app.get("/")
async def Home():
    return {"message":"Welcome to TeamAPI"}
@app.get("/healthz")
async def check_health():
    return{"status":"ok"}

@app.post("/webhook-test")
async def wh(request:Request):
    print(request.body)
    print(request.headers)
    return 