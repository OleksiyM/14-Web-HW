"""
API Application
"""

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi_limiter import FastAPILimiter
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from routes import contacts, auth, users
import re
from ipaddress import ip_address
from typing import Callable
from pathlib import Path

import redis.asyncio as redis

from db import get_db
from conf.config import config

app = FastAPI()

# with ip_address
# banned_ips = [
#     ip_address("192.168.0.210"),
#     ip_address("192.168.0.68"),
#     ip_address("10.10.10.10"),
#     ip_address("127.0.0.1")
# ]

# ip_address as string
banned_ips = [
    "192.168.0.210",
    # "192.168.0.68",
    "10.10.10.10",
]

user_agent_ban_list = [r"Somebot", r"Python-urllib"]

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def ban_ips(request: Request, call_next: Callable):
    # with ip_address
    # ip = ip_address(request.client.host)
    # print(f'1: {ip=}')
    # ip_address ass string
    ip = request.client.host
    # print(f'2 {ip=}')
    if ip in banned_ips:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN,
                            content={"detail": "IP address is banned"})
    response = await call_next(request)
    return response


@app.middleware("http")
async def user_agent_ban(request: Request, call_next: Callable):
    user_agent = request.headers.get("user-agent")
    # print(f"User-agent: {user_agent}")
    for agent_banned in user_agent_ban_list:
        if re.search(agent_banned, user_agent):
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN,
                                content={"detail": "User-agent is banned"}, )
    response = await call_next(request)
    return response


BASE_DIR = Path(__file__).parent
# directory = BASE_DIR.joinpath("src").joinpath("static")
directory = BASE_DIR.joinpath("static")
app.mount("/static", StaticFiles(directory=directory), name="static")

app.include_router(contacts.router, prefix='/api')
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')


@app.on_event("startup")
async def startup():
    if not config.REDIS_PASSWORD:
        config.REDIS_PASSWORD = None
    r = await redis.Redis(host=config.REDIS_DOMAIN,
                          port=config.REDIS_PORT,
                          db=0,
                          password=config.REDIS_PASSWORD, )
    await FastAPILimiter.init(r)


templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """Returns a welcome htm page for the API

    :param: request
    :type request: Request
    :return: html page
    :rtype: templates.TemplateResponse
    """
    # return {"message": "Contacts Application"}
    return templates.TemplateResponse("index.html", {"request": request, "about_app": "Contacts App main page"})


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """Checks the health of the database

    :param: db
    :type db: AsyncSession
    :return: A message
    :rtype: dict
    :raises: HTMLException with status code 500

    """
    if db is None:
        raise HTTPException(status_code=500, detail="Database is not configured correctly")

    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
