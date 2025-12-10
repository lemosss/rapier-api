from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import os

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@router.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/me", response_class=HTMLResponse)
def me(request: Request):
    access_token = request.cookies.get('access_token') or request.headers.get('Authorization')
    # Apenas renderiza, o JS da página redireciona se não autenticado de fato
    return templates.TemplateResponse("me.html", {"request": request})

@router.get("/admin/users/new", response_class=HTMLResponse)
def admin_create_user(request: Request):
    return templates.TemplateResponse("admin_users_new.html", {"request": request})

@router.get("/admin/users", response_class=HTMLResponse)
def admin_list_users(request: Request):
    return templates.TemplateResponse("admin_users_list.html", {"request": request})

@router.get("/companies", response_class=HTMLResponse)
def companies_list(request: Request):
    return templates.TemplateResponse("companies_list.html", {"request": request})

@router.get("/companies/new", response_class=HTMLResponse)
def companies_new(request: Request):
    return templates.TemplateResponse("companies_new.html", {"request": request})
