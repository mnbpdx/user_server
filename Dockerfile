FROM python:3.10-slim

WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml ./

# Install dependencies from pyproject.toml
RUN pip install --no-cache-dir .[test]

# Copy all application code
COPY . ./

EXPOSE 5003

CMD ["python", "app.py"]
