from __future__ import annotations

import contextlib
from functools import lru_cache
from typing import Any, Optional, TYPE_CHECKING, Iterable

from pyrus.models.requests import FormRegisterRequest, TaskCommentRequest

if TYPE_CHECKING:
    from pyrus import PyrusAPI
    from pyrus.models.entities import FormRegisterFilter


class PyrusORMSession:
    def __init__(self, pyrus_api: PyrusAPI):
        self.pyrus_api = pyrus_api

    @lru_cache(maxsize=512)
    def get_catalog(self, catalog_id: int):
        from pyrus_orm.catalog import CatalogItem

        catalog = self.pyrus_api.get_catalog(catalog_id)
        headers = [x.name for x in catalog.catalog_headers]
        return [
            CatalogItem(
                item_id=item.item_id,
                catalog_id=catalog_id,
                headers=headers,
                values_row=item.values,
                values=dict(zip(headers, item.values))
            )
            for item in catalog.items
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

    def update_task(self, task_id: int, field_updates: list[Any], comment: Optional[str] = None) -> None:
        response = self.pyrus_api._perform_post_request(
            self.pyrus_api._create_url(f'/tasks/{task_id}/comments'),
            {
                'text': comment,
                'field_updates': field_updates,
            }
        )
        if 'error' in response:
            raise Exception(response['error'])  # TODO: proper error handling

        if not response.get('task'):
            raise Exception('no task received')

        return response['task']

    def create_task(self, data: dict[str, Any]) -> dict[str, Any]:
        response = self.pyrus_api._perform_post_request(
            self.pyrus_api._create_url(f'/tasks'),
            data
        )
        if 'error' in response:
            raise Exception(response['error'])  # TODO: proper error handling

        if not response.get('task'):
            raise Exception('no task received')

        return response['task']

    def get_filtered_tasks(
        self,
        form_id: int,
        include_archived: bool = False,
        steps: Iterable[int] = (),
        filters: Iterable[FormRegisterFilter] = (),
        only: Iterable[int] = (),
    ):
        request = FormRegisterRequest(
            include_archived=include_archived,
            steps=list(steps),
            filters=filters,
        )
        if only:
            request.field_ids = only


        response = self.pyrus_api._perform_post_request(
            self.pyrus_api._create_url(f'/forms/{form_id}/register'),
            request,
        )
        if 'error' in response:
            raise Exception(response['error'])  # TODO: proper error handling

        return response.get('tasks', [])

    def comment_task(self, task_id: int, comment: str) -> None:
        self.pyrus_api.comment_task(task_id, TaskCommentRequest(text=comment))


_session: Optional[PyrusORMSession] = None


def get_session() -> PyrusORMSession:
    global _session
    assert _session is not None, 'no pyrus-orm session is set. ' \
                                 'try calling set_session_global or use `with set_session(..):`'
    return _session


@contextlib.contextmanager
def set_session(session: PyrusORMSession):
    assert isinstance(session, PyrusORMSession)
    global _session
    prev_value = _session

    _session = session
    yield
    _session = prev_value


def set_session_global(session: PyrusORMSession) -> None:
    global _session
    _session = session
