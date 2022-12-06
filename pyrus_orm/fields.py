from typing import Literal, Optional, Generic, TypeVar, Union, TYPE_CHECKING

from .types import Flag, Status, CatalogItem

if TYPE_CHECKING:
    from .model import PyrusModel

FieldType = Literal[
    'text', 'money', 'number', 'date', 'time',
    'checkmark', 'due_date', 'due_date_time',
    'email', 'phone', 'flag', 'step', 'status',
    'creation_date', 'note',
]

T = TypeVar('T')


class BaseField(Generic[T]):
    id: int
    name: Optional[str] = None
    type: FieldType

    def __init__(self, id: int):
        self.id = id

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance: 'PyrusModel', owner) -> T:
        return instance._field_values[self.id]['value']

    def __set__(self, instance, value: T):
        instance._field_values[self.id]['value'] = value


class TextField(BaseField[str]):
    type = 'text'


class NumericField(BaseField[float]):
    type = 'number'


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


class CatalogField(BaseField):
    type = 'catalog'
    _catalog_id: int

    def __init__(self, id: int, *, catalog_id: int):
        super().__init__(id)
        self._catalog_id = catalog_id

    def __get__(self, instance: PyrusModel, owner):
        value = instance._field_values[self.id]['value']
        return CatalogItem.from_pyrus_data(
            catalog_id=self._catalog_id,
            data=value,
        )

    def __set__(self, instance: PyrusModel, value: Union[CatalogItem, int]):
        if isinstance(value, CatalogItem):
            item_id = value.item_id
        else:
            item_id = value

        # TODO: check if item_id is valid
        instance._field_values[self.id]['value'] = {
            'item_id': item_id
        }
