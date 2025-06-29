# Use Python 3.12 base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/

# Set Python path to include src directory
ENV PYTHONPATH=/app/src/lambda

# Default command to run tests
CMD ["python", "-m", "unittest", "tests.test_search_word_receiver", "-v"]