from dataclasses import dataclass, field
from typing import Optional, TypedDict, Any, TYPE_CHECKING, Callable

if TYPE_CHECKING:
    pass


class PyrusCatalogSingleItem(TypedDict):
    item_id: int
    item_ids: list[int]
    headers: list[str]
    values: list[str]
    rows: list[list[str]]


class _CatalogListWrapper(list['CatalogItem']):
    def find(self, pattern: dict[str, Any]) -> Optional['CatalogItem']:
        for item in self:
            for k, v in pattern.items():
                if item.values[k] != v:
                    break
            else:
                return item
        return None


class _CatalogMixin:
    catalog_id: Optional[int]

    def __init__(self, catalog_id: int):
        self.catalog_id = catalog_id

    def catalog(self) -> _CatalogListWrapper:
        from pyrus_orm.session import get_session
        assert self.catalog_id, 'catalog_id is not set'

        return _CatalogListWrapper(get_session().get_catalog(self.catalog_id))


@dataclass
class CatalogItem(_CatalogMixin):
    item_id: int
    catalog_id: Optional[int] = field(compare=False, default=None)
    headers: list[str] = field(compare=False, default_factory=list)
    values_row: list[str] = field(compare=False, default_factory=list)
    values: dict[str, str] = field(compare=False, default_factory=dict)

    _bound_field_setter: Optional[Callable[['CatalogItem'], None]] = field(compare=False, default=None)

    @classmethod
    def from_pyrus_data(
        cls,
        data: PyrusCatalogSingleItem,
        catalog_id: Optional[int],
        bound_field_setter: Optional[Callable[['CatalogItem'], None]]
    ) -> 'CatalogItem':
        return cls(
            catalog_id=catalog_id,
            item_id=data['item_id'],
            headers=data.get('headers', []),
            values_row=data.get('values', []),
            values=(
                dict(zip(data['headers'], data['values']))
                if 'headers' in data and 'values' in data else {}
            ),
            _bound_field_setter=bound_field_setter,
        )

    def find_and_set(self, pattern: dict[str, Any]):
        assert self._bound_field_setter, f"CatalogItem is not bound to model's field " \
                                         f"(you should access it as model property only)"
        item = self.catalog().find(pattern)
        if item:
            self._bound_field_setter(item)
        else:
            raise ValueError("no item matching pattern found")


class CatalogEmptyValue(_CatalogMixin):
    catalog_id: int

    def __bool__(self):
        return False
