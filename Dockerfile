# ---- Stage 1: Build Endee from source ----
FROM ubuntu:22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    cmake build-essential libssl-dev libcurl4-openssl-dev \
    unzip curl git wget gnupg lsb-release software-properties-common \
    && wget https://apt.llvm.org/llvm.sh && chmod +x llvm.sh && ./llvm.sh 19 && rm llvm.sh \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN chmod +x install.sh && ./install.sh --release --avx2 --skip-deps

# ---- Stage 2: Runtime ----
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libssl3 libcurl4 curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy built Endee binary and symlink
COPY --from=builder /app/build/ndd* /app/build/
RUN chmod +x /app/build/ndd*

# Copy application code
COPY ai_resume_selector/ /app/ai_resume_selector/
COPY start.sh /app/start.sh
COPY .env.example /app/.env.example

# Install Python deps
RUN pip install --no-cache-dir -r /app/ai_resume_selector/requirements.txt

# Create data directory for Endee
RUN mkdir -p /app/data

# Expose ports
EXPOSE 7860

# Make start script executable
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
