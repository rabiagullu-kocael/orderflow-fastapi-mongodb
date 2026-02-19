from fastapi import FastAPI
from app.routes import router

app = FastAPI()

# Router eklenir
app.include_router(router)
