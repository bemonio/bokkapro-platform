from sqlalchemy.sql import Select


def apply_sorting(
    query: Select,
    *,
    sort: str,
    order: str,
    allowed_fields: dict[str, object],
) -> Select:
    sort_column = allowed_fields[sort]
    if order == "desc":
        return query.order_by(sort_column.desc())
    return query.order_by(sort_column.asc())
