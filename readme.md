To run locally:
1. Clone this repository
2. Install the required dependencies with `pip install -r requirements.txt`
3. Run the app using `cd scraper && uvicorn runner:app --host 0.0.0.0 --port 8000`

To run using Docker:
1. docker pull ragehelix/fastapi-scraper:v1
2. docker run -p 8000:8000 ragehelix/fastapi-scraper:v1

To build and run using Docker:
1. Clone this repository
2. Build the docker image using `docker build -t fastapi-scraper .`
3. Run the docker container using `docker run -p 8000:8000 fastapi-scraper`
