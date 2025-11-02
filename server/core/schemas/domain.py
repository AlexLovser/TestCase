from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class CreateDomainModel(BaseModel):
    name: str
    parent_id: Optional[int] = None


class UpdateDomainModel(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None


# Базовая схема без вложенности
class DomainBaseResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    parent_id: Optional[int] = None

    # Кастомные вычисляемые поля
    full_path: str
    children_count: int


# class DomainListResponseModel(BaseModel):
#     model_config = ConfigDict(from_attributes=True)

#     id: int
#     name: str
#     parent_id: Optional[int] = None

#     # Кастомные вычисляемые поля
#     full_path: str
#     children_count: int


# Схема для родителя (без children, чтобы избежать циклов)
class DomainParentResponseModel(DomainBaseResponseModel):
    parent: Optional["DomainParentResponseModel"] = None


# Схема для дочерних (без parent, только базовая информация)
class DomainChildResponseModel(DomainBaseResponseModel):
    pass


# Полная схема для основного списка
class DomainResponseModel(DomainBaseResponseModel):
    parent: Optional[DomainParentResponseModel] = None
    children: List[DomainChildResponseModel] = []
