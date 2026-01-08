from pydantic import BaseModel, field_validator, Field
from pydantic.types import PositiveFloat
import math


class EmptyFieldMixin:
    @field_validator("*", mode="before")
    def no_empty_excel_values(cls, v):
        if v is None:
            raise ValueError("Поле не может быть пустым")

        if isinstance(v, float) and math.isnan(v):
            raise ValueError("Поле не может быть пустым")

        if isinstance(v, str) and not v.strip():
            raise ValueError("Поле не может быть пустым")

        return v



class HoleSchema(BaseModel, EmptyFieldMixin):
    name: str
    x: float
    y: float
    z: float
    lenght: PositiveFloat
    level_: PositiveFloat = Field(alias="_level")
    issue_date: str

    @field_validator("issue_date", mode="before")
    @classmethod
    def convert_issue_date(cls, value):
        """Конвертирует issue_date в строку из другого типа"""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return str(int(value))
        return str(value)


class AssaySchema(BaseModel, EmptyFieldMixin):
    name: str
    from_: float = Field(alias="_from")
    to_: float = Field(alias="_to")
    Au: PositiveFloat
