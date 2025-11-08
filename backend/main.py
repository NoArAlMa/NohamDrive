from fastapi import FastAPI

app = FastAPI(title="OneDrive Alternative API", version="0.1.0")

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API OneDrive Alternative !"}