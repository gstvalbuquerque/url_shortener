import validators


from fastapi import Depends, APIRouter, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.datastructures import URL

from ..core.models import models

from ..core.schemas import schemas

from ..services import services
from ..core.models.database import SessionLocal, engine
from ..core.config import get_settings
from ..utils.exception_handling import handle_exception

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{url_key}", response_class=RedirectResponse, status_code=302)
def forward_to_target_url(
    url_key: str,
    request: Request,
    db: Session = Depends(get_db),
):
    if db_url := services.get_db_url_by_key(db=db, url_key=url_key):
        services.update_db_clicks(db=db, db_url=db_url)
        return db_url.target_url
    else:
        handle_exception(status_code=404, request=request)


@router.get(
    "/admin/{secret_key}",
    name="administration info",
    response_model=schemas.URLInfo,
)
def get_url_info(
    secret_key: str, request: Request, db: Session = Depends(get_db)
):
    if db_url := services.get_db_url_by_secret_key(db, secret_key=secret_key):
        return get_admin_info(db_url)
    else:
        handle_exception(status_code=404, request=request)


@router.post("/url", response_model=schemas.URLInfo)
def create_url(url: schemas.URLBase, db: Session = Depends(get_db)):
    validate_url(url.target_url)
    db_url = services.create_db_url(db=db, url=url)
    return get_admin_info(db_url)


@router.post("/custom-url", response_model=schemas.URLInfo)
def create_custom_url(url: schemas.CustomURL, request: Request, db: Session = Depends(get_db)):
    validate_url(url.target_url)
    if services.get_db_url_by_key(db=db, url_key=url.custom_url_key):
        handle_exception(status_code=409)
    db_url = services.create_custom_db_url(db=db, url=url)
    return get_admin_info(db_url)


@router.delete("/admin/{secret_key}")
def delete_url(
    secret_key: str, request: Request, db: Session = Depends(get_db)
):
    if db_url := services.deactivate_db_url_by_secret_key(db, secret_key=secret_key):
        message = f"Successfully deleted shortened URL for '{db_url.target_url}'"
        return {"detail": message}
    else:
        handle_exception(status_code=404, request=request)


def get_admin_info(db_url: models.URL) -> schemas.URLInfo:
    base_url = URL(get_settings().base_url)
    admin_endpoint = router.url_path_for(
        "administration info", secret_key=db_url.secret_key
    )
    db_url.url = str(base_url.replace(path=db_url.key))
    db_url.admin_url = str(base_url.replace(path=admin_endpoint))
    return db_url


def validate_url(url: str):
    if not validators.url(url):
        handle_exception(
            status_code=400, message="Your provided URL is not valid")
