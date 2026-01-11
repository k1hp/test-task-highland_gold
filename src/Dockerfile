FROM ubuntu:22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-qgis \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

ENV PYTHONPATH=/usr/share/qgis/python:$PYTHONPATH
ENV QT_QPA_PLATFORM=offscreen

CMD ["python3", "run_all_tests.py"]