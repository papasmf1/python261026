import random
import sqlite3

DB_NAME = "MyProduct.db"


class ProductDB:
    def __init__(self, db_name=DB_NAME):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS Products (
                productID INTEGER PRIMARY KEY,
                productName TEXT NOT NULL,
                productPrice INTEGER NOT NULL
            )"""
        )
        self.conn.commit()

    def insert(self, product_id, name, price):
        self.conn.execute(
            "INSERT INTO Products (productID, productName, productPrice) VALUES (?, ?, ?)",
            (product_id, name, price),
        )
        self.conn.commit()

    def insert_many(self, rows):
        self.conn.executemany(
            "INSERT INTO Products (productID, productName, productPrice) VALUES (?, ?, ?)",
            rows,
        )
        self.conn.commit()

    def update(self, product_id, name, price):
        cur = self.conn.execute(
            "UPDATE Products SET productName = ?, productPrice = ? WHERE productID = ?",
            (name, price, product_id),
        )
        self.conn.commit()
        return cur.rowcount

    def delete(self, product_id):
        cur = self.conn.execute(
            "DELETE FROM Products WHERE productID = ?", (product_id,)
        )
        self.conn.commit()
        return cur.rowcount

    def select(self, product_id=None):
        if product_id is None:
            cur = self.conn.execute(
                "SELECT productID, productName, productPrice FROM Products ORDER BY productID"
            )
        else:
            cur = self.conn.execute(
                "SELECT productID, productName, productPrice FROM Products WHERE productID = ?",
                (product_id,),
            )
        return cur.fetchall()

    def count(self):
        return self.conn.execute("SELECT COUNT(*) FROM Products").fetchone()[0]

    def close(self):
        self.conn.close()


def make_sample_data(n=1000):
    kinds = ["TV", "냉장고", "세탁기", "노트북", "스마트폰", "태블릿", "에어컨",
             "청소기", "전자레인지", "헤드폰", "모니터", "키보드", "마우스", "스피커"]
    brands = ["삼성", "LG", "애플", "소니", "레노버", "델", "HP", "필립스"]
    rng = random.Random(42)
    return [
        (i, f"{rng.choice(brands)} {rng.choice(kinds)} {i:04d}", rng.randrange(10000, 3000001, 1000))
        for i in range(1, n + 1)
    ]


if __name__ == "__main__":
    db = ProductDB()
    if db.count() == 0:
        db.insert_many(make_sample_data(1000))
    print("총 제품 수:", db.count())

    db.insert(1001, "테스트 제품", 99000)
    print("INSERT :", db.select(1001))
    db.update(1001, "테스트 제품(수정)", 88000)
    print("UPDATE :", db.select(1001))
    db.delete(1001)
    print("DELETE :", db.select(1001))

    print("SELECT (상위 5개)")
    for row in db.select()[:5]:
        print(row)
    db.close()
