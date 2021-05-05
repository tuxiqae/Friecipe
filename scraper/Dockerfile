FROM python:3.9.5
# Allows the service to print to STDOUT without buffering
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml .
RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry install
COPY . .
