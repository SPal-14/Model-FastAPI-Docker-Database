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

@app.post("/api/create_contacts/", response_model=_schemas.Contact)
async def create_contact(
    contact: _schemas.CreateContact,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    return await _services.create_contact(contact=contact, db=db)


@app.put("/api/detect_languages/{id}")
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
 
@app.get("/api/read_results/{id}")
def read_result(id:str):
    db = _db.SessionLocal()
    l=id
    id = db.execute("SELECT ID FROM results WHERE ID = :id", {"id": id}).fetchone()
    if id is None:
         return {"error": "Contact not found"}
    result='a'
    while(result != None):
        result = db.execute("SELECT RESULT FROM results WHERE ID = :id", {"id": l}).fetchone()
        return{result}
    
# @app.post("/update_result{id}")
# def read_result(id:int):
#     db = _db.SessionLocal()
#     id1 = db.execute("SELECT id FROM contacts WHERE id = :id", {"id": id}).fetchone()
#     if id1 is None:
#          return {"error": "Contact not found"}
    

#     result = db.execute("SELECT * FROM contacts WHERE id = :id", {"id": id}).fetchone()
#     return{result}

# @app.get("/api/contacts/{contact_id}/", response_model=_schemas.Contact)
# async def get_contact(
#     contact_id: int, db: _orm.Session = _fastapi.Depends(_services.get_db)
# ):
#     contact = await _services.get_contact(db=db, contact_id=contact_id)
#     if contact is None:
#         raise _fastapi.HTTPException(status_code=404, detail="Contact does not exist")

#     return contact


@app.put("/api/update_contacts/{id}/", response_model=_schemas.Contact)
async def update_contact(
    id: int,
    contact_data: _schemas.CreateContact,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    contact = await _services.get_contact(db=db, contact_id=id)
    if contact is None:
        raise _fastapi.HTTPException(status_code=404, detail="Contact does not exist")

    return await _services.update_contact(
        contact_data=contact_data, contact=contact, db=db
    )

@app.delete("/delete_contacts/{id}/")
async def delete_contact(
    id: int, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    contact = await _services.get_contact(db=db, contact_id=id)
    results= await _services.get_result(db=db, result_id=id)
    
    if contact is None:
         raise _fastapi.HTTPException(status_code=404, detail="Contact does not exist")
    await _services.delete_contact(contact, db=db)
    if results is None:
         raise _fastapi.HTTPException(status_code=404, detail="Result does not exist")
    await _services.delete_result(results, db=db)

    return "successfully deleted the user"

