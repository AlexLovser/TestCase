from pydantic import BaseModel, ConfigDict, field_validator, model_serializer
from typing import Optional, List, Any
from server.core.schemas.address import CreateAddressModel, AddressResponseModel


class CreateEnterpriseModel(BaseModel):
    name: str
    domain_id: Optional[int] = None
    address: CreateAddressModel
    phones: Optional[List[str]] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError('Name cannot be empty')
        if len(v) > 255:
            raise ValueError('Name is too long (max 255 characters)')
        return v.strip()


class UpdateEnterpriseModel(BaseModel):
    name: Optional[str] = None
    domain_id: Optional[int] = None
    phones: Optional[List[str]] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError('Name cannot be empty')
            if len(v) > 255:
                raise ValueError('Name is too long (max 255 characters)')
            return v.strip()
        return v

    @field_validator('phones')
    @classmethod
    def validate_phones(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        return list(set(v)) if v else [] if v is not None else None


class EnterpriseDomainResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    full_path: str


class PhoneResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    phone: str


class EnterpriseResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    domain: Optional[EnterpriseDomainResponseModel] = None
    address: AddressResponseModel
    phones: Any = []

    @model_serializer
    def serialize_model(self):
        phones_list = [phone.phone if hasattr(phone, 'phone') else str(phone) for phone in self.phones] if self.phones else []

        domain_data = self.domain.model_dump() if self.domain and hasattr(self.domain, 'model_dump') else (self.domain if isinstance(self.domain, dict) else None)
        address_data = self.address.model_dump() if self.address and hasattr(self.address, 'model_dump') else (self.address if isinstance(self.address, dict) else None)

        return {
            'id': self.id,
            'name': self.name,
            'domain': domain_data,
            'address': address_data,
            'phones': phones_list
        }

