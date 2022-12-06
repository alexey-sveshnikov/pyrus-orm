import copy
from typing import Any, TypeVar, Type

from pyrus_orm.manager import _ManagerProperty

T = TypeVar('T', bound='PyrusModel')


class PyrusModel:
    _data = None
    _field_values: dict[int, Any] = {}

    objects: _ManagerProperty[T]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.objects = _ManagerProperty(cls)

    @classmethod
    def from_pyrus_data(
        cls: Type[T],
        data: dict[str, Any],
    ) -> T:
        data = copy.deepcopy(data)
        obj = cls()
        fields = data.pop('fields')
        obj._data = data
        obj._field_values = {
            f['id']: f
            for f in fields
        }
        return obj

    def as_pyrus_data(self):
        fields = sorted(self._field_values.values(), key=lambda f: f['id'])
        return {
            'fields': fields,
            **self._data,
        }
