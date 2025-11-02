from .base import *
from sqlalchemy.ext.hybrid import hybrid_property


class Domain(Base):
    __tablename__ = "domain"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(length=255), unique=True)

    enterprises: Mapped[List["Enterprise"]] = relationship("Enterprise", back_populates="domain")

    parent_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("domain.id", name="fk_domain_parent_id__domain_id"),
        nullable=True,
    )

    parent: Mapped[Optional["Domain"]] = relationship(
        "Domain",
        remote_side=[id],
        back_populates="children",
    )
    children: Mapped[List["Domain"]] = relationship(
        "Domain",
        back_populates="parent",
    )

    __table_args__ = (
        Index("idx_domain_name", name),
    )


    @hybrid_property
    def full_path(self) -> str:
        parts = [self.name]
        current = self.parent
        while current:
            parts.append(current.name)
            current = current.parent
        return " > ".join(parts[::-1])


    @hybrid_property
    def children_count(self) -> int:
        return len(self.children)

    @hybrid_property
    def depth(self) -> int:
        level = 0
        current = self.parent
        while current:
            level += 1
            current = current.parent
        return level

    def get_all_descendants(self) -> List["Domain"]:
        result = []
        for child in self.children:
            result.append(child)
            result.extend(child.get_all_descendants())
        return result

    def __str__(self) -> str:
        return f"Domain(id={self.id}, name={self.name}, parent_id={self.parent_id})"
