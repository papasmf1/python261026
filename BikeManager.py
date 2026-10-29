import sqlite3

DB_NAME = "bike.db"


class BikeManager:
    def __init__(self, db_name=DB_NAME):
        self.conn = sqlite3.connect(db_name)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS MyProduct ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "name TEXT NOT NULL, price INTEGER NOT NULL)"
        )
        self.conn.commit()

    def get_all(self):
        return self.conn.execute(
            "SELECT id, name, price FROM MyProduct ORDER BY id").fetchall()

    def add(self, name, price):
        self.conn.execute(
            "INSERT INTO MyProduct (name, price) VALUES (?, ?)", (name, price))
        self.conn.commit()

    def update(self, item_id, name, price):
        self.conn.execute("UPDATE MyProduct SET name=?, price=? WHERE id=?",
                          (name, price, item_id))
        self.conn.commit()

    def delete(self, item_id):
        self.conn.execute("DELETE FROM MyProduct WHERE id=?", (item_id,))
        self.conn.commit()

    def search(self, keyword):
        return self.conn.execute(
            "SELECT id, name, price FROM MyProduct WHERE name LIKE ? ORDER BY id",
            (f"%{keyword}%",)).fetchall()

    def close(self):
        self.conn.close()
