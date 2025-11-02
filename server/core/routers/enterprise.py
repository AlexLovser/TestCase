from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from typing import List
from server.core.schemas.enterprise import (
    CreateEnterpriseModel,
    EnterpriseResponseModel,
    UpdateEnterpriseModel,
)
from server.core.models import Enterprise, Address, Phone
from server.core.db import get_db
from server.core.utils.rings import EarthRing


# Константы
HTTP_404_NOT_FOUND = status.HTTP_404_NOT_FOUND
HTTP_400_BAD_REQUEST = status.HTTP_400_BAD_REQUEST
HTTP_409_CONFLICT = status.HTTP_409_CONFLICT

router = APIRouter(
    prefix="/enterprises",
    tags=["Enterprises"],
    responses={404: {"description": "Not found"}}
)


class EnterpriseNotFoundError(HTTPException):
    """Исключение для не найденного предприятия"""
    def __init__(self, enterprise_id: int):
        super().__init__(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Enterprise with id {enterprise_id} not found"
        )


class DuplicateEnterpriseError(HTTPException):
    """Исключение для дублирующегося имени предприятия"""
    def __init__(self, name: str):
        super().__init__(
            status_code=HTTP_409_CONFLICT,
            detail=f"Enterprise with name '{name}' already exists"
        )


def get_enterprises_query(db: Session):
    return db.query(Enterprise).options(
        joinedload(Enterprise.address),
        joinedload(Enterprise.domain),
        joinedload(Enterprise.phones),
    )

@router.get("", response_model=List[EnterpriseResponseModel], summary="Список всех предприятий")
def get_enterprises(db: Session = Depends(get_db)):
    return get_enterprises_query(db).all()


@router.get("/search/", response_model=List[EnterpriseResponseModel],
    summary="Поиск предприятий по названию",
    description="Поиск предприятий по частичному совпадению в названии (регистр не важен)")
def search_enterprises(q: str, db: Session = Depends(get_db)):
    return get_enterprises_query(db).filter(Enterprise.name.ilike(f"%{q}%")).all()


@router.get("/with_address/", response_model=List[EnterpriseResponseModel],
    summary="Поиск предприятий по адресу",
    description="Поиск предприятий по частичному совпадению в адресе")
def get_enterprises_by_address(q: str, db: Session = Depends(get_db)):
    return get_enterprises_query(db).join(Address).filter(Address.address.ilike(f"%{q}%")).all()


@router.get("/in_circle/", response_model=List[EnterpriseResponseModel],
    summary="Поиск в радиусе",
    description="Находит все предприятия в заданном радиусе от точки с координатами (x, y)")
def get_enterprises_in_circle(
    x: float,
    y: float,
    r: float,
    db: Session = Depends(get_db)
):
    earth = EarthRing()
    center = earth.to_flat((x, y))
    all_enterprises = get_enterprises_query(db).all()

    result = []
    for ent in all_enterprises:
        point = earth.to_flat((ent.address.latitude, ent.address.longitude))
        if earth.in_circle(a=point, r=r, center=center):
            result.append(ent)
    return result


@router.get("/in_frame/", response_model=List[EnterpriseResponseModel],
    summary="Поиск в области",
    description="Находит все предприятия в прямоугольной области между двумя точками")
def get_enterprises_in_frame(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    db: Session = Depends(get_db)
):
    earth = EarthRing()
    corner1 = earth.to_flat((x1, y1))
    corner2 = earth.to_flat((x2, y2))
    all_enterprises = get_enterprises_query(db).all()

    result = []
    for ent in all_enterprises:
        point = earth.to_flat((ent.address.latitude, ent.address.longitude))
        if earth.in_frame(a=corner1, c=point, b=corner2):
            result.append(ent)
    return result



@router.get("/by_domain/{domain_id}", response_model=List[EnterpriseResponseModel],
    summary="Поиск по виду деятельности",
    description="""
Поиск предприятий по виду деятельности (домену).

Если include_children=true (по умолчанию), поиск включает все дочерние домены.
Например, поиск по домену "Еда" найдет также "Мясную продукцию", "Колбасы" и т.д.
    """)
def get_enterprises_by_domain(
    domain_id: int,
    include_children: bool = True,
    db: Session = Depends(get_db)
):
    from server.core.models.domain import Domain

    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Domain {domain_id} not found")

    if include_children:
        domain_ids = [domain_id]
        domain_ids.extend([d.id for d in domain.get_all_descendants()])
        return get_enterprises_query(db).filter(Enterprise.domain_id.in_(domain_ids)).all()
    else:
        return get_enterprises_query(db).filter(Enterprise.domain_id == domain_id).all()

@router.post("", status_code=status.HTTP_201_CREATED, response_model=EnterpriseResponseModel,
    summary="Создать предприятие",
    description="Создает новое предприятие с адресом и телефонами")
def create_enterprises(payload: CreateEnterpriseModel, db: Session = Depends(get_db)):
    try:
        address = Address(
            address=payload.address.address,
            latitude=payload.address.latitude,
            longitude=payload.address.longitude
        )
        db.add(address)
        db.flush()

        enterprise = Enterprise(
            name=payload.name,
            address_id=address.id,
            domain_id=payload.domain_id
        )
        db.add(enterprise)
        db.flush()

        if payload.phones:
            for phone_number in payload.phones:
                db.add(Phone(phone=phone_number, enterprise_id=enterprise.id))

        db.commit()
        db.refresh(enterprise)
        return enterprise

    except IntegrityError as e:
        db.rollback()
        if 'unique constraint' in str(e).lower() and 'name' in str(e).lower():
            raise DuplicateEnterpriseError(payload.name)
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{enterprise_id}", response_model=EnterpriseResponseModel,
    summary="Полная замена предприятия")
def replace_enterprises(enterprise_id: int, payload: CreateEnterpriseModel, db: Session = Depends(get_db)):
    enterprise = db.query(Enterprise).filter(Enterprise.id == enterprise_id).first()
    if not enterprise:
        raise EnterpriseNotFoundError(enterprise_id)

    try:
        enterprise.name = payload.name
        enterprise.domain_id = payload.domain_id

        db.query(Phone).filter(Phone.enterprise_id == enterprise_id).delete()
        if payload.phones:
            for phone_number in payload.phones:
                db.add(Phone(phone=phone_number, enterprise_id=enterprise_id))

        db.commit()
        db.refresh(enterprise)
        return enterprise

    except IntegrityError as e:
        db.rollback()
        if 'unique constraint' in str(e).lower() and 'name' in str(e).lower():
            raise DuplicateEnterpriseError(payload.name)
        if 'unique constraint' in str(e).lower() and 'phone' in str(e).lower():
            raise HTTPException(status_code=HTTP_409_CONFLICT, detail="Phone already exists")
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))

@router.patch("/{enterprise_id}", response_model=EnterpriseResponseModel,
    summary="Обновить предприятие",
    description="Частичное обновление предприятия. Телефоны заменяются полностью (set операция)")
def update_enterprises(enterprise_id: int, payload: UpdateEnterpriseModel, db: Session = Depends(get_db)):
    enterprise = db.query(Enterprise).filter(Enterprise.id == enterprise_id).first()
    if not enterprise:
        raise EnterpriseNotFoundError(enterprise_id)

    try:
        data = payload.model_dump(exclude_unset=True)
        phones_data = data.pop('phones', None)

        for field, value in data.items():
            setattr(enterprise, field, value)

        if phones_data is not None:
            db.query(Phone).filter(Phone.enterprise_id == enterprise_id).delete()
            if phones_data:
                for phone_number in phones_data:
                    db.add(Phone(phone=phone_number, enterprise_id=enterprise_id))

        db.commit()
        db.refresh(enterprise)
        return enterprise

    except IntegrityError as e:
        db.rollback()
        if 'unique constraint' in str(e).lower() and 'name' in str(e).lower():
            raise DuplicateEnterpriseError(payload.name)
        if 'unique constraint' in str(e).lower() and 'phone' in str(e).lower():
            raise HTTPException(status_code=HTTP_409_CONFLICT, detail="Phone already exists")
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
