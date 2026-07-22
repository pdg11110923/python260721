import sqlite3


class ProductList:
    def __init__(self, db_name="MyProduct.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Products (
                productID INTEGER PRIMARY KEY,
                productName TEXT NOT NULL,
                productPrice INTEGER NOT NULL
            )
            """
        )
        self.conn.commit()

    def insert_product(self, product_id, product_name, product_price):
        self.cursor.execute(
            "INSERT INTO Products (productID, productName, productPrice) VALUES (?, ?, ?)",
            (product_id, product_name, product_price),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def update_product(self, product_id, new_name=None, new_price=None):
        updates = []
        values = []

        if new_name is not None:
            updates.append("productName = ?")
            values.append(new_name)

        if new_price is not None:
            updates.append("productPrice = ?")
            values.append(new_price)

        if not updates:
            return False

        values.append(product_id)
        self.cursor.execute(
            f"UPDATE Products SET {', '.join(updates)} WHERE productID = ?",
            tuple(values),
        )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_product(self, product_id):
        self.cursor.execute("DELETE FROM Products WHERE productID = ?", (product_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def select_all(self):
        self.cursor.execute(
            "SELECT productID, productName, productPrice FROM Products ORDER BY productID"
        )
        return self.cursor.fetchall()

    def select_by_id(self, product_id):
        self.cursor.execute(
            "SELECT productID, productName, productPrice FROM Products WHERE productID = ?",
            (product_id,),
        )
        return self.cursor.fetchone()

    def prepare_sample_data(self, count=1000):
        self.cursor.execute("DELETE FROM Products")
        self.conn.commit()

        sample_data = [
            (i, f"Product {i}", 10000 + i)
            for i in range(1, count + 1)
        ]
        self.cursor.executemany(
            "INSERT INTO Products (productID, productName, productPrice) VALUES (?, ?, ?)",
            sample_data,
        )
        self.conn.commit()
        return len(sample_data)

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    product_db = ProductList()
    count = product_db.prepare_sample_data(1000)

    print(f"샘플 데이터 {count}개 준비 완료")
    print("첫 번째 제품:", product_db.select_by_id(1))

    product_db.update_product(1, new_name="Updated Product 1", new_price=99999)
    print("수정 후 첫 번째 제품:", product_db.select_by_id(1))

    product_db.delete_product(2)
    print("2번 제품 삭제 후 조회:", product_db.select_by_id(2))

    print("총 제품 수:", len(product_db.select_all()))
    product_db.close()
