FROM python:3.11-slim

WORKDIR /app

#PYTHONDONTWRITEBYTECODE=1 -> When Python imports a file, it creates a compiled version called a bytecode file. This tells docker "Don't create those .pyc files."
#PYTHONUNBUFFERED=1 -> Print output immediately. Makes Docker logs appear in real time
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

#required dependencies
COPY pyproject.toml ./

#optional dependencies inside pyproject.toml
RUN pip install --no-cache-dir '.[dev]'

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]