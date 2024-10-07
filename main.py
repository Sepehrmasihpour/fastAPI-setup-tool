import os


class FastApiSetup:
    def __init__(self, project_name: str) -> None:
        self.project_name = project_name
        self.folders = [
            f"{self.project_name}",
            f"{self.project_name}/src",
            f"{self.project_name}/src/core",
            f"{self.project_name}/src/db",
            f"{self.project_name}/src/models",
            f"{self.project_name}/src/modules",
            f"{self.project_name}/src/tests",
        ]
        self.files = {
            f"{self.project_name}/pyproject.toml": """[tool.poetry]
name = fastApiProject
version = "0.1.0"
description = ""
authors = ""
readme = "README.md"
packages = [{ include = "src" }]

[tool.poetry.dependencies]
python = "^3.11"
pydantic = "^2.8.2"
python-dotenv = "^1.0.1"
fastapi = "^0.112.0"
uvicorn = "^0.30.5"
gunicorn = "^23.0.0"
pyjwt = "^2.9.0"
pyotp = "^2.9.0"
pytest-asyncio = "^0.24.0"
pytest-mock = "^3.14.0"
passlib = "^1.7.4"
bcrypt = ">=3.1.0,<4.0.0"
python-multipart = "^0.0.10"


[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.scripts]
start = "src.main:main"
""",
            f"{self.project_name}/.dockerignore": """__pycache__
.py[cod]
.venv
.git
.gitignore
Dockerfile
docker-compose.yml
README.md
.example.env
*_cache
tests/
""",
            f"{self.project_name}/.example.env": """API_KEY = ...
SECRET_KEY = ...
PROXY_URL = ...
DB_USER_NAME = ...
DB_PASSWORD = ...
DB_HOST = ...
DB_NAME = ...
SMS_SERVICE_API_KEY = ...
WEBSERVER_PORT = ...
WEBSERVER_HOST = ...
""",
            f"{self.project_name}/.gitignore": """.env
__pycache__
..env.swp
.venv
*.swp
cache/
""",
            f"{self.project_name}/docker-compose.yml": "",
            f"{self.project_name}/Dockerfile": "",
            f"{self.project_name}/main.py": """import subprocess
from fastapi import HTTPException
from src.config import settings

# from src.api import auth, complaint, user
# from src.db.redis_control import RedisControll
from src.app_instance import app as fastapi_app

# from src.tests.api import auth_tests, user_tests

app = fastapi_app
# app.include_router(auth.router, prefix="/auth", tags=["auth"])
# app.include_router(user.router, prefix="/user", tags=["user"])
# app.include_router(complaint.router, prefix="/complaint", tags=["complaints"])
# app.include_router(auth_tests.tests_router, prefix="/test/auth", tags=["tests"])
# app.include_router(user_tests.tests_router, prefix="/test/user", tags=["tests"])


#! Make sure this is completed and run the tests whenever this is called and give a report as response
@app.get("/healthcheck")
async def health_check():
    health_status = {}

    # Check Redis
    # try:
    #     await RedisControll.client.ping()
    #     health_status["redis"] = "healthy"
    # except Exception as e:
    #     health_status["redis"] = f"unhealthy: {e}"

    # Determine overall status
    if all(status == "healthy" for status in health_status.values()):
        return {"status": "healthy", "details": health_status}
    else:
        raise HTTPException(
            status_code=503, detail={"status": "unhealthy", "details": health_status}
        )


def main():
    command = [
        "gunicorn",
        "-w",
        str(settings.worker_count),  # Separate the flag and value
        "-k",
        "uvicorn.workers.UvicornWorker",
        "--bind",
        f"{settings.webserver_host}:{settings.webserver_port}",
        "main:app",
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:

        print(f"An error occurred while running Gunicorn: {e}")


if __name__ == "__main__":
    main()
""",
            f"{self.project_name}/README.md": "",
            f"{self.project_name}/src/__init__.py": "",
            f"{self.project_name}/src/app_instance.py": """from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager
# from src.core.jibit_client import JibitClient
# from src.db import db_client

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the JibitClient instance #!uncomment this when the server are back on for the jibit client
    # jibit_client = JibitClient(
    #     refresh_interval_hours=5
    # )  # Adjust the interval as needed
    # app.state.jibit_client = jibit_client
    print("JibitClient initialized and running background token refresh.")

    try:
        yield
    finally:
        # Ensure the background task is cancelled on shutdown
        # await app.state.jibit_client.close() #!uncomment this when the server are back on for the jibit client
        print("JibitClient shutdown gracefully.")
        # db_client.close_client()
        print("The connection with the mongo db close gracefully")


app = FastAPI(lifespan=lifespan)

#!uncomment this when the server are back on for the jibit client
# def get_jibit_client(request: Request) -> JibitClient:
#     """
            #     Dependency to retrieve the JibitClient instance from app state.
            #     """
            #     jibit_client = request.app.state.jibit_client
            #     if not jibit_client._access_token:
            #         raise HTTPException(
            #             status_code=500, detail="JibitClient not initialized properly."
            #         )
            #     return jibit_client
            """
""",
            f"{self.project_name}/src/config.py": """from dotenv import load_dotenv
from urllib.parse import quote_plus
from os import getenv
import multiprocessing

load_dotenv()


class Settings:

    # * These two bellow are for accessing the jibit api
    # jibit_api_key = getenv("JIBIT_API_KEY")
    # jibit_secret_key = getenv("JIBIT_SECRET_KEY")

    # * For running code through the server on a proxy, as jibit requires all requests to go thorugh a dedicated ip
    server_proxy_url = getenv("PROXY_URL")

    # * these are the credentials for accessing the mongodb
    db_user_name = quote_plus(getenv("MONGODB_USER_NAME"))
    db_password = quote_plus(getenv("MONGODB_PASSWORD"))
    db_uri = f"mongodb://{db_user_name}:{db_password}@mongo:27017"

    # * The code for the jwt auth
    jwt_secret = getenv("SECRET_KEY")
    jwt_access_secs = int(getenv("JWT_ACCESS_SECS"))
    jwt_refresh_secs = int(getenv("JWT_REFRESH_SECS"))
    jwt_algorithm = getenv("JWT_ALGORITHM")

    # * the config for the app itself
    webserver_port = getenv("WEBSERVER_PORT")
    webserver_host = getenv("WEBSERVER_HOST")
    worker_count = multiprocessing.cpu_count() * 2 + 1
    broker_uri = getenv("BROKER_URI")

    # * config for the sms service
    sms_service_api_key = getenv("SMS_SERVICE_API_KEY")

    # * config for the reddis db
    redis_url = getenv("REDIS_URL")

    # * config for the postGIS db
    postgres_user = getenv("POSTGRES_USER")
    postgres_password = getenv("POSTGRES_PASSWORD")
    postgres_db = getenv("POSTGRES_DB")
    postgres_url = (
        f"postgresql://{postgres_user}:{postgres_password}@postgis:5432/{postgres_db}"
    )


settings = Settings()
""",
            f"{self.project_name}/src/api/__init__.py": "",
            f"{self.project_name}/src/core/__init__.py": "",
            f"{self.project_name}/src/db/__init__.py": "",
            f"{self.project_name}/src/models/__init__.py": "",
            f"{self.project_name}/src/modules/__init__.py": "",
            f"{self.project_name}/src/tests/__init__.py": "",
        }

    def setup(self):
        for folder in self.folders:
            os.makedirs(folder, exist_ok=True)
            print(f"created directory: {folder}")

        for file_path, content in self.files.items():
            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                f.write(content)
            print(f"Created file: {file_path}")


if __name__ == "__main__":
    setup_tool = FastApiSetup(project_name="test")
    setup_tool.setup()
