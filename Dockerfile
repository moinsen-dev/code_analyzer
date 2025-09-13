FROM python:3.13-slim

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Install codeinsight
RUN uv pip install codeinsight

# Set entrypoint
ENTRYPOINT ["codeinsight"]