"""SQLite setup and query helpers for the restaurant chatbot."""

import sqlite3
from typing import Any, Dict, List, Tuple, cast


def initialize_database(db_path: str = "restaurant.sqlite") -> None:
    """Create tables and seed starter data if this is a new database."""
    with sqlite3.connect(db_path) as conn:

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS menu_items (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name     TEXT NOT NULL,
                category      TEXT NOT NULL,
                description   TEXT NOT NULL,
                price         REAL NOT NULL,
                is_vegetarian INTEGER NOT NULL DEFAULT 0,
                is_spicy      INTEGER NOT NULL DEFAULT 0,
                is_available  INTEGER NOT NULL DEFAULT 1
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS restaurant_details (
                id      INTEGER PRIMARY KEY CHECK (id = 1),
                name    TEXT NOT NULL,
                address TEXT NOT NULL,
                phone   TEXT NOT NULL,
                email   TEXT NOT NULL,
                website TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS opening_hours (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                day_of_week TEXT NOT NULL UNIQUE,
                open_time   TEXT NOT NULL,
                close_time  TEXT NOT NULL,
                notes       TEXT
            )
            """
        )

        # New table for reservations
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reservations (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                date          TEXT NOT NULL,
                time          TEXT NOT NULL,
                party_size    INTEGER NOT NULL,
                contact       TEXT
            )
            """
        )

        _seed_if_empty(conn)


def _seed_if_empty(conn: sqlite3.Connection) -> None:
    """Insert a comprehensive Asian restaurant dataset once, keeping reruns idempotent."""
    has_menu    = conn.execute("SELECT COUNT(*) FROM menu_items").fetchone()[0] > 0
    has_details = conn.execute("SELECT COUNT(*) FROM restaurant_details").fetchone()[0] > 0
    has_hours   = conn.execute("SELECT COUNT(*) FROM opening_hours").fetchone()[0] > 0

    if not has_menu:
        menu_rows = [
            # ── Starters & Salads ──
            ("Salted Edamame", "Starter", "Steamed soybeans with coarse sea salt", 6.50, 1, 0, 1),
            ("Spicy Garlic Edamame", "Starter", "Wok-tossed soybeans in spicy garlic sauce", 7.50, 1, 1, 1),
            ("Vegetable Spring Rolls", "Starter", "Crispy rolls served with sweet chili sauce (3 pcs)", 8.00, 1, 0, 1),
            ("Chicken Gyoza", "Starter", "Pan-fried Japanese chicken dumplings (5 pcs)", 9.50, 0, 0, 1),
            ("Pork Belly Bao Buns", "Starter", "Steamed buns with braised pork, cucumber, and hoisin", 12.00, 0, 0, 1),
            ("Spicy Tuna Crispy Rice", "Starter", "Crispy sushi rice topped with spicy tuna and jalapeño", 13.00, 0, 1, 1),
            ("Wakame Seaweed Salad", "Salad", "Traditional Japanese marinated seaweed salad", 7.00, 1, 0, 1),
            ("Som Tum (Papaya Salad)", "Salad", "Green papaya, peanuts, tomatoes, and spicy lime dressing", 11.00, 1, 1, 1),

            # ── Soups ──
            ("Classic Miso Soup", "Soup", "Tofu, seaweed, and scallions in a dashi broth", 5.00, 1, 0, 1),
            ("Tom Yum Goong", "Soup", "Spicy and sour Thai soup with shrimp, mushrooms, and lemongrass", 11.50, 0, 1, 1),
            ("Vegan Pho", "Soup", "Vietnamese noodle soup with tofu and vegetable broth", 14.00, 1, 0, 1),

            # ── Sushi Rolls & Sashimi ──
            ("California Roll", "Sushi", "Crab meat, avocado, and cucumber", 9.00, 0, 0, 1),
            ("Spicy Salmon Roll", "Sushi", "Fresh salmon, spicy mayo, and cucumber", 11.00, 0, 1, 1),
            ("Dragon Roll", "Sushi", "Shrimp tempura topped with eel, avocado, and unagi sauce", 16.50, 0, 0, 1),
            ("Rainbow Roll", "Sushi", "California roll topped with assorted fresh sashimi", 15.00, 0, 0, 1),
            ("Spider Roll", "Sushi", "Crispy soft shell crab, avocado, and eel sauce", 17.00, 0, 0, 1),
            ("Vegan Zen Roll", "Sushi", "Avocado, cucumber, carrots, and pickled radish", 9.50, 1, 0, 1),
            ("Volcano Roll", "Sushi", "Baked crab and scallop mix over a spicy tuna roll", 18.00, 0, 1, 1),
            ("Sashimi Deluxe", "Sushi", "Chef's selection of 12 pieces of premium raw fish", 28.00, 0, 0, 1),

            # ── Noodles ──
            ("Pad Thai", "Noodles", "Rice noodles, peanuts, egg, bean sprouts, and tamarind sauce", 15.50, 0, 0, 1),
            ("Spicy Dan Dan Mian", "Noodles", "Szechuan style noodles with minced pork and chili oil", 16.00, 0, 1, 1),
            ("Beef Yaki Soba", "Noodles", "Stir-fried buckwheat noodles with tender beef and vegetables", 17.50, 0, 0, 1),
            ("Seafood Udon", "Noodles", "Thick wheat noodles in a savory broth with shrimp and squid", 19.00, 0, 0, 1),
            ("Tofu Drunken Noodles", "Noodles", "Spicy wide rice noodles with Thai basil and vegetables", 15.00, 1, 1, 1),

            # ── Wok & Curries (Mains) ──
            ("General Tso's Chicken", "Main", "Crispy chicken in a sweet and spicy sauce with broccoli", 18.00, 0, 1, 1),
            ("Kung Pao Beef", "Main", "Stir-fried beef with peanuts, zucchini, and dried chilies", 19.50, 0, 1, 1),
            ("Teriyaki Salmon", "Main", "Grilled salmon fillet glazed with homemade teriyaki sauce", 22.00, 0, 0, 1),
            ("Miso Glazed Eggplant", "Main", "Roasted eggplant with sweet miso glaze and sesame seeds", 14.50, 1, 0, 1),
            ("Thai Green Curry", "Main", "Chicken and bamboo shoots in a spicy coconut green curry", 17.50, 0, 1, 1),
            ("Massaman Curry", "Main", "Rich and mild beef curry with potatoes and roasted peanuts", 18.50, 0, 0, 1),

            # ── Desserts ──
            ("Mochi Ice Cream Trio", "Dessert", "Mango, green tea, and strawberry Japanese ice cream", 8.50, 1, 0, 1),
            ("Matcha Cheesecake", "Dessert", "Green tea infused creamy cheesecake with a graham crust", 9.00, 1, 0, 1),
            ("Mango Sticky Rice", "Dessert", "Sweet coconut rice topped with fresh mango slices", 10.00, 1, 0, 1),
            ("Fried Banana", "Dessert", "Crispy battered banana served with vanilla ice cream", 8.00, 1, 0, 1),

            # ── Drinks ──
            ("House Sake (Hot/Cold)", "Drinks", "Traditional Japanese premium rice wine", 10.00, 1, 0, 1),
            ("Plum Wine (Umeshu)", "Drinks", "Sweet Japanese liqueur made from fresh plums", 9.00, 1, 0, 1),
            ("Sapporo Draft Beer", "Drinks", "Classic Japanese premium lager", 6.50, 1, 0, 1),
            ("Thai Iced Tea", "Drinks", "Sweet black tea with milk and exotic spices", 5.50, 1, 0, 1),
            ("Matcha Latte", "Drinks", "Ceremonial grade green tea with steamed milk", 6.00, 1, 0, 1),
            ("Lychee Lemonade", "Drinks", "Refreshing lemonade infused with fresh lychee syrup", 5.00, 1, 0, 1)
        ]
        conn.executemany(
            """
            INSERT INTO menu_items
            (item_name, category, description, price, is_vegetarian, is_spicy, is_available)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            menu_rows,
        )

    if not has_details:
        conn.execute(
            """INSERT INTO restaurant_details (id, name, address, phone, email, website)
               VALUES (1, ?, ?, ?, ?, ?)""",
            (
                "Sakura Asian Kitchen",
                "88 Lotus Avenue, Central District",
                "+1-555-0888",
                "hello@sakura-asian.example",
                "www.sakura-asian.example",
            ),
        )

    if not has_hours:
        hours_rows = [
            ("Monday",    "11:30", "22:00", ""),
            ("Tuesday",   "11:30", "22:00", ""),
            ("Wednesday", "11:30", "22:00", ""),
            ("Thursday",  "11:30", "23:00", ""),
            ("Friday",    "11:30", "23:30", "Late night menu starts at 22:00"),
            ("Saturday",  "12:00", "23:30", "Sushi happy hour until 16:00"),
            ("Sunday",    "12:00", "21:00", "Family platters available all day"),
        ]
        conn.executemany(
            """INSERT INTO opening_hours (day_of_week, open_time, close_time, notes)
               VALUES (?, ?, ?, ?)""",
            hours_rows,
        )


def get_menu_items(db_path: str) -> List[Dict[str, Any]]:
    """Return all menu items when no specific search terms are provided."""
    sql = (
        "SELECT item_name, category, description, price, is_vegetarian, is_spicy, is_available "
        "FROM menu_items ORDER BY category, item_name"
    )
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql).fetchall()

    return [cast(Dict[str, Any], dict(row)) for row in rows]


def search_menu_items(db_path: str, query: str) -> List[Dict[str, Any]]:
    """Simple LIKE-based search with synonym expansion and boolean mapping."""

    # Sanitize the query: remove hidden surrogate characters that crash SQLite
    clean_query = "".join(c for c in query if not (0xD800 <= ord(c) <= 0xDFFF))

    tokens = [t.strip().lower() for t in clean_query.split() if len(t.strip()) >= 3]

    # Add common synonyms and handle plurals
    expanded_tokens = []
    for t in tokens:
        expanded_tokens.append(t)
        if t == "vegan":
            expanded_tokens.append("vegetarian")
        elif t in ("drink", "beverage", "beverages"):
            expanded_tokens.append("drinks")
        elif t == "mains":
            expanded_tokens.append("main")
        elif t == "starters":
            expanded_tokens.append("starter")
        elif t == "desserts":
            expanded_tokens.append("dessert")

    tokens = list(set(expanded_tokens))

    if not tokens:
        return get_menu_items(db_path)

    where_clauses = []
    params: List[str] = []

    if "vegetarian" in tokens:
        where_clauses.append("is_vegetarian = 1")
    if "spicy" in tokens:
        where_clauses.append("is_spicy = 1")

    for token in tokens[:6]:
        where_clauses.append("(LOWER(item_name) LIKE ? OR LOWER(description) LIKE ? OR LOWER(category) LIKE ?)")
        wildcard = f"%{token}%"
        params.extend([wildcard, wildcard, wildcard])

    sql = (
        "SELECT item_name, category, description, price, is_vegetarian, is_spicy, is_available "
        "FROM menu_items WHERE " + " OR ".join(where_clauses) + " ORDER BY category, item_name"
    )

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, params).fetchall()

    return [cast(Dict[str, Any], dict(row)) for row in rows]


def get_restaurant_details_and_hours(db_path: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Return the single restaurant details row and all opening-hours rows."""
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        details_row = conn.execute(
            "SELECT name, address, phone, email, website FROM restaurant_details WHERE id = 1"
        ).fetchone()
        hours_rows = conn.execute(
            "SELECT day_of_week, open_time, close_time, notes FROM opening_hours ORDER BY id"
        ).fetchall()

    details = cast(Dict[str, Any], dict(details_row)) if details_row else {}
    hours   = [cast(Dict[str, Any], dict(row)) for row in hours_rows]
    return details, hours

def book_reservation(
    db_path: str,
    customer_name: str,
    date: str,
    time: str,
    party_size: int,
    contact: str = None
) -> int:
    """Insert a new reservation and return the generated booking ID."""

    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO reservations (customer_name, date, time, party_size, contact)
            VALUES (?, ?, ?, ?, ?)
            """,
            (customer_name, date, time, party_size, contact)
        )

        return cursor.lastrowid


def find_duplicate_reservation(
    db_path: str,
    customer_name: str,
    date: str,
    time: str,
    party_size: int,
    contact: str
):
    """Return the booking ID when an identical reservation already exists."""

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT id
            FROM reservations
            WHERE LOWER(customer_name) = LOWER(?)
              AND date = ?
              AND time = ?
              AND party_size = ?
              AND LOWER(COALESCE(contact, '')) = LOWER(?)
            ORDER BY id
            LIMIT 1
            """,
            (customer_name, date, time, party_size, contact)
        ).fetchone()

    return row[0] if row else None


def cancel_reservation(db_path: str, res_id: int) -> bool:
    """Delete a reservation and return True only when a row was deleted."""

    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "DELETE FROM reservations WHERE id = ?",
            (res_id,)
        )

        return cursor.rowcount > 0