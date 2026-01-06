from pydantic import BaseModel, field_validator, Field
from pydantic.types import PositiveFloat


class HoleSchema(BaseModel):
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


class AssaySchema(BaseModel):
    name: str
    from_: float = Field(alias="_from")
    to_: float = Field(alias="_to")
    Au: PositiveFloat
