from sqlalchemy import func
from datetime import date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    create_at: Mapped[date] = mapped_column(
        server_default=func.current_date(), index=True)

    update_at: Mapped[date] = mapped_column(
        server_default=func.current_date(),
        server_onupdate=func.current_date())

    delete_at: Mapped[date] = mapped_column(
        nullable=True, index=True)

    def __repr__(self) -> str:
        cols = [f"{col}={getattr(self, col)}"
                for col in self.__table__.columns.keys()]
        return f"<{self.__class__.__name__}: {', '.join(cols)}>"
