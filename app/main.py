import uvicorn
# from database.database import Base,engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.profile import profilerouter
from routers.user import userRouter
from routers.team import teamRouter
from mangum import Mangum
from routers.tournaments import tournament_router

app = FastAPI()

# Lista de orígenes permitidos (puedes modificar esto según tus necesidades)
# origins = [
#     "http://localhost:3000",  # Reemplaza con la URL de tu frontend
#     "https://yourfrontend.com",  # Agrega otras URLs permitidas
#     "*",  # Esto permite solicitudes desde cualquier origen, si es necesario
# ]
@app.get("/")
async def home():
    return {"Exito": "Exito"}
# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)
app.include_router(profilerouter)
app.include_router(userRouter)
app.include_router(teamRouter)
app.include_router(tournament_router)
handler = Mangum(app)
# Base.metadata.create_all(bind=engine)
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8080)
# if __name__=="__main__" :
#     uvicorn.run("main:handler", port=8000, log_level="info")
