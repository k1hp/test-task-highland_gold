from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


class ProjectBase(BaseModel):
    name: str


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    project_id: int
    created_at: datetime
    images: List["ImageResponse"] = []

    model_config = ConfigDict(from_attributes=True)


class ImageBase(BaseModel):
    original_filename: str


class ImageCreate(ImageBase):
    pass


class ImageResponse(ImageBase):
    image_id: int
    filename: str
    file_path: str
    public_url: str
    project_id: int
    download_url: str
    view_url: str

    model_config = ConfigDict(from_attributes=True)


ProjectResponse.model_rebuild()
