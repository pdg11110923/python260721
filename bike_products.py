import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)


DB_FILE = "products.db"

# 앱 레벨 스타일시트 (QSS)
APP_STYLE = """
QWidget {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #f7fbff, stop:1 #e6f0ff);
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #03314b;
}
QLabel { font-weight: 600; }
QLineEdit {
    background: white;
    border: 1px solid #b9d6ff;
    padding: 6px;
    border-radius: 6px;
}
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #66b3ff, stop:1 #1976d2);
    color: white;
    border-radius: 8px;
    padding: 6px 12px;
    font-weight: 600;
}
QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #7cc0ff, stop:1 #1e88e5); }
QPushButton:pressed { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1669b8, stop:1 #145a9a); }
QTableWidget {
    background: rgba(255,255,255,0.9);
    border: 1px solid #cfe8ff;
    gridline-color: #e6f2ff;
}
QTableWidget::item:selected { background: #cfe8ff; color: #012a40; }
QHeaderView::section {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #eaf6ff, stop:1 #cfe8ff);
    padding: 6px;
    border: 1px solid #d7ecff;
    font-weight: 700;
}
"""


class ProductDB:
    def __init__(self, db_file=DB_FILE):
        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row
        self.create_table()

    def create_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS MyProduct (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
        """
        self.conn.execute(sql)
        self.conn.commit()

    def add_product(self, name, price):
        cur = self.conn.execute("INSERT INTO MyProduct (name, price) VALUES (?, ?)", (name, price))
        self.conn.commit()
        return cur.lastrowid

    def update_product(self, prod_id, name, price):
        self.conn.execute("UPDATE MyProduct SET name=?, price=? WHERE id=?", (name, price, prod_id))
        self.conn.commit()

    def delete_product(self, prod_id):
        self.conn.execute("DELETE FROM MyProduct WHERE id=?", (prod_id,))
        self.conn.commit()

    def search(self, name_query=None):
        if name_query:
            cur = self.conn.execute("SELECT id, name, price FROM MyProduct WHERE name LIKE ? ORDER BY id", (f"%{name_query}%",))
        else:
            cur = self.conn.execute("SELECT id, name, price FROM MyProduct ORDER BY id")
        return cur.fetchall()


class ProductManager(QWidget):
    def __init__(self):
        super().__init__()
        self.db = ProductDB()
        self.setWindowTitle("자전거 용품 관리")
        self.resize(600, 400)
        self._build_ui()
        self.load_table()

    def _build_ui(self):
        v = QVBoxLayout()

        # 입력 영역
        form = QHBoxLayout()

        self.id_label = QLineEdit()
        self.id_label.setReadOnly(True)
        self.id_label.setPlaceholderText("ID (자동생성)")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("상품명")

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("가격 (숫자)")

        form.addWidget(QLabel("ID:"))
        form.addWidget(self.id_label)
        form.addWidget(QLabel("이름:"))
        form.addWidget(self.name_input)
        form.addWidget(QLabel("가격:"))
        form.addWidget(self.price_input)

        v.addLayout(form)

        # 버튼 영역
        btns = QHBoxLayout()
        self.add_btn = QPushButton("입력")
        self.update_btn = QPushButton("수정")
        self.delete_btn = QPushButton("삭제")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("검색어 (이름)")
        self.search_btn = QPushButton("검색")
        self.refresh_btn = QPushButton("전체")

        btns.addWidget(self.add_btn)
        btns.addWidget(self.update_btn)
        btns.addWidget(self.delete_btn)
        btns.addStretch()
        btns.addWidget(self.search_input)
        btns.addWidget(self.search_btn)
        btns.addWidget(self.refresh_btn)

        v.addLayout(btns)

        # 테이블
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["id", "name", "price"])
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        # 미려한 표시를 위한 설정
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        v.addWidget(self.table)

        self.setLayout(v)

        # 시그널
        self.add_btn.clicked.connect(self.on_add)
        self.update_btn.clicked.connect(self.on_update)
        self.delete_btn.clicked.connect(self.on_delete)
        self.search_btn.clicked.connect(self.on_search)
        self.refresh_btn.clicked.connect(self.on_refresh)
        self.table.cellClicked.connect(self.on_table_click)

    def load_table(self, name_query=None):
        rows = self.db.search(name_query)
        self.table.setRowCount(0)
        for r in rows:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(r["id"])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(r["name"]))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(r["price"])))

    def on_add(self):
        name = self.name_input.text().strip()
        price_text = self.price_input.text().strip()
        if not name or not price_text:
            QMessageBox.warning(self, "입력 오류", "이름과 가격을 모두 입력하세요.")
            return
        try:
            price = float(price_text)
        except ValueError:
            QMessageBox.warning(self, "입력 오류", "가격은 숫자여야 합니다.")
            return
        self.db.add_product(name, price)
        self.clear_inputs()
        self.load_table()

    def on_update(self):
        id_text = self.id_label.text().strip()
        if not id_text:
            QMessageBox.warning(self, "수정 오류", "수정할 항목을 테이블에서 선택하세요.")
            return
        try:
            prod_id = int(id_text)
            price = float(self.price_input.text().strip())
            name = self.name_input.text().strip()
        except ValueError:
            QMessageBox.warning(self, "수정 오류", "ID와 가격 형식을 확인하세요.")
            return
        self.db.update_product(prod_id, name, price)
        self.clear_inputs()
        self.load_table()

    def on_delete(self):
        id_text = self.id_label.text().strip()
        if not id_text:
            QMessageBox.warning(self, "삭제 오류", "삭제할 항목을 테이블에서 선택하세요.")
            return
        prod_id = int(id_text)
        reply = QMessageBox.question(self, "삭제 확인", f"ID {prod_id} 항목을 삭제하시겠습니까?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_product(prod_id)
            self.clear_inputs()
            self.load_table()

    def on_search(self):
        q = self.search_input.text().strip()
        self.load_table(name_query=q if q else None)

    def on_refresh(self):
        self.search_input.clear()
        self.load_table()

    def on_table_click(self, row, col):
        id_item = self.table.item(row, 0)
        name_item = self.table.item(row, 1)
        price_item = self.table.item(row, 2)
        if id_item:
            self.id_label.setText(id_item.text())
        if name_item:
            self.name_input.setText(name_item.text())
        if price_item:
            self.price_input.setText(price_item.text())

    def clear_inputs(self):
        self.id_label.clear()
        self.name_input.clear()
        self.price_input.clear()


def main():
    app = QApplication(sys.argv)
    # 앱 레벨 스타일 적용
    app.setStyleSheet(APP_STYLE)
    win = ProductManager()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
