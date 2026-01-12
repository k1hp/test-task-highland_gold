from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas


def create_project(db: Session, project: schemas.ProjectCreate) -> models.Project:
    db_project = models.Project(name=project.name)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_projects(db: Session, skip: int = 0, limit: int = 100) -> List[models.Project]:
    return db.query(models.Project).offset(skip).limit(limit).all()


def get_project(db: Session, project_id: int) -> Optional[models.Project]:
    return db.query(models.Project).filter(models.Project.project_id == project_id).first()


def get_project_by_name(db: Session, name: str) -> Optional[models.Project]:
    return db.query(models.Project).filter(models.Project.name == name).first()


def delete_project(db: Session, project_id: int) -> bool:
    project = get_project(db, project_id)
    if not project:
        return False
    db.delete(project)
    db.commit()
    return True


def create_image(
        db: Session,
        filename: str,
        original_filename: str,
        file_path: str,
        public_url: str,
        project_id: int
) -> models.Image:
    db_image = models.Image(
        filename=filename,
        original_filename=original_filename,
        file_path=file_path,
        public_url=public_url,
        project_id=project_id
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def get_images_by_project(db: Session, project_id: int) -> List[models.Image]:
    return db.query(models.Image).filter(models.Image.project_id == project_id).all()


def get_image(db: Session, image_id: int) -> Optional[models.Image]:
    return db.query(models.Image).filter(models.Image.image_id == image_id).first()


def delete_image(db: Session, image_id: int) -> bool:
    image = get_image(db, image_id)
    if not image:
        return False
    db.delete(image)
    db.commit()
    return True