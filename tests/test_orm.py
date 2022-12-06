import copy
from typing import Any

import pytest
from pyrus import PyrusAPI

from pyrus_orm.fields import TextField, NumericField, CatalogField
from pyrus_orm.model import PyrusModel
from pyrus_orm.session import PyrusORMSession, set_session
from pyrus_orm.types import CatalogItem


@pytest.fixture
def form_data() -> dict[str, Any]:
    return {
        "id": 11610,
        "create_date": "2017-08-20T12:31:14Z",
        "last_modified_date": "2017-08-23T10:20:11Z",
        "current_step": 1,
        "fields": [
            {
                "id": 10,
                "type": "text",
                "name": "Purpose",
                "value": "IT conference in Amsterdam"
            },
            {
                "id": 20,
                "type": "number",
                "name": "counter",
                "value": 42,
            },
            {
                "id": 30,
                "value": {
                    "item_id": 80797460,
                    "item_ids": [
                        80797460
                    ],
                    "headers": [
                        "Vendor Name",
                        "Vendor Code"
                    ],
                    "values": [
                        "GE",
                        "123"
                    ],
                    "rows": [
                        [
                            "GE",
                            "123"
                        ]
                    ]
                }
            }
        ]
    }


@pytest.fixture
def session():
    with set_session(PyrusORMSession(PyrusAPI())):
        yield


class Model(PyrusModel):
    purpose = TextField(10)
    counter = NumericField(20)
    vendor = CatalogField(30, catalog_id=12345)


def test_text_field(form_data: dict[str, Any], session: PyrusORMSession) -> None:
    model = Model.from_pyrus_data(form_data)

    assert model.purpose == 'IT conference in Amsterdam'

    new_value = 'Other entertainments in Amsterdam'
    model.purpose = new_value
    assert model.purpose == new_value

    new_data = copy.deepcopy(form_data)
    new_data['fields'][0]['value'] = new_value

    assert model.as_pyrus_data() == new_data


def test_numeric_field(form_data: dict[str, Any], session: PyrusORMSession) -> None:
    model = Model.from_pyrus_data(form_data)
    assert model.counter == 42
    model.counter += 1
    assert model.counter == 43


def test_single_catalog_field(form_data: dict[str, Any], session: PyrusORMSession) -> None:
    model = Model.from_pyrus_data(form_data)

    assert model.vendor.item_id == 80797460

    model.vendor = CatalogItem(item_id=123)
    assert model.vendor == CatalogItem(item_id=123)
