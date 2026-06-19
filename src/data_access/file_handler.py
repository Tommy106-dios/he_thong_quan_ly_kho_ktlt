# -*- coding: utf-8 -*-
import json
import os
from ..models import User, Category, Supplier, Product, Transaction, TransactionDetail

DEFAULT_USERS = [
    {"id": "US001", "username": "admin", "password": "123", "fullName": "Nguyễn Văn A", "role": "Admin"},
    {"id": "US002", "username": "kho", "password": "123", "fullName": "Lê Văn B", "role": "NhanVienKho"}
]

DEFAULT_CATEGORIES = [
    {"id": "CAT01", "name": "Vật liệu", "description": "Thép, xi măng, gạch cát"},
    {"id": "CAT02", "name": "Hóa chất", "description": "Sơn, dung môi"},
    {"id": "CAT03", "name": "Phụ kiện", "description": "Ống nước, đai ốc"}
]

DEFAULT_SUPPLIERS = [
    {"id": "SUP01", "name": "Công ty Cổ phần Thép Hòa Phát", "phone": "0123456789", "address": "Hà Nội"},
    {"id": "SUP02", "name": "Tổng Công ty Xi măng Việt Nam", "phone": "0987654321", "address": "TP. HCM"},
    {"id": "SUP03", "name": "Nhà máy Gạch Tuynel Bình Dương", "phone": "0112233445", "address": "Bình Dương"}
]

DEFAULT_PRODUCTS = [
    {"id": "SP001", "name": "Thép Hòa Phát D10", "categoryId": "CAT01", "price": 15500.0, "stockQuantity": 120, "minStockLevel": 50, "maxStockLevel": 500},
    {"id": "SP002", "name": "Xi măng Vicem Hà Tiên", "categoryId": "CAT01", "price": 89000.0, "stockQuantity": 25, "minStockLevel": 40, "maxStockLevel": 300},
    {"id": "SP003", "name": "Gạch tuynel 2 lỗ Bình Dương", "categoryId": "CAT01", "price": 1200.0, "stockQuantity": 2400, "minStockLevel": 500, "maxStockLevel": 2000}
]

DEFAULT_TRANSACTIONS = [
    {"id": "TX001", "type": "NHAP", "createdDate": "2026-06-05T08:30:00Z", "userId": "US002", "supplierId": "SUP01"},
    {"id": "TX002", "type": "XUAT", "createdDate": "2026-06-06T10:15:00Z", "userId": "US002", "receiverOrNote": "Công trình Landmark"}
]

DEFAULT_TRANSACTION_DETAILS = [
    {"transactionId": "TX001", "productId": "SP001", "quantity": 100, "unitPrice": 15000.0},
    {"transactionId": "TX002", "productId": "SP001", "quantity": 50, "unitPrice": 15500.0}
]

class FileHandler:
    """Tầng xử lý đọc/ghi cơ sở dữ liệu JSON vật lý"""
    def __init__(self, data_dir=None):
        """Đầu vào: data_dir (str | None, optional) – Đường dẫn thư mục chứa các file JSON dữ liệu,
            mặc định là None (sử dụng thư mục data/ tại gốc dự án).
        Đầu ra: Không có giá trị trả về. Khởi tạo thuộc tính data_dir và tự động tạo thư mục nếu chưa tồn tại.
        Mô tả chức năng: Xác định đường dẫn vật lý đến thư mục dữ liệu. Nếu data_dir không được truyền,
            tự động tính toán dựa trên vị trí tương đối của file source code.
            Tạo thư mục nếu chưa có bằng os.makedirs().
        """
        if data_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.data_dir = os.path.join(base_dir, "data")
        else:
            self.data_dir = data_dir

        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _get_path(self, filename):
        return os.path.join(self.data_dir, filename)

    def _read_file(self, filename, default_data):
        """Đầu vào: filename (str) – Tên file JSON cần đọc (ví dụ: "products.json").
            default_data (list) – Dữ liệu mặc định được sử dụng nếu file chưa tồn tại hoặc lỗi đọc.
        Đầu ra: list – Danh sách dictionary được phân tích từ file JSON,
            hoặc default_data nếu file không tồn tại hoặc gặp lỗi.
        Mô tả chức năng: Đọc nội dung file JSON theo đường dẫn. Nếu file chưa tồn tại, ghi dữ liệu
            mặc định vào file mới rồi trả về. Nếu file bị lỗi hoặc rỗng, trả về dữ liệu mặc định.
            Xử lý mã hóa UTF-8 cho tiếng Việt.
        """
        path = self._get_path(filename)
        if not os.path.exists(path):
            self._write_file(filename, default_data)
            return default_data
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                return json.loads(content) if content else default_data
        except Exception:
            return default_data

    def _write_file(self, filename, data):
        """Đầu vào: filename (str) – Tên file JSON cần ghi.
            data (list) – Danh sách dictionary cần ghi xuống file.
        Đầu ra: Không có giá trị trả về. Ghi dữ liệu xuống file JSON.
        Mô tả chức năng: Ghi danh sách dictionary xuống file JSON với định dạng thụt lề 4 ký tự (indent=4),
            hỗ trợ Unicode tiếng Việt (ensure_ascii=False). Bắt lỗi và in thông báo nếu ghi thất bại.
        """
        path = self._get_path(filename)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Lỗi ghi file {filename}: {e}")

    # Users
    def load_users(self):
        return [User.from_dict(d) for d in self._read_file("users.json", DEFAULT_USERS)]

    def save_users(self, users):
        self._write_file("users.json", [u.to_dict() for u in users])

    # Categories
    def load_categories(self):
        return [Category.from_dict(d) for d in self._read_file("categories.json", DEFAULT_CATEGORIES)]

    def save_categories(self, categories):
        self._write_file("categories.json", [c.to_dict() for c in categories])

    # Suppliers
    def load_suppliers(self):
        return [Supplier.from_dict(d) for d in self._read_file("suppliers.json", DEFAULT_SUPPLIERS)]

    def save_suppliers(self, suppliers):
        self._write_file("suppliers.json", [s.to_dict() for s in suppliers])

    # Products
    def load_products(self):
        """Đầu vào: self – Đối tượng FileHandler hiện tại.
        Đầu ra: list[Product] – Danh sách các đối tượng Product được tạo từ file products.json.
        Mô tả chức năng: Đọc file products.json, chuyển đổi mỗi phần tử dictionary thành đối tượng Product
            thông qua Product.from_dict(). Nếu file chưa tồn tại, tạo file mới với dữ liệu mẫu mặc định.
        """
        return [Product.from_dict(d) for d in self._read_file("products.json", DEFAULT_PRODUCTS)]

    def save_products(self, products):
        """Đầu vào: self – Đối tượng FileHandler hiện tại.
            products (list[Product]) – Danh sách các đối tượng Product cần lưu.
        Đầu ra: Không có giá trị trả về. Ghi dữ liệu xuống file products.json.
        Mô tả chức năng: Chuyển đổi mỗi đối tượng Product thành dictionary qua to_dict(),
            sau đó ghi toàn bộ danh sách xuống file JSON.
        """
        self._write_file("products.json", [p.to_dict() for p in products])

    # Transactions
    def load_transactions(self):
        return [Transaction.from_dict(d) for d in self._read_file("transactions.json", DEFAULT_TRANSACTIONS)]

    def save_transactions(self, transactions):
        self._write_file("transactions.json", [t.to_dict() for t in transactions])

    # TransactionDetails
    def load_transaction_details(self):
        return [TransactionDetail.from_dict(d) for d in self._read_file("transaction_details.json", DEFAULT_TRANSACTION_DETAILS)]

    def save_transaction_details(self, details):
        self._write_file("transaction_details.json", [d.to_dict() for d in details])
