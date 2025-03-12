from datetime import date

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status

from src.db.conn import get_async_session
from src.db.rolls import rollsManager
from src.schemas import rolls
from src.utils.filters import serialize_filters

router = APIRouter()


@router.post('/rolls', response_model=rolls.Rolls)
async def create_rolls(roll_data: rolls.RollsCreate,
                       session=Depends(get_async_session)):
    roll = await rollsManager.create(session, roll_data.model_dump())
    return roll


@router.delete('/rolls/{roll_id}', response_model=rolls.Rolls)
async def delete_rolls(roll_id: int = Path(..., gt=0),
                       session=Depends(get_async_session)):
    roll = await rollsManager.delete(session, roll_id)
    return roll


@router.get('/rolls', response_model=list[rolls.Rolls])
async def get_rolls(session=Depends(get_async_session),
                    id_min: int | None = Query(None, gt=0),
                    id_max: int | None = Query(None, gt=0),
                    weight_min: int | None = Query(None, gt=0),
                    weight_max: int | None = Query(None, gt=0),
                    length_min: int | None = Query(None, gt=0),
                    length_max: int | None = Query(None, gt=0),
                    is_deleted: bool | None = Query(None),
                    created_after: date | None = Query(None),
                    created_before: date | None = Query(None),
                    deleted_after: date | None = Query(None),
                    deleted_before: date | None = Query(None),
                    ):
    filters = locals()
    filters.pop('session')
    filters = serialize_filters(filters)

    rolls_list = await rollsManager.get_with_filters(session=session,
                                                     **filters)
    return rolls_list


@router.get('/rolls/statistics')
async def get_rolls_statistics(session=Depends(get_async_session),
                               start_date: date | None = Query(None, gt=0),
                               end_date: date | None = Query(None, gt=0)):
    if (start_date is not None
            and end_date is not None
            and start_date > end_date):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Start date cannot be greater than End date"
        )
    statistics = await rollsManager.get_statistics(session,
                                                   start_date,
                                                   end_date)
    return statistics
