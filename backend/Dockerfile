FROM python:3.12-alpine

WORKDIR /backend

RUN pip install --no-cache-dir uv

COPY ./pyproject.toml ./uv.lock ./

RUN uv sync

COPY ./app ./app


ENV PYTHONPATH=/backend

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
