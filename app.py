from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3

app = Flask(__name__)
app.secret_key = "prodigy_task_3_secret"


# Database connection
def get_db():
    conn = sqlite3.connect("store.db")
    conn.row_factory = sqlite3.Row
    return conn


# Create products table
def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            image TEXT NOT NULL
        )
    """)

    count = conn.execute(
        "SELECT COUNT(*) FROM products"
    ).fetchone()[0]

    if count == 0:
        products = [
            (
                "Wireless Headphones",
                "Comfortable headphones with clear sound.",
                1499,
                "https://placehold.co/400x300?text=Headphones"
            ),
            (
                "Smart Watch",
                "Smart watch for everyday use.",
                1999,
                "https://placehold.co/400x300?text=Smart+Watch"
            ),
            (
                "Backpack",
                "Stylish backpack for college and travel.",
                899,
                "https://placehold.co/400x300?text=Backpack"
            ),
            (
                "Water Bottle",
                "Reusable bottle for daily use.",
                299,
                "https://placehold.co/400x300?text=Water+Bottle"
            )
        ]

        conn.executemany("""
            INSERT INTO products (name, description, price, image)
            VALUES (?, ?, ?, ?)
        """, products)

    conn.commit()
    conn.close()


# Home page
@app.route("/")
def index():
    conn = get_db()
    products = conn.execute(
        "SELECT * FROM products"
    ).fetchall()
    conn.close()

    cart = session.get("cart", {})
    cart_count = sum(cart.values())

    return render_template(
        "index.html",
        products=products,
        cart_count=cart_count
    )


# Add product to cart
@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    conn = get_db()

    product = conn.execute(
        "SELECT id FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    conn.close()

    if product is None:
        return "Product not found", 404

    cart = session.get("cart", {})
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1

    session["cart"] = cart

    return redirect(url_for("index"))


# View cart
@app.route("/cart")
def view_cart():
    cart = session.get("cart", {})
    cart_items = []
    total = 0

    conn = get_db()

    for product_id, quantity in cart.items():
        product = conn.execute(
            "SELECT * FROM products WHERE id = ?",
            (int(product_id),)
        ).fetchone()

        if product:
            subtotal = product["price"] * quantity

            cart_items.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })

            total += subtotal

    conn.close()

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total,
        cart_count=sum(cart.values())
    )


# Remove product from cart
@app.route("/remove_from_cart/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    cart.pop(str(product_id), None)
    session["cart"] = cart

    return redirect(url_for("view_cart"))


# Clear cart
@app.route("/clear_cart", methods=["POST"])
def clear_cart():
    session["cart"] = {}
    return redirect(url_for("view_cart"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)