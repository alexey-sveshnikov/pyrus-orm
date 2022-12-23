from typing import TypeVar, Type, Generic, Optional, Iterable

from pyrus.models.entities import EqualsFilter

from .catalog import CatalogItem
from .session import get_session

T = TypeVar('T', bound='PyrusModel')


class Manager(Generic[T]):
    _model: Type[T]

    def __init__(self, model: Type[T]):
        self._model = model

    def get(self, task_id: int) -> Optional[T]:
        from pyrus_orm.session import get_session

        data = get_session().get_task_raw(task_id)
        return self._model.from_pyrus_data(data)

    def get_filtered(
        self,
        *,
        include_archived: bool = False,
        steps: Iterable[int] = (),
        only: Iterable[str] = (),
        **kwargs,
    ) -> list[T]:
        fields = self._model.Meta.fields

        filters = []
        for k, v in kwargs.items():
            assert k in fields, f'field {k} not found in model fields'

            if isinstance(v, CatalogItem):
                value = v.item_id
            else:
                value = v

            filters.append(EqualsFilter(fields[k].id, value))

        field_ids = []
        for field_name in only:
            field_ids.append(self._model.Meta.fields[field_name].id)

        tasks = get_session().get_filtered_tasks(
            self._model.Meta.form_id,
            include_archived=include_archived,
            steps=steps,
            filters=filters,
            only=field_ids or None
        )
        return [self._model.from_pyrus_data(x) for x in tasks]


class _ManagerProperty(Generic[T]):
    def __init__(self, model: Type[T]):
        self._model = model

    def __get__(self, instance, owner) -> Manager[T]:
        return Manager(self._model)
