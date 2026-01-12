from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from typing import List, Optional


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = 'projects'
    project_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    images: Mapped[List["Image"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Image(Base):
    __tablename__ = 'images'
    image_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    filename: Mapped[str] = mapped_column(nullable=False)  # уникальное имя (uuid.jpg)
    original_filename: Mapped[str] = mapped_column(nullable=False)  # оригинальное имя от пользователя
    file_path: Mapped[str] = mapped_column(nullable=False, unique=True)
    public_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.project_id', ondelete="CASCADE"))
    project: Mapped[Project] = relationship(back_populates='images')