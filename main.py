from typing import TYPE_CHECKING, List
import fastapi as _fastapi
import sqlalchemy.orm as _orm
import app.database as _db
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.model.model import predict_pipeline
from app.model.model import __version__ as model_version
import app.schemas as _schemas
import app.services as _services

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

app = _fastapi.FastAPI()

@app.get("/")
def read_root():
    return {"health_check": "OK", "model_version": model_version}

@app.post("/api/contacts/", response_model=_schemas.Contact)
async def create_contact(
    contact: _schemas.CreateContact,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    return await _services.create_contact(contact=contact, db=db)


@app.put("/detect_language/{id}")
def detect_language(id: int, file: UploadFile = File(...)):
    db = _db.SessionLocal()
    l=id
    id = db.execute("SELECT id FROM contacts WHERE id = :id", {"id": id}).fetchone()
    if id is None:
         return {"error": "Contact not found"}
    # # content = result[0].decode('latin-1')
    # # clean_byte_string = result[0].translate(None, 'result[0]')
    
    result=file.file.read()
    decoded_string = result.decode('utf-8', errors='replace')
    language = predict_pipeline(decoded_string)
    db.execute("INSERT INTO results (ID, RESULT) VALUES (:ID, :RESULT)", {"ID": l, "RESULT": language})
    db.commit()
    return {"language": language}
