from .base import *
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Float



class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    address: Mapped[str] = mapped_column(String(length=255))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    __table_args__ = (
        Index("idx_address_address", address),
        Index("idx_address_latitude", latitude),
        Index("idx_address_longitude", longitude),
    )

    def __str__(self) -> str:
        return f"Address(id={self.id}, address={self.address})"
