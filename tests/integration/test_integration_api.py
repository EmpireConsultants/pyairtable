import pytest
import os
from pyairtable import Base, Table
from pyairtable import formulas as fo
from uuid import uuid4


@pytest.fixture
def cols():
    class Columns:
        # Table should have these Columns
        TEXT = "text"  # Text
        NUM = "number"  # Number, float
        BOOL = "boolean"  # Boolean

    return Columns


# TODO - re-use integration fixtures
@pytest.fixture
def base():
    base_id = "appaPqizdsNHDvlEm"
    base = Base(os.environ["AIRTABLE_API_KEY"], base_id)
    yield base
    table_name = "My Table"
    records = base.all(table_name)
    base.batch_delete(table_name, [r["id"] for r in records])


# TODO - re-use integration fixtures
@pytest.fixture
def table():
    base_id = "appaPqizdsNHDvlEm"
    table_name = "My Table"
    table = Table(os.environ["AIRTABLE_API_KEY"], base_id, table_name)
    yield table
    records = table.all()
    table.batch_delete([r["id"] for r in records])


@pytest.mark.integration
def test_integration_table(table, cols):
    # Create / Get
    rec = table.create({cols.TEXT: "A", cols.NUM: 1, cols.BOOL: True})
    rv_get = table.get(rec["id"])
    assert rv_get["fields"][cols.TEXT] == "A"

    # Update
    rv = table.update(rec["id"], {cols.TEXT: "B"})
    assert rv["fields"][cols.TEXT] == "B"
    assert rv["fields"][cols.NUM] == 1

    # Replace
    rv = table.update(rec["id"], {cols.NUM: 2}, replace=True)
    assert rv["fields"] == {cols.NUM: 2}

    # Get all
    records = table.all()
    assert rec["id"] in [r["id"] for r in records]

    # Delete
    rv = table.delete(rec["id"])
    assert rv["deleted"]

    # Batch Create
    COUNT = 15
    records = table.batch_create(
        [{cols.TEXT: "A", cols.NUM: 1, cols.BOOL: True} for _ in range(COUNT)]
    )

    for record in records:
        record["fields"][cols.TEXT] = "C"
    rv_batch_update = table.batch_update(records)
    assert all([r["fields"][cols.TEXT] == "C" for r in rv_batch_update])

    # Batch Delete
    records = table.batch_delete([r["id"] for r in records])
    assert len(records) == COUNT


@pytest.mark.integration
def test_integration_base(base, cols):
    table_name = "My Table"

    # Create / Get
    rec = base.create(table_name, {cols.TEXT: "A", cols.NUM: 1, cols.BOOL: True})
    rv_get = base.get(table_name, rec["id"])
    assert rv_get["fields"][cols.TEXT] == "A"

    # Update
    rv = base.update(table_name, rec["id"], {cols.TEXT: "B"})
    assert rv["fields"][cols.TEXT] == "B"
    assert rv["fields"][cols.NUM] == 1

    # Replace
    rv = base.update(table_name, rec["id"], {cols.NUM: 2}, replace=True)
    assert rv["fields"] == {cols.NUM: 2}

    # Get all
    records = base.all(
        table_name,
    )
    assert rec["id"] in [r["id"] for r in records]

    # Delete
    rv = base.delete(table_name, rec["id"])
    assert rv["deleted"]

    # Batch Create
    COUNT = 15
    records = base.batch_create(
        table_name,
        [{cols.TEXT: "A", cols.NUM: 1, cols.BOOL: True} for _ in range(COUNT)],
    )

    for record in records:
        record["fields"][cols.TEXT] = "C"
    rv_batch_update = base.batch_update(table_name, records)
    assert all([r["fields"][cols.TEXT] == "C" for r in rv_batch_update])

    # Batch Delete
    records = base.batch_delete(table_name, [r["id"] for r in records])
    assert len(records) == COUNT


@pytest.mark.integration
def test_integration_field_equals(table: Table, cols):
    VALUE = "Simeple {}".format(uuid4())
    rv_create = table.create({cols.TEXT: VALUE})
    rv_first = table.first(formula=fo.match({cols.TEXT: VALUE}))
    assert rv_first and rv_first["id"] == rv_create["id"]


@pytest.mark.integration
def test_integration_field_equals_with_quotes(table: Table, cols):
    VALUE = "Contact's Name {}".format(uuid4())
    rv_create = table.create({cols.TEXT: VALUE})
    rv_first = table.first(formula=fo.match({cols.TEXT: VALUE}))
    assert rv_first and rv_first["id"] == rv_create["id"]

    VALUE = 'Some "Quote"  {}'.format(uuid4())
    rv_create = table.create({cols.TEXT: VALUE})
    rv_first = table.first(formula=fo.match({cols.TEXT: VALUE}))
    assert rv_first and rv_first["id"] == rv_create["id"]


@pytest.mark.integration
def test_integration_formula_composition(table: Table, cols):
    text = "Mike's Thing {}".format(uuid4())
    num = 1
    bool_ = True
    rv_create = table.create({cols.TEXT: text, cols.NUM: num, cols.BOOL: bool_})

    formula = fo.AND(
        fo.EQUAL(fo.FIELD(cols.TEXT), fo.to_airtable_value(text)),
        fo.EQUAL(fo.FIELD(cols.NUM), fo.to_airtable_value(num)),
        fo.EQUAL(
            fo.FIELD(cols.BOOL), fo.to_airtable_value(bool_)
        ),  # not needs to be int()
    )
    rv_first = table.first(formula=formula)

    assert rv_first["id"] == rv_create["id"]
