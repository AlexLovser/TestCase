from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from server.core.schemas.domain import *
from server.core.models.domain import Domain
from server.core.db import get_db
from server.core.security import verify_api_key


# Константы
MAX_DEPTH = 3

router = APIRouter(
    prefix="/domains",
    tags=["Domains"],
    responses={404: {"description": "Not found"}}
)


class DomainNotFoundError(HTTPException):
    """Исключение для не найденного домена"""
    def __init__(self, domain_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain with id {domain_id} not found"
        )


class DomainDepthExceededError(HTTPException):
    """Исключение для превышения глубины дерева доменов"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum domain depth is {MAX_DEPTH} levels"
        )


def calculate_depth(domain_id: int, db: Session) -> int:
    depth = 0
    current_id = domain_id
    while current_id:
        domain = db.query(Domain).filter(Domain.id == current_id).first()
        if not domain:
            break
        current_id = domain.parent_id
        depth += 1
        if depth > MAX_DEPTH:
            break
    return depth


@router.get("", response_model=List[DomainBaseResponseModel],
    summary="Список доменов",
    description="Получить список всех видов деятельности")
def list_domains(
    db: Session = Depends(get_db),
    api_key: str = Security(verify_api_key)
):
    return db.query(Domain).all()


@router.get("/{domain_id}", response_model=DomainResponseModel,
    summary="Получить домен")
def retrieve_domain(
    domain_id: int,
    db: Session = Depends(get_db),
    api_key: str = Security(verify_api_key)
):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")
    return domain


@router.post("", status_code=status.HTTP_201_CREATED, response_model=DomainBaseResponseModel,
    summary="Создать домен",
    description="Создать новый вид деятельности. Максимальная глубина дерева - 3 уровня")
def create_domain(
    payload: CreateDomainModel,
    db: Session = Depends(get_db),
    api_key: str = Security(verify_api_key)
):
    if payload.parent_id and calculate_depth(payload.parent_id, db) >= MAX_DEPTH:
        raise DomainDepthExceededError()

    try:
        domain = Domain(**payload.model_dump(exclude_unset=True))
        db.add(domain)
        db.commit()
        db.refresh(domain)
        return domain
    except IntegrityError as e:
        db.rollback()
        if 'unique constraint' in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Domain '{payload.name}' exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{domain_id}", response_model=DomainResponseModel,
    summary="Полная замена домена")
def replace_domain(
    domain_id: int,
    payload: CreateDomainModel,
    db: Session = Depends(get_db),
    api_key: str = Security(verify_api_key)
):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")

    for field, value in payload.model_dump().items():
        setattr(domain, field, value)

    db.commit()
    db.refresh(domain)
    return domain


@router.patch("/{domain_id}", response_model=DomainResponseModel,
    summary="Обновить домен")
def update_domain(
    domain_id: int,
    payload: UpdateDomainModel,
    db: Session = Depends(get_db),
    api_key: str = Security(verify_api_key)
):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise DomainNotFoundError(domain_id)

    data = payload.model_dump(exclude_unset=True)
    if 'parent_id' in data and data['parent_id'] and calculate_depth(data['parent_id'], db) >= MAX_DEPTH:
        raise DomainDepthExceededError()

    try:
        for field, value in data.items():
            setattr(domain, field, value)
        db.commit()
        db.refresh(domain)
        return domain
    except IntegrityError as e:
        db.rollback()
        if 'unique constraint' in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Domain name exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{domain_id}", status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить домен")
def delete_domain(
    domain_id: int,
    db: Session = Depends(get_db),
    api_key: str = Security(verify_api_key)
):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")
    db.delete(domain)
    db.commit()
