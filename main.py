from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import redis.asyncio as redis

from src.routes import contacts
from src.routes import users
from src.conf.config import settings

app = FastAPI()

app.include_router(users.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')


origins = [ 
    "http://localhost:8000"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup() -> None: 
    """Initialize connection with redis db.
    :return: None.
    :rtype: None
    """       
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8",
                          decode_responses=True)
    await FastAPILimiter.init(r)


@app.get("/")
def root():
    """Initialize root endpoint.

    :return: Object with message
    :rtype: dict
    """    
    return {"message": "Welcome to FastAPI!"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)