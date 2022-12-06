import contextlib
from typing import Any, Optional

from pyrus import PyrusAPI


class PyrusORMSession:
    def __init__(self, pyrus_api: PyrusAPI):
        self.pyrus_api = pyrus_api

    def get_catalog(self, catalog_id: int):
        from pyrus_orm.types import CatalogItem

        items = self.pyrus_api.get_catalog(catalog_id).items
        return [
            CatalogItem(
                item_id=item.item_id,
                catalog_id=catalog_id,
                headers=item.headers,
                values_row=item.values,
            )
            for item in items
        ]

    def get_task_raw(self, task_id: int) -> dict[str, Any]:
        response = self.pyrus_api._perform_get_request(
            self.pyrus_api._create_url(f'/tasks/{task_id}')
        )
        if 'error' in response:
            raise Exception(response['error'])  # TODO: proper error handling

        if not response.get('task'):
            raise Exception('no task received')

        return response['task']


_session: Optional[PyrusORMSession] = None


def get_session() -> PyrusORMSession:
    global _session
    assert _session is not None
    return _session


@contextlib.contextmanager
def set_session(session: PyrusORMSession):
    global _session
    prev_value = _session

    _session = session
    yield
    _session = prev_value
