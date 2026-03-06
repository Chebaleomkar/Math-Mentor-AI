from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="Math Mentor AI")

app.include_router(router)