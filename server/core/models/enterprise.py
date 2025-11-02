from .base import *


class Phone(Base):
    __tablename__ = "phones"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    phone: Mapped[str] = mapped_column(String(length=255), unique=True)
    enterprise_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("enterprises.id"))
    enterprise: Mapped["Enterprise"] = relationship("Enterprise", back_populates="phones")


class Enterprise(Base):
    __tablename__ = "enterprises"


    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(length=255), unique=True)
    address_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("addresses.id"))
    address: Mapped["Address"] = relationship("Address", uselist=False)

    phones: Mapped[List["Phone"]] = relationship("Phone", back_populates="enterprise")

    domain_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("domain.id", name="fk_enterprise_domain_id__domain_id"),
        nullable=True,
    )
    domain: Mapped[Optional["Domain"]] = relationship("Domain", back_populates="enterprises")


    __table_args__ = (
        Index("idx_enterprise_name", name),
    )

    def __str__(self) -> str:
        phones_str = ', '.join([p.phone for p in self.phones]) if self.phones else 'No phones'
        return f"Enterprise(id={self.id}, name={self.name}, phones=[{phones_str}])"
