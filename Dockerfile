FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y \
    redis-server && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

EXPOSE 8000

CMD ["sh", "-c", "redis-server --daemonize yes && cd scraper && uvicorn runner:app --host 0.0.0.0 --port 8000"]

# <!-- docker tag fastapi-scraper ragehelix/fastapi-scraper:v1 -->
# <!-- docker push ragehelix/fastapi-scraper:v1 -->
