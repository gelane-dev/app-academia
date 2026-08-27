from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import get_db

app = FastAPI(
    title="Academia API",
    description="API gerenciamento de academia",
    version="1.0.0"
)

@app.get("/login")
def root(db: Session = Depends(get_db)):
    return {"message": "API funcionando"}