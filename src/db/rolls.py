from datetime import date
from sqlalchemy import and_, select, or_, func, cast, Date

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException
from src.db.base import BaseManager
from src.models import Rolls
from src.utils.filters import build_filters


class RollsManager(BaseManager):
    model = Rolls

    async def delete(self, session: AsyncSession, roll_id: int):
        roll = await session.get(self.model, roll_id)

        if not roll:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Roll not found')

        if roll.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail='The roll has already been removed')

        try:
            roll.is_deleted = True
            roll.delete_at = date.today()
            await session.flush()
            await session.refresh(roll)

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, )
        await session.commit()
        return roll

    async def get_with_filters(
            self, session: AsyncSession,
            **kwargs
    ):
        try:
            filters = build_filters(
                **kwargs
            )
            query = select(self.model)

            if filters:
                query = query.where(and_(*filters))

            result = await session.execute(query)
            result = result.scalars().all()
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error")
        return result

    async def get_statistics(self, session: AsyncSession,
                             start_date: date | None,
                             end_date: date | None):

        end_date = end_date or date.today()

        if start_date is None:
            earliest_date_query = \
                await session.execute(select(func.min(self.model.create_at)))
            earliest_date = earliest_date_query.scalar()
            start_date = earliest_date or date.today()

        in_period_condition = and_(
            self.model.create_at <= end_date,
            or_(
                self.model.delete_at == None,
                self.model.delete_at >= start_date
            )
        )

        query = select(

            func.count(self.model.id).filter(
                and_(self.model.create_at >= start_date,
                     self.model.create_at <= end_date)
            ).label("added_count"),

            func.count(self.model.id).filter(
                and_(self.model.delete_at !=  None,
                     self.model.delete_at >= start_date,
                     self.model.delete_at <= end_date)
            ).label("deleted_count"),

            func.avg(self.model.weight)
            .filter(in_period_condition).label("average_weight"),

            func.avg(self.model.length)
            .filter(in_period_condition).label("average_length"),

            func.min(self.model.length)
            .filter(in_period_condition).label("min_length"),

            func.max(self.model.length)
            .filter(in_period_condition).label("max_length"),

            func.min(self.model.weight)
            .filter(in_period_condition).label("min_weight"),

            func.max(self.model.weight)
            .filter(in_period_condition).label("max_weight"),

            func.sum(self.model.weight)
            .filter(in_period_condition).label("total_weight"),
        )

        result = await session.execute(query)
        stats = result.mappings().first()
        result = {
            "added_count": stats["added_count"],
            "deleted_count": stats["deleted_count"],
            "average_weight": stats["average_weight"],
            "average_length": stats["average_length"],
            "min_length": stats["min_length"],
            "max_length": stats["max_length"],
            "min_weight": stats["min_weight"],
            "max_weight": stats["max_weight"],
            "total_weight": stats["total_weight"],
        }
        result_days = await self.get_statistics_days(session,
                                                     start_date,
                                                     end_date)
        result.update(result_days)
        return result

    async def get_statistics_days(self,
                                  session: AsyncSession,
                                  start_date: date | None,
                                  end_date: date | None):

        end_date = end_date or date.today()

        if start_date is None:
            earliest_date_query =\
                await session.execute(select(func.min(self.model.create_at)))
            earliest_date = earliest_date_query.scalar()
            start_date = earliest_date or date.today()

        interval_query = await session.execute(
            select(
                func.min(self.model.delete_at -
                         self.model.create_at).label('min_interval'),
                func.max(self.model.delete_at -
                         self.model.create_at).label('max_interval'),
            ).where(
                self.model.delete_at.is_not(None)
            )
        )
        interval_result = interval_query.fetchone()

        min_interval = interval_result.min_interval \
            if interval_result.min_interval is not None else 0
        max_interval = interval_result.max_interval \
            if interval_result.max_interval is not None else 0

        count_per_day = await session.execute(
            select(
                cast(self.model.create_at, Date).label("day"),
                func.count().label("count")
            ).where(
                and_(
                    self.model.create_at <= end_date,
                    or_(self.model.delete_at >= start_date,
                        self.model.delete_at.is_(None))
                )
            ).group_by(cast(self.model.create_at, Date))
        )
        counts = count_per_day.fetchall()
        min_day_count = min(counts, key=lambda x: x.count, default=None)
        max_day_count = max(counts, key=lambda x: x.count, default=None)

        weight_per_day = await session.execute(
            select(
                cast(Rolls.create_at, Date).label("day"),
                func.sum(Rolls.weight).label("total_weight")
            ).where(
                and_(
                    Rolls.create_at <= end_date,
                    or_(Rolls.delete_at >= start_date,
                        Rolls.delete_at.is_(None))
                )
            ).group_by(cast(Rolls.create_at, Date))
        )
        weights = weight_per_day.fetchall()
        min_day_weight = min(weights,
                             key=lambda x: x.total_weight, default=None)
        max_day_weight = max(weights,
                             key=lambda x: x.total_weight, default=None)

        return {
            "min_interval": min_interval,
            "max_interval": max_interval,
            "min_day_count": {
                "day": min_day_count.day
                if min_day_count else None,
                "count": min_day_count.count
                if min_day_count else None
            },
            "max_day_count": {
                "day": max_day_count.day
                if max_day_count else None,
                "count": max_day_count.count
                if max_day_count else None
            },
            "min_day_weight": {
                "day": min_day_weight.day
                if min_day_weight else None,
                "weight": min_day_weight.total_weight
                if min_day_weight else None
            },
            "max_day_weight": {
                "day": max_day_weight.day
                if max_day_weight else None,
                "weight": max_day_weight.total_weight
                if max_day_weight else None
            }
        }


rollsManager = RollsManager()
