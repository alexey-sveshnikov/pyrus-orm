import sys
from datetime import date, time, datetime
from enum import Enum
from typing import Literal, Optional, Generic, TypeVar, Union, TYPE_CHECKING, Type, cast, Any

from .catalog import CatalogItem, CatalogEmptyValue, _CatalogListWrapper
from .session import get_session
from .types import Flag, Status

if TYPE_CHECKING:
    from .model import PyrusModel

FieldType = Literal[
    'text', 'money', 'number', 'date', 'time',
    'checkmark', 'due_date', 'due_date_time',
    'email', 'phone', 'flag', 'step', 'status',
    'creation_date', 'note', 'catalog',
]

T = TypeVar('T')


class BaseField(Generic[T]):
    id: int
    name: Optional[str] = None
    type: FieldType

    def __init__(self, id: int):
        self.id = id

    def __set_name__(self, owner, name):
        if not hasattr(owner.Meta, 'fields'):
            setattr(owner.Meta, 'fields', {})
        owner.Meta.fields[name] = self
        self.name = name

    def __get__(self, instance: 'PyrusModel', owner) -> Optional[T]:
        return instance._field_values[self.id].get('value')

    def __set__(self, instance, value: T):
        instance._field_values[self.id]['value'] = value
        instance._changed_fields.add(self.id)

    @classmethod
    def deserialize_from_pyrus(cls, value: Any) -> T:
        return cast(T, value)

    @classmethod
    def serialize_to_pyrus(cls, value: T) -> Any:
        return value


class TextField(BaseField[str]):
    type = 'text'


class NumericField(BaseField[float]):
    type = 'number'

    @classmethod
    def deserialize_from_pyrus(cls, value: Any) -> T:
        return float(value)


class IntegerField(BaseField[int]):
    type = 'number'

    @classmethod
    def deserialize_from_pyrus(cls, value: Any) -> T:
        return int(value)


class DateField(BaseField[date]):
    type = 'date'

    @classmethod
    def deserialize_from_pyrus(cls, value: Any) -> T:
        return date.fromisoformat(value)

    @classmethod
    def serialize_to_pyrus(cls, value: T) -> Any:
        return value.isoformat()


class TimeField(BaseField[time]):
    type = 'time'

    @classmethod
    def deserialize_from_pyrus(cls, value: Any) -> T:
        return datetime.strptime(value, '%H:%M').time()

    @classmethod
    def serialize_to_pyrus(cls, value: T) -> Any:
        return value.strftime('%H:%M')


class DueDateTimeField(BaseField[Optional[datetime]]):
    type = 'due_date_time'

    @classmethod
    def deserialize_from_pyrus(cls, value: str) -> T:
        if not value:
            return None
        if sys.version_info < (3, 11):
            value = value.replace('Z', '+00:00')
        return datetime.fromisoformat(value)

    @classmethod
    def serialize_to_pyrus(cls, value: T) -> Any:
        if value:
            return value.isoformat()
        return ''


class StepField(BaseField[int]):
    type = 'step'

    def __set__(self, *_):
        raise AttributeError('step field is read-only')


class StatusField(BaseField[Status]):
    type = 'status'

    def __set__(self, *_):
        raise AttributeError('status field is read-only')


class NoteField(BaseField[str]):
    type = 'note'

    def __set__(self, *_):
        raise AttributeError('note field is read-only')


class FlagField(BaseField[Flag]):
    type = 'flag'


class CheckmarkField(BaseField[bool]):
    type = 'checkmark'

    def __get__(self, instance: 'PyrusModel', owner) -> bool:
        return instance._field_values[self.id].get('value') == 'checked'

    def __set__(self, instance, value: bool):
        instance._field_values[self.id]['value'] = 'checked' if value else 'unchecked'
        instance._changed_fields.add(self.id)


class CatalogField(BaseField):
    type = 'catalog'
    _catalog_id: int

    def __init__(self, id: int, *, catalog_id: int):
        super().__init__(id)
        self._catalog_id = catalog_id

    def __get__(self, instance: 'PyrusModel', owner) -> Union[CatalogEmptyValue, CatalogItem]:
        try:
            field_value = instance._field_values[self.id]['value']
        except (KeyError, AttributeError):
            return CatalogEmptyValue(self._catalog_id)

        return CatalogItem.from_pyrus_data(
            catalog_id=self._catalog_id,
            data=field_value,
            bound_field_setter=lambda value: self.__set__(instance, value),
        )

    def __set__(self, instance: 'PyrusModel', value: Union[CatalogItem, int]):
        assert isinstance(value, (int, CatalogItem)), f'invalid type for {self.name}: {type(value).__name__}'

        if isinstance(value, CatalogItem):
            item_id = value.item_id
        else:
            item_id = value

        # TODO: check if item_id is valid
        instance._field_values[self.id]['value'] = {
            'item_id': item_id
        }
        instance._changed_fields.add(self.id)


T_Enum = TypeVar('T_Enum', bound=Enum)


class CatalogEnumField(BaseField[T_Enum]):
    type = 'catalog'
    _catalog_id: int
    _enum: Type[T_Enum]
    _id_field: str

    def __init__(self, id: int, *, catalog_id: int, enum: Type[T_Enum], id_field: str):
        super().__init__(id)
        self._catalog_id = catalog_id
        self._enum = enum
        self._id_field = id_field

    def __get__(self, instance: 'PyrusModel', owner) -> Optional[T_Enum]:
        try:
            field_value = instance._field_values[self.id]['value']
        except (KeyError, AttributeError):
            return None

        if self._id_field == 'item_id':
            enum_value = field_value['item_id']
        else:
            item_values = dict(zip(field_value['headers'], field_value['values']))
            enum_value = item_values[self._id_field]

        for item in self._enum:
            if item.value == enum_value:
                return item
        raise ValueError(f"can't find enum item with value '{enum_value}'")

    def __set__(self, instance: 'PyrusModel', value: T_Enum):
        if self._id_field == 'item_id':
            item_id = value.value
        else:
            catalog = _CatalogListWrapper(get_session().get_catalog(self._catalog_id))
            item = catalog.find({self._id_field: value.value})
            if item is None:
                raise ValueError(f"can't find catalog item with field '{self._id_field}'='{value.value}'")
            item_id = item.item_id

        instance._field_values[self.id]['value'] = {
            'item_id': item_id
        }
        instance._changed_fields.add(self.id)


class MultipleChoiceField(BaseField[set[T_Enum]]):
    type = 'multiple_choice'
    _enum: Type[T_Enum]

    def __init__(self, id: int, *, enum: Type[T_Enum]):
        super().__init__(id)
        self._enum = enum

    def __get__(self, instance: 'PyrusModel', owner) -> set[T_Enum]:
        try:
            field_value = instance._field_values[self.id]['value']
        except (KeyError, AttributeError):
            return set()

        choice_ids = field_value['choice_ids']

        return set(self._enum(x) for x in choice_ids)

    def __set__(self, instance: 'PyrusModel', value: set[T_Enum]):
        instance._field_values[self.id]['value'] = {
            'choice_ids': [x.value for x in value]
        }
        instance._changed_fields.add(self.id)
