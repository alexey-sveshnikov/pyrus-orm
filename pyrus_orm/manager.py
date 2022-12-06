from typing import TypeVar, Type, Generic

T = TypeVar('T', bound='PyrusModel')


class Manager(Generic[T]):
    _model: Type[T]

    def __init__(self, model: Type[T]):
        self._model = model

    def get(self, task_id: int):
        from pyrus_orm.session import get_session

        data = get_session().get_task_raw(task_id)
        return self._model.from_pyrus_data(data)


class _ManagerProperty(Generic[T]):
    def __init__(self, model: Type[T]):
        self._model = model

    def __get__(self, instance, owner):
        return Manager(self._model)
