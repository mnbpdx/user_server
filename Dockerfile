FROM python:3.10-slim

WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml ./

# Install dependencies
RUN pip install --no-cache-dir "flask>=3.1.1" "flask-sqlalchemy>=3.1.1" "pydantic>=2.11.7" "sqlalchemy>=2.0.41" "structlog>=24.5.0" "pytest>=7.0.0" "pytest-flask>=1.2.0" "pytest-cov>=4.0.0" "coverage>=7.0.0"

# Copy all application code
COPY . ./

EXPOSE 5003

CMD ["python", "app.py"]
