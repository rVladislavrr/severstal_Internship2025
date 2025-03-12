from src.models import Rolls
from fastapi import HTTPException, status


def build_filters(**kwargs) -> list:
    filters = []
    for field, value in kwargs.items():

        if value is None:
            continue

        if field.endswith("_min"):
            filters.append(getattr(Rolls, field[:-4]) >= value)
        elif field.endswith("_max"):
            filters.append(getattr(Rolls, field[:-4]) <= value)

        elif field.endswith("_after"):
            filters.append(getattr(Rolls, field[:-7] + '_at') >= value)
        elif field.endswith("_before"):
            filters.append(getattr(Rolls, field[:-8] + '_at') <= value)

        elif field == "is_deleted":
            filters.append(Rolls.is_deleted == value)

    return filters


def serialize_filters(filters: dict) -> dict:
    for key in filters:
        if key.endswith('_min'):
            field = key[:-4]
            min_value = filters[key]
            max_value = filters.get(f"{field}_max")

        elif key.endswith('_after'):
            field = key[:-6]
            min_value = filters[key]
            max_value = filters.get(f"{field}_before")

        else:
            continue

        if (min_value is not None
                and max_value is not None
                and min_value > max_value):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{key} cannot be greater than "
                       f"{field}_max/{field}_before"
            )
    return filters
