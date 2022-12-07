import copy
from datetime import datetime
from typing import Any, TypeVar, Type, Optional, Protocol

from pyrus_orm.manager import _ManagerProperty
from pyrus_orm.session import get_session

T = TypeVar('T', bound='PyrusModel')


class _ModelMeta(Protocol):
    form_id: int


class PyrusModel:
    id: int
    create_date: datetime
    last_modified_date: datetime

    Meta: _ModelMeta

    _data = None
    _field_values: dict[int, Any] = {}
    _changed_fields: set[int]

    objects: _ManagerProperty[T]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.objects = _ManagerProperty(cls)

        try:
            int(cls.Meta.form_id)
        except (ValueError, AttributeError) as e:
            raise Exception('Model.Meta.form_id is not set') from e

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
        obj._changed_fields = set()

        obj.id = data['id']

        def fix_datetime(v: str) -> str:
            # makes datetime compatible with python's 3.9 fromisoformat() function
            # 3.10+ does not require this
            return v.replace('Z', '+00:00')

        obj.create_date = datetime.fromisoformat(fix_datetime(data['create_date']))
        obj.last_modified_date = datetime.fromisoformat(fix_datetime(data['last_modified_date']))
        return obj

    def as_pyrus_data(self):
        return {
            **self._data,
            'fields': self.get_pyrus_fields_data(),
            'form_id': self.Meta.form_id,
        }

    def get_pyrus_fields_data(self, changed_only: bool = False) -> list[Any]:
        values = self._field_values.values()
        if changed_only:
            values = [x for x in values if x['id'] in self._changed_fields]

        return sorted(values, key=lambda f: f['id'])

    def save(self, comment: Optional[str] = None):
        if self.id:
            get_session().update_task(self.id, self.get_pyrus_fields_data(changed_only=True), comment)
        else:
            get_session().create_task(self.as_pyrus_data())
