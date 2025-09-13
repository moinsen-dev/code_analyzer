FROM python:3.13-slim

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Install code_analyzer
RUN uv pip install code_analyzer

# Set entrypoint
ENTRYPOINT ["code_analyzer"]