import uvicorn
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import shutil
import uuid
from pathlib import Path
from typing import List
import mimetypes

from app import models, schemas, crud
from app.database import engine, get_db
from app.config import settings

app = FastAPI(
    title="Project Manager API",
    version="1.0.0",
    description="API for project and image management"
)

# access docs
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # for file download
)

upload_dir = settings.UPLOAD_DIR
app.mount("/static/images", StaticFiles(directory=str(upload_dir)), name="static_images")

def get_project_dir(project_id: int) -> Path:
    project_dir = upload_dir / f"project_{project_id}"
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir

def save_uploaded_file(file: UploadFile, project_id: int) -> tuple[str, str]:
    file_extension = Path(file.filename).suffix or ".jpg"
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    project_dir = get_project_dir(project_id)
    file_path = project_dir / unique_filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return unique_filename, str(file_path)

def delete_project_directory(project_id: int):
    project_dir = upload_dir / f"project_{project_id}"
    if project_dir.exists():
        shutil.rmtree(project_dir)

@app.post(
    "/projects/",
    response_model=schemas.ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new project"
)
def create_project(
        project: schemas.ProjectCreate,
        db: Session = Depends(get_db)
):
    existing_project = crud.get_project_by_name(db, name=project.name)
    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project with name '{project.name}' already exists"
        )
    db_project = crud.create_project(db, project)
    get_project_dir(db_project.project_id)
    return db_project

@app.get(
    "/projects/",
    response_model=List[schemas.ProjectResponse],
    summary="Get all projects"
)
def read_projects(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    return crud.get_projects(db, skip=skip, limit=limit)

@app.get(
    "/projects/{project_id}",
    response_model=schemas.ProjectResponse,
    summary="Get project by ID"
)
def read_project(
        project_id: int,
        db: Session = Depends(get_db)
):
    project = crud.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    return project

@app.delete(
    "/projects/{project_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete project"
)
def delete_project(
        project_id: int,
        db: Session = Depends(get_db)
):
    project = crud.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    delete_project_directory(project_id)
    crud.delete_project(db, project_id)
    return {"message": f"Project '{project.name}' successfully deleted"}

@app.post(
    "/projects/{project_id}/images/",
    response_model=schemas.ImageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload image to project"
)
def upload_image(
        project_id: int,
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    project = crud.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    unique_filename, file_path = save_uploaded_file(file, project_id)
    public_url = f"/static/images/project_{project_id}/{unique_filename}"
    db_image = crud.create_image(
        db=db,
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        public_url=public_url,
        project_id=project_id
    )
    return db_image

@app.get(
    "/projects/{project_id}/images/",
    response_model=List[schemas.ImageResponse],
    summary="Get all project images"
)
def get_project_images(
        project_id: int,
        db: Session = Depends(get_db)
):
    project = crud.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    return crud.get_images_by_project(db, project_id=project_id)

@app.delete(
    "/images/{image_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete image"
)
def delete_image(
        image_id: int,
        db: Session = Depends(get_db)
):
    image = crud.get_image(db, image_id=image_id)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with ID {image_id} not found"
        )
    if os.path.exists(image.file_path):
        os.remove(image.file_path)
    crud.delete_image(db, image_id=image_id)
    return {"message": f"Image '{image.original_filename}' successfully deleted"}

@app.get(
    "/download/image/{image_id}",
    summary="Download image by ID"
)
def download_image_by_id(
        image_id: int,
        db: Session = Depends(get_db)
):
    image = crud.get_image(db, image_id=image_id)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    file_path = Path(image.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found"
        )
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if not mime_type:
        mime_type = "application/octet-stream"
    return FileResponse(
        path=file_path,
        media_type=mime_type,
        filename=image.original_filename
    )

@app.get("/health", summary="API health check")
def health_check():
    return {"status": "healthy", "service": "project-manager-api"}

@app.on_event("startup")
def startup_event():
    try:
        models.Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Could not create tables: {e}")

@app.get("/", summary="API information")
def root():
    return {
        "message": "Project Manager API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "upload_directory": str(upload_dir),
        "endpoints": {
            "projects": {
                "POST": "/projects/",
                "GET": "/projects/",
                "GET by ID": "/projects/{project_id}",
                "DELETE": "/projects/{project_id}"
            },
            "images": {
                "POST": "/projects/{project_id}/images/",
                "GET": "/projects/{project_id}/images/",
                "GET file": "/download/image/{image_id}",
                "DELETE": "/images/{image_id}"
            }
        }
    }