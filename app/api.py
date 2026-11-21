from flask import Flask, jsonify, request
import time

app = Flask(__name__)

# Initial product database
INITIAL_PRODUCTS = [
    {
        "id": 1,
        "name": "Laptop",
        "category": "Electronics",
        "price": 75000,
        "stock": 10
    },
    {
        "id": 2,
        "name": "Smartphone",
        "category": "Electronics",
        "price": 25000,
        "stock": 20
    },
    {
        "id": 3,
        "name": "Headphones",
        "category": "Accessories",
        "price": 3000,
        "stock": 15
    },
    {
        "id": 4,
        "name": "Keyboard",
        "category": "Accessories",
        "price": 1500,
        "stock": 30
    }
]

# Mutable product database
products = [product.copy() for product in INITIAL_PRODUCTS]


@app.route("/")
def home():
    return jsonify({
        "message": "REST API Regression Testing Framework API",
        "version": "1.0",
        "endpoints": [
            "/api/health",
            "/api/products",
            "/api/products/<id>"
        ]
    })


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": time.time()
    }), 200


@app.route("/api/products", methods=["GET"])
def get_products():
    return jsonify(products), 200


@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = next(
        (p for p in products if p["id"] == product_id),
        None
    )

    if product:
        return jsonify(product), 200

    return jsonify({
        "error": "Product not found"
    }), 404


@app.route("/api/products", methods=["POST"])
def create_product():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Invalid JSON"
        }), 400

    required_fields = ["name", "category", "price", "stock"]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": f"Missing field: {field}"
            }), 400

    new_product = {
        "id": max(
            [p["id"] for p in products],
            default=0
        ) + 1,
        "name": data["name"],
        "category": data["category"],
        "price": data["price"],
        "stock": data["stock"]
    }

    products.append(new_product)

    return jsonify(new_product), 201


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    global products

    product = next(
        (p for p in products if p["id"] == product_id),
        None
    )

    if not product:
        return jsonify({
            "error": "Product not found"
        }), 404

    products = [
        p for p in products
        if p["id"] != product_id
    ]

    return jsonify({
        "message": "Product deleted successfully"
    }), 200


@app.route("/api/products/reset", methods=["POST"])
def reset_products():
    global products

    products = [
        product.copy()
        for product in INITIAL_PRODUCTS
    ]

    return jsonify({
        "message": "Products reset successfully",
        "count": len(products)
    }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)