from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, TypedDict, Self


class Status(str, Enum):
    open = 'open'
    closed = 'closed'


class Flag(str, Enum):
    none = 'none'
    checked = 'checked'
    unchecked = 'unchecked'


class PyrusCatalogSingleItem(TypedDict):
    item_id: int
    item_ids: list[int]
    headers: list[str]
    values: list[str]
    rows: list[list[str]]


@dataclass
class CatalogItem:
    item_id: int
    catalog_id: Optional[int] = field(compare=False, default=None)
    headers: list[str] = field(compare=False, default_factory=list)
    values_row: list[str] = field(compare=False, default_factory=list)
    values: dict[str, str] = field(compare=False, default_factory=dict)

    @classmethod
    def from_pyrus_data(
        cls,
        data: PyrusCatalogSingleItem,
        catalog_id: Optional[int],
    ) -> Self:
        return cls(
            catalog_id=catalog_id,
            item_id=data['item_id'],
            headers=data.get('headers'),
            values_row=data.get('values'),
            values=(
                dict(zip(data['headers'], data['values']))
                if 'headers' in data and 'values' in data else None
            ),
        )

    def catalog(self) -> list[Self]:
        from pyrus_orm.session import get_session
        assert self.catalog_id, 'catalog_id is not set'

        return get_session().get_catalog(self.catalog_id)
