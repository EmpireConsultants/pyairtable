import pytest
import os
from pyairtable import Base, Table
from pyairtable.metadata import get_base_schema, get_api_bases, get_table_schema


INTEGRATION_BASE_NAME = "Test Wrapper"


# TODO - re-use integration fixtures
@pytest.fixture
def table():
    base_id = "appaPqizdsNHDvlEm"
    table_name = "My Table"
    table = Table(os.environ["AIRTABLE_API_KEY"], base_id, table_name)
    yield table
    records = table.all()
    table.batch_delete([r["id"] for r in records])


# TODO - re-use integration fixtures
@pytest.fixture
def base():
    base_id = "appaPqizdsNHDvlEm"
    base = Base(os.environ["AIRTABLE_API_KEY"], base_id)
    yield base
    table_name = "My Table"
    records = base.all(table_name)
    base.batch_delete(table_name, [r["id"] for r in records])


@pytest.mark.integration
def test_get_api_bases(base: Base):
    rv = get_api_bases(base)
    assert INTEGRATION_BASE_NAME in [b["name"] for b in rv["bases"]]


@pytest.mark.skip("metadata api returning 404 for base schema")
def test_get_base_schema(base: Base):
    rv = get_base_schema(base)
    assert len(rv["tables"]) == 3


@pytest.mark.skip("metadata api returning 404 for base schema")
def test_get_table_schema(table: Table):
    rv = get_table_schema(table)
    assert rv and rv["name"] == table.table_name
