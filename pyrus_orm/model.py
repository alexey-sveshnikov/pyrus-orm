import copy
from datetime import datetime
from typing import Any, TypeVar, Type, Optional, Generic

from pyrus_orm.catalog import CatalogItem, CatalogEmptyValue
from pyrus_orm.fields import BaseField
from pyrus_orm.manager import Manager
from pyrus_orm.session import get_session
from pyrus_orm.utils import classproperty

T = TypeVar('T', bound='PyrusModel')


class PyrusModel(Generic[T]):
    id: Optional[int]
    create_date: datetime
    last_modified_date: datetime

    _data = None
    _field_values: dict[int, Any] = {}
    _changed_fields: set[int]

    class Meta:
        form_id: int
        fields: dict[str, BaseField]

    @classproperty
    def objects(cls: Type[T]) -> Manager[T]:
        return Manager(cls)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        try:
            int(cls.Meta.form_id)
        except (ValueError, AttributeError) as e:
            raise Exception('Model.Meta.form_id is not set') from e

    def __init__(self, **kwargs):
        self._field_values = {}
        self._changed_fields = set()
        self.id = None

        for field_name, field in self.Meta.fields.items():
            if field_name not in self._field_values:
                self._field_values[field.id] = {
                    'id': field.id,
                }

        for k, v in kwargs.items():
            if v is not None:
                setattr(self, k, v)

    @classmethod
    def from_pyrus_data(
        cls: Type[T],
        data: dict[str, Any],
    ) -> T:
        data = copy.deepcopy(data)

        def fix_datetime(v: str) -> str:
            # makes datetime compatible with python's 3.9 fromisoformat() function
            # 3.10+ does not require this
            return v.replace('Z', '+00:00')

        create_date = datetime.fromisoformat(fix_datetime(data['create_date']))
        last_modified_date = datetime.fromisoformat(fix_datetime(data['last_modified_date']))

        fields = data.pop('fields')
        flatten_fields = []
        for field in fields:
            if field['type'] == 'title':
                flatten_fields.extend(field['value']['fields'])  # check if title fields may be nested
            else:
                flatten_fields.append(field)

        obj = cls(
            id=data['id'],
            _data=data,
            _field_values={
                f['id']: f
                for f in flatten_fields
            },
            create_date=create_date,
            last_modified_date=last_modified_date,
        )
        return obj

    def as_pyrus_data(self):
        return {
            **(self._data or {}),
            'fields': self.get_pyrus_fields_data(),
            'form_id': self.Meta.form_id,
        }

    def get_pyrus_fields_data(self, changed_only: bool = False) -> list[Any]:
        values = list(self._field_values.values())
        if changed_only:
            values = [x for x in values if x['id'] in self._changed_fields]

        return sorted(values, key=lambda f: f['id'])

    def as_dict(self) -> dict[str, Any]:
        values = {}
        for field_name in self.Meta.fields.keys():
            value = getattr(self, field_name)
            if isinstance(value, CatalogItem):
                value = value.values
            elif isinstance(value, CatalogEmptyValue):
                value = None
            values[field_name] = value

        return values

    def save(self, comment: Optional[str] = None):
        if self.id:
            get_session().update_task(self.id, self.get_pyrus_fields_data(changed_only=True), comment)
        else:
            data = get_session().create_task(self.as_pyrus_data())
            new_item = type(self).from_pyrus_data(data)
            self.__dict__ = new_item.__dict__

    def comment(self, comment: str) -> None:
        assert self.id
        get_session().comment_task(self.id, comment)

    def get_url(self) -> str:
        return f'https://pyrus.com/t#id{self.id}'

    def __repr__(self) -> str:
        return f'Task {self.get_url()}'
