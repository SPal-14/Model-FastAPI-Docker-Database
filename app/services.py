from typing import TYPE_CHECKING, List

import app.database as _database
import app.models as _models
import app.schemas as _schemas

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def _add_tables():
    return _database.Base.metadata.create_all(bind=_database.engine)


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def create_contact(
    contact: _schemas.CreateContact, db: "Session"
) -> _schemas.Contact:
    contact = _models.Contact(**contact.dict())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return _schemas.Contact.from_orm(contact)


async def get_all_contacts(db: "Session") -> List[_schemas.Contact]:
    contacts = db.query(_models.Contact).all()
    return list(map(_schemas.Contact.from_orm, contacts))


async def get_contact(contact_id: int, db: "Session"):
    contact = db.query(_models.Contact).filter(_models.Contact.id == contact_id).first()
    return contact
async def get_result(result_id: int, db: "Session"):
    contact = db.query(_models.Result).filter(_models.Result.ID == result_id).first()
    return contact


async def delete_contact(contact: _models.Contact, db: "Session"):
    db.delete(contact)
    db.commit()

async def delete_result(result: _models.Result, db: "Session"):
    db.delete(result)
    db.commit()

async def update_contact(
    contact_data: _schemas.CreateContact, contact: _models.Contact, db: "Session"
) -> _schemas.Contact:
    contact.name = contact_data.name
    contact.email = contact_data.email
    contact.age = contact_data.age
    contact.gender = contact_data.gender

    db.commit()
    db.refresh(contact)

    return _schemas.Contact.from_orm(contact)
