
import pytest
from framework.api_test_runner import APITestRunner


@pytest.fixture
def runner():
    return APITestRunner(
        base_url="http://127.0.0.1:5000"
    )


# --------------------------------------------------
# GET HEALTH ENDPOINT
# --------------------------------------------------

def test_get_health_endpoint(runner):

    response = runner.get("/api/health")

    assert response["success"] is True
    assert response["status_code"] == 200

    assert response["response_body"]["status"] == "healthy"


# --------------------------------------------------
# GET ALL PRODUCTS
# --------------------------------------------------

def test_get_products_endpoint(runner):

    response = runner.get("/api/products")

    assert response["success"] is True
    assert response["status_code"] == 200

    products = response["response_body"]

    assert isinstance(products, list)
    assert len(products) >= 3

    assert all(
        "id" in product
        and "name" in product
        and "category" in product
        and "price" in product
        and "stock" in product
        for product in products
    )


# --------------------------------------------------
# GET SINGLE PRODUCT
# --------------------------------------------------

def test_get_single_product(runner):

    response = runner.get("/api/products/1")

    assert response["success"] is True
    assert response["status_code"] == 200

    product = response["response_body"]

    assert product["id"] == 1
    assert product["name"] == "Laptop"
    assert product["category"] == "Electronics"
    assert product["price"] == 75000
    assert product["stock"] == 10


# --------------------------------------------------
# GET NONEXISTENT PRODUCT
# --------------------------------------------------

def test_get_nonexistent_product(runner):

    response = runner.get("/api/products/999")

    assert response["success"] is True
    assert response["status_code"] == 404

    assert response["response_body"]["error"] == "Product not found"


# --------------------------------------------------
# POST, GET, DELETE PRODUCT
# --------------------------------------------------

def test_post_create_product(runner):

    # Reset the API database before the test
    reset_response = runner.post(
        "/api/products/reset"
    )

    assert reset_response["success"] is True
    assert reset_response["status_code"] == 200

    # Get the original product count
    initial_response = runner.get(
        "/api/products"
    )

    assert initial_response["success"] is True
    assert initial_response["status_code"] == 200

    initial_products = initial_response["response_body"]
    initial_count = len(initial_products)

    product_data = {
        "name": "Regression Test Product",
        "category": "Testing",
        "price": 1000,
        "stock": 10
    }

    created_product_id = None

    try:

        # ------------------------------------------
        # CREATE PRODUCT
        # ------------------------------------------

        response = runner.post(
            "/api/products",
            json_data=product_data
        )

        assert response["success"] is True
        assert response["status_code"] == 201

        created_product = response["response_body"]

        created_product_id = created_product["id"]

        assert created_product["name"] == product_data["name"]
        assert created_product["category"] == product_data["category"]
        assert created_product["price"] == product_data["price"]
        assert created_product["stock"] == product_data["stock"]

        # ------------------------------------------
        # VERIFY PRODUCT WAS CREATED
        # ------------------------------------------

        get_response = runner.get(
            f"/api/products/{created_product_id}"
        )

        assert get_response["success"] is True
        assert get_response["status_code"] == 200

        retrieved_product = get_response["response_body"]

        assert retrieved_product["id"] == created_product_id
        assert retrieved_product["name"] == product_data["name"]

        # ------------------------------------------
        # VERIFY PRODUCT COUNT INCREASED
        # ------------------------------------------

        products_response = runner.get(
            "/api/products"
        )

        assert products_response["success"] is True

        current_products = products_response["response_body"]

        assert len(current_products) == initial_count + 1

        # ------------------------------------------
        # DELETE CREATED PRODUCT
        # ------------------------------------------

        delete_response = runner.delete(
            f"/api/products/{created_product_id}"
        )

        assert delete_response["success"] is True
        assert delete_response["status_code"] == 200

        assert (
            delete_response["response_body"]["message"]
            == "Product deleted successfully"
        )

        # ------------------------------------------
        # VERIFY PRODUCT WAS DELETED
        # ------------------------------------------

        deleted_product_response = runner.get(
            f"/api/products/{created_product_id}"
        )

        assert deleted_product_response["status_code"] == 404

        assert (
            deleted_product_response["response_body"]["error"]
            == "Product not found"
        )

        # ------------------------------------------
        # VERIFY DATABASE IS CLEAN
        # ------------------------------------------

        final_response = runner.get(
            "/api/products"
        )

        assert final_response["success"] is True

        final_products = final_response["response_body"]

        assert len(final_products) == initial_count

        assert all(
            product["id"] != created_product_id
            for product in final_products
        )

    finally:

        # Always restore the original database
        runner.post(
            "/api/products/reset"
        )


# --------------------------------------------------
# RESPONSE HEADERS
# --------------------------------------------------

def test_response_contains_headers(runner):

    response = runner.get("/api/health")

    assert response["success"] is True

    assert isinstance(response["headers"], dict)

    assert "Content-Type" in response["headers"]


# --------------------------------------------------
# RESPONSE TIME
# --------------------------------------------------

def test_response_contains_response_time(runner):

    response = runner.get("/api/health")

    assert response["success"] is True

    assert response["response_time"] is not None

    assert response["response_time"] >= 0


# --------------------------------------------------
# CONNECTION ERROR
# --------------------------------------------------

def test_connection_error():

    runner = APITestRunner(
        base_url="http://127.0.0.1:5999"
    )

    response = runner.get("/api/health")

    assert response["success"] is False

    assert response["error"] == "Unable to connect to API"
