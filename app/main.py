import json
import pathlib
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.authentication import AuthenticationMiddleware
from cassandra.cqlengine.management import sync_table
from pydantic.error_wrappers import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.authentication import requires

from .users.models import User
from app.users.schemas import (
    UserSignupSchema,
    UserLoginSchema
)
from app.users.decorators import login_required
from . import config, db, utils
from .shortcuts import render, redirect
from app.users.exceptions import LoginRequiredException
from app.users.backends import JWTCookieBackend
from app.videos.models import Video
from app.videos.routers import router as video_router
from app.watch_events.models import WatchEvent
from app.watch_events.routers import router as watch_event_router
from app.playlists.models import Playlist
from app.playlists.routers import router as playlist_router


BASE_DIR = pathlib.Path(__file__).resolve().parent
DB_SESSION = None

app = FastAPI()
app.add_middleware(AuthenticationMiddleware, backend=JWTCookieBackend())
app.include_router(video_router)
app.include_router(watch_event_router)
app.include_router(playlist_router)


'''
Handle exception
'''
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    status_code = exc.status_code
    template_name = "errors/main.html"
    if status_code == 404:
        template_name = "errors/404.html"
    context = {"status_code": status_code}
    return render(request, template_name, context, status_code)


@app.exception_handler(LoginRequiredException)
async def login_required_exception_handler(request, exc):
    return redirect(f"/login?next={request.url}", remove_session=True)


'''
app event
'''
@app.on_event("startup")
def on_startup():
    global DB_SESSION
    DB_SESSION = db.get_session()
    sync_table(User)
    sync_table(Video)
    sync_table(WatchEvent)
    sync_table(Playlist)


'''
Api Endpoint
'''
@app.get('/', response_class=HTMLResponse)
def homepage(request: Request):
    if request.user.is_authenticated:
        return render(request,  "dashboard.html", {}, status_code=200)
    return render(request, "home.html", {})


@app.get('/account', response_class=HTMLResponse)
@login_required
def account_view(request: Request):
    
    context = {
    }
    return render(request, "account.html", context=context)


@app.get('/login', response_class=HTMLResponse)
def login_get_view(request: Request):
    session_id = request.cookies.get('session_id') or None
    return render(request, "auth/login.html", {
        "logged_in": session_id is not None
    })


@app.post('/login', response_class=HTMLResponse)
def login_post_view(request: Request, email: str=Form(...), password:str=Form(...)):
    
    
    raw_data = {
        "email": email,
        "password": password,
    }
    
    data, errors = utils.valid_schema_data_or_error(raw_data, UserLoginSchema)
    
    context = {
        "data": data,
        "errors": errors
    }
    
    if len(errors) > 0:
        return render(request, "auth/login.html", context, status_code=400)
    
    return redirect("/", cookies=data)


@app.get('/signup', response_class=HTMLResponse)
def signup_get_view(request: Request):
    context = {
    }
    return render(request, "auth/signup.html", context=context)


@app.post('/signup', response_class=HTMLResponse)
def signup_post_view(request: Request, email: str=Form(...)
                    , password:str=Form(...)
                    , password_confirm:str=Form(...)):
    
    raw_data = {
        "email": email,
        "password": password,
        "password_confirm": password_confirm
    }
    
    data, errors = utils.valid_schema_data_or_error(raw_data, UserSignupSchema)
    
    if len(errors) == 0:
        User.create_user(email=email, password=password)        
        return redirect("/login")
    
    context = {
        "data": data,
        "errors": errors
    }
    
    return render(request, "auth/signup.html", context, status_code=400)


@app.get('/users')
def users_list_view():
    q = User.objects.all().limit(10)
    return list(q)
