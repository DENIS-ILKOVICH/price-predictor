# app/schemas/pydantic_schemas/post.py
from pydantic import BaseModel, field_validator


class REData(BaseModel):
    district: str
    rooms: int
    floor: int
    floors: int
    area: float
    type: str
    cond: str
    walls: str


    @field_validator('rooms', 'floor', 'floors', 'area', mode='before')
    @classmethod
    def check_numeric(cls, value, field):
        if isinstance(value, str) and not value.isdigit():
            return 0
        return value


    @field_validator('rooms', 'floor', 'floors', mode='before')
    @classmethod
    def convert_to_int(cls, value, field):
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return value

    @field_validator('area', mode='before')
    @classmethod
    def convert_area(cls, value, field):
        if isinstance(value, str) and value.replace('.', '', 1).isdigit():
            return float(value)
        return value
