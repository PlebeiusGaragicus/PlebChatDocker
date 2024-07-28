import dotenv
dotenv.load_dotenv()

from src.logger import setup_logging, logger
setup_logging()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.database import connect_to_mongo, close_mongo_connection
from src.routes import user_routes #, admin_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:5522",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

# Include the user and admin routers
# app.include_router(user_routes.router, prefix="/user", tags=["user"])
# app.include_router(admin_routes.router, prefix="/admin", tags=["admin"])
app.include_router(user_routes.router)
# app.include_router(admin_routes.router)


@app.get("/health")
def read_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, "path"):
            routes.append(
                {
                    "route": route.path,
                    "method": route.methods
                })
    return {"routes": routes}




# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=5101)
