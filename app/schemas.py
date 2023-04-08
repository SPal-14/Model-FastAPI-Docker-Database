import datetime as _dt
import pydantic as _pydantic
import app.test as _t

class _BaseContact(_pydantic.BaseModel):
    name: str
    email: str
    age: str
    gender: str

class Contact(_BaseContact):
    id: int
    date_created: _dt.datetime

    class Config:
        orm_mode = True


class CreateContact(_BaseContact):
    pass
class UserGet(_BaseContact):
    id: int
