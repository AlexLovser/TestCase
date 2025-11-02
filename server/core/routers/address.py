from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from server.core.schemas.address import CreateAddressModel, AddressResponseModel, UpdateAddressModel
from server.core.db import get_db
from sqlalchemy.orm import Session
from server.core.models.address import Address
from typing import List


router = APIRouter(
    prefix="/addresses",
    tags=["Addresses"],
    responses={404: {"description": "Not found"}}
)


class AddressNotFoundError(HTTPException):
    """Исключение для не найденного адреса"""
    def __init__(self, address_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address with id {address_id} not found"
        )

@router.get("", response_model=List[AddressResponseModel],
    summary="Список адресов")
def list_addresses(db: Session = Depends(get_db)):
    return db.query(Address).all()


@router.get("/{address_id}", response_model=AddressResponseModel,
    summary="Получить адрес")
def retrieve_address(address_id: int, db: Session = Depends(get_db)):
    address = db.query(Address).filter(Address.id == address_id).first()
    if not address:
        raise AddressNotFoundError(address_id)
    return address


@router.get("/{address_id}/enterprises", response_model=List[dict],
    summary="Предприятия по адресу",
    description="Получить список всех организаций находящихся по данному адресу")
def get_enterprises_at_address(address_id: int, db: Session = Depends(get_db)):
    from server.core.models.enterprise import Enterprise

    address = db.query(Address).filter(Address.id == address_id).first()
    if not address:
        raise AddressNotFoundError(address_id)

    enterprises = db.query(Enterprise).filter(Enterprise.address_id == address_id).all()

    return [
        {
            "id": ent.id,
            "name": ent.name,
            "domain_id": ent.domain_id,
            "phones": [phone.phone for phone in ent.phones] if ent.phones else []
        }
        for ent in enterprises
    ]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AddressResponseModel,
    summary="Создать адрес",
    description="Обычно адреса создаются автоматически вместе с предприятиями")
def create_addresses(payload: CreateAddressModel, db: Session = Depends(get_db)):
    try:
        address = Address(address=payload.address, latitude=payload.latitude, longitude=payload.longitude)
        db.add(address)
        db.commit()
        db.refresh(address)
        return address
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{address_id}", response_model=AddressResponseModel,
    summary="Полная замена адреса")
def replace_address(address_id: int, payload: CreateAddressModel, db: Session = Depends(get_db)):
    address = db.query(Address).filter(Address.id == address_id).first()
    if not address:
        raise AddressNotFoundError(address_id)

    try:
        address.address = payload.address
        address.latitude = payload.latitude
        address.longitude = payload.longitude
        db.commit()
        db.refresh(address)
        return address
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.patch("/{address_id}", response_model=AddressResponseModel,
    summary="Обновить адрес")
def update_address(address_id: int, payload: UpdateAddressModel, db: Session = Depends(get_db)):
    address = db.query(Address).filter(Address.id == address_id).first()
    if not address:
        raise AddressNotFoundError(address_id)

    try:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(address, field, value)
        db.commit()
        db.refresh(address)
        return address
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
