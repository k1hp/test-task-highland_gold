import fastapi, uvicorn

from backend.app.models import Base
from backend.app.database import engine


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    app = fastapi.FastAPI()
    uvicorn.run(app, host="0.0.0.0", port=8000)