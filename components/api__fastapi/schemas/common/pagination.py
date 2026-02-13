from math import ceil
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    total: int
    page: int
    pageSize: int
    pages: int
    hasNext: bool
    hasPrev: bool

    @classmethod
    def from_values(cls, *, total: int, page: int, page_size: int) -> "PaginationMeta":
        pages = max(1, ceil(total / page_size)) if page_size else 1
        return cls(
            total=total,
            page=page,
            pageSize=page_size,
            pages=pages,
            hasNext=page < pages,
            hasPrev=page > 1,
        )


class Meta(BaseModel):
    pagination: PaginationMeta
    filters: dict[str, str | int | float | bool | None] | None = None
    sort: dict[str, str | int | float | bool | None] | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: Meta
