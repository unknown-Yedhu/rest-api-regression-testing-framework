from framework.response_comparator import ResponseComparator


# --------------------------------------------------
# BASIC COMPARISON TESTS
# --------------------------------------------------

def test_identical_responses():

    comparator = ResponseComparator()

    expected = {
        "id": 1,
        "name": "Laptop",
        "price": 75000
    }

    actual = {
        "id": 1,
        "name": "Laptop",
        "price": 75000
    }

    result = comparator.compare(expected, actual)

    assert result["match"] is True
    assert result["total_differences"] == 0
    assert result["differences"] == []


def test_value_mismatch():

    comparator = ResponseComparator()

    expected = {
        "id": 1,
        "name": "Laptop",
        "price": 75000
    }

    actual = {
        "id": 1,
        "name": "Laptop",
        "price": 80000
    }

    result = comparator.compare(expected, actual)

    assert result["match"] is False
    assert result["total_differences"] == 1

    difference = result["differences"][0]

    assert difference["type"] == "value_mismatch"
    assert difference["path"] == "root.price"
    assert difference["expected"] == 75000
    assert difference["actual"] == 80000


# --------------------------------------------------
# FIELD COMPARISON TESTS
# --------------------------------------------------

def test_missing_field():

    comparator = ResponseComparator()

    expected = {
        "id": 1,
        "name": "Laptop",
        "price": 75000
    }

    actual = {
        "id": 1,
        "name": "Laptop"
    }

    result = comparator.compare(expected, actual)

    assert result["match"] is False

    assert result["differences"][0]["type"] == "missing_field"

    assert result["differences"][0]["path"] == "root.price"


def test_unexpected_field():

    comparator = ResponseComparator()

    expected = {
        "id": 1,
        "name": "Laptop"
    }

    actual = {
        "id": 1,
        "name": "Laptop",
        "stock": 10
    }

    result = comparator.compare(expected, actual)

    assert result["match"] is False

    difference = result["differences"][0]

    assert difference["type"] == "unexpected_field"
    assert difference["path"] == "root.stock"


# --------------------------------------------------
# LIST COMPARISON TESTS
# --------------------------------------------------

def test_list_length_mismatch():

    comparator = ResponseComparator()

    expected = [1, 2, 3]

    actual = [1, 2]

    result = comparator.compare(expected, actual)

    assert result["match"] is False

    assert any(
        difference["type"] == "list_length_mismatch"
        for difference in result["differences"]
    )


def test_list_element_mismatch():

    comparator = ResponseComparator()

    expected = [
        {"id": 1, "name": "Laptop"},
        {"id": 2, "name": "Smartphone"}
    ]

    actual = [
        {"id": 1, "name": "Laptop"},
        {"id": 2, "name": "Tablet"}
    ]

    result = comparator.compare(expected, actual)

    assert result["match"] is False

    assert any(
        difference["type"] == "value_mismatch"
        for difference in result["differences"]
    )


# --------------------------------------------------
# NESTED COMPARISON TESTS
# --------------------------------------------------

def test_nested_value_mismatch():

    comparator = ResponseComparator()

    expected = {
        "success": True,
        "data": {
            "product": {
                "name": "Laptop",
                "price": 75000
            }
        }
    }

    actual = {
        "success": True,
        "data": {
            "product": {
                "name": "Laptop",
                "price": 80000
            }
        }
    }

    result = comparator.compare(expected, actual)

    assert result["match"] is False

    assert result["differences"][0]["path"] == (
        "root.data.product.price"
    )


# --------------------------------------------------
# TYPE MISMATCH TESTS
# --------------------------------------------------

def test_integer_and_boolean_are_not_equal():

    comparator = ResponseComparator()

    expected = {
        "success": 1
    }

    actual = {
        "success": True
    }

    result = comparator.compare(expected, actual)

    assert result["match"] is False

    difference = result["differences"][0]

    assert difference["type"] == "type_mismatch"
    assert difference["path"] == "root.success"
    assert difference["expected"] == 1
    assert difference["actual"] is True

    assert difference["expected_type"] == "int"
    assert difference["actual_type"] == "bool"


def test_string_and_integer_are_not_equal():

    comparator = ResponseComparator()

    expected = {
        "id": 123
    }

    actual = {
        "id": "123"
    }

    result = comparator.compare(expected, actual)

    assert result["match"] is False

    difference = result["differences"][0]

    assert difference["type"] == "type_mismatch"
    assert difference["expected_type"] == "int"
    assert difference["actual_type"] == "str"


# --------------------------------------------------
# NUMERIC TOLERANCE TESTS
# --------------------------------------------------

def test_numeric_tolerance_allows_small_difference():

    comparator = ResponseComparator(
        numeric_tolerance=0.01
    )

    expected = {
        "price": 10.50
    }

    actual = {
        "price": 10.505
    }

    result = comparator.compare(expected, actual)

    assert result["match"] is True
    assert result["total_differences"] == 0


def test_numeric_tolerance_detects_large_difference():

    comparator = ResponseComparator(
        numeric_tolerance=0.01
    )

    expected = {
        "price": 10.50
    }

    actual = {
        "price": 10.75
    }

    result = comparator.compare(expected, actual)

    assert result["match"] is False

    assert result["differences"][0]["type"] == "value_mismatch"


def test_integer_and_float_comparison():

    comparator = ResponseComparator()

    expected = {
        "price": 10
    }

    actual = {
        "price": 10.0
    }

    result = comparator.compare(expected, actual)

    assert result["match"] is True


# --------------------------------------------------
# IGNORE PATH TESTS
# --------------------------------------------------

def test_ignore_specific_field():

    comparator = ResponseComparator(
        ignore_paths=[
            "root.request_id"
        ]
    )

    expected = {
        "request_id": "abc-123",
        "status": "success"
    }

    actual = {
        "request_id": "xyz-789",
        "status": "success"
    }

    result = comparator.compare(expected, actual)

    assert result["match"] is True
    assert result["total_differences"] == 0


def test_ignore_nested_field():

    comparator = ResponseComparator(
        ignore_paths=[
            "root.data.created_at"
        ]
    )

    expected = {
        "data": {
            "name": "Laptop",
            "created_at": "2026-01-01"
        }
    }

    actual = {
        "data": {
            "name": "Laptop",
            "created_at": "2026-11-21"
        }
    }

    result = comparator.compare(expected, actual)

    assert result["match"] is True


def test_ignore_nested_object():

    comparator = ResponseComparator(
        ignore_paths=[
            "root.metadata"
        ]
    )

    expected = {
        "data": {
            "name": "Laptop"
        },
        "metadata": {
            "request_id": "abc",
            "timestamp": "2026-01-01"
        }
    }

    actual = {
        "data": {
            "name": "Laptop"
        },
        "metadata": {
            "request_id": "xyz",
            "timestamp": "2026-11-21"
        }
    }

    result = comparator.compare(expected, actual)

    assert result["match"] is True


def test_ignore_path_with_missing_field():

    comparator = ResponseComparator(
        ignore_paths=[
            "root.request_id"
        ]
    )

    expected = {
        "status": "success",
        "request_id": "abc"
    }

    actual = {
        "status": "success"
    }

    result = comparator.compare(expected, actual)

    assert result["match"] is True


# --------------------------------------------------
# DETERMINISTIC RESULT TESTS
# --------------------------------------------------

def test_difference_order_is_deterministic():

    comparator = ResponseComparator()

    expected = {
        "z": 1,
        "a": 2,
        "m": 3
    }

    actual = {
        "z": 10,
        "a": 20,
        "m": 30
    }

    result = comparator.compare(expected, actual)

    paths = [
        difference["path"]
        for difference in result["differences"]
    ]

    assert paths == [
        "root.a",
        "root.m",
        "root.z"
    ]


# --------------------------------------------------
# DIFFERENCE METADATA TESTS
# --------------------------------------------------

def test_difference_contains_type_information():

    comparator = ResponseComparator()

    expected = {
        "price": 75000
    }

    actual = {
        "price": 80000
    }

    result = comparator.compare(expected, actual)

    difference = result["differences"][0]

    assert "expected_type" in difference
    assert "actual_type" in difference

    assert difference["expected_type"] == "int"
    assert difference["actual_type"] == "int"


def test_missing_field_contains_type_information():

    comparator = ResponseComparator()

    expected = {
        "price": 75000
    }

    actual = {}

    result = comparator.compare(expected, actual)

    difference = result["differences"][0]

    assert difference["type"] == "missing_field"

    assert difference["expected_type"] == "int"
    assert difference["actual_type"] == "NoneType"


def test_unexpected_field_contains_type_information():

    comparator = ResponseComparator()

    expected = {}

    actual = {
        "stock": 10
    }

    result = comparator.compare(expected, actual)

    difference = result["differences"][0]

    assert difference["type"] == "unexpected_field"

    assert difference["expected_type"] == "NoneType"
    assert difference["actual_type"] == "int"