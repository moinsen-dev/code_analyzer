FROM python:3.13-slim

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Install Refactoroscope
RUN uv pip install refactoroscope

# Set entrypoint
ENTRYPOINT ["refactoroscope"]