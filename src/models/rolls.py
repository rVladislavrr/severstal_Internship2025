from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
import enum
from src.models.base import Base


class Status(enum.Enum):
    """
    Класс статуса если понадобиться не только удалённые,
     а так же в ожидании или какие-либо ещё
    """
    DELETED = "deleted"
    ACTIVE = "active"


class Rolls(Base):
    __tablename__ = 'rolls'

    id: Mapped[int] = mapped_column(primary_key=True)
    length: Mapped[int] = mapped_column(nullable=False)
    weight: Mapped[int] = mapped_column(nullable=False)
    is_deleted: Mapped[bool] = mapped_column(default=False,
                                             nullable=False,
                                             index=True)

    __table_args__ = (
        CheckConstraint('length > 0',
                        name='check_length_positive'),
        CheckConstraint('weight > 0',
                        name='check_weight_positive'),
    )
