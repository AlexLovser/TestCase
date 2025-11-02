from .base import *
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Float
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from server.core.models.enterprise import Enterprise


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    address: Mapped[str] = mapped_column(String(length=255))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    enterprises: Mapped[List["Enterprise"]] = relationship("Enterprise", back_populates="address")

    __table_args__ = (
        Index("idx_address_address", address),
        Index("idx_address_latitude", latitude),
        Index("idx_address_longitude", longitude),
    )

    def __str__(self) -> str:
        enterprises_count = len(self.enterprises) if self.enterprises else 0
        return f"Address(id={self.id}, address={self.address}, enterprises={enterprises_count})"
