from fastapi import HTTPException


def validate_sort_field(sort: str, allowed_fields: tuple[str, ...]) -> str:
    if sort not in allowed_fields:
        allowed_fields_text = ", ".join(allowed_fields)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort field '{sort}'. Allowed fields: {allowed_fields_text}",
        )
    return sort
