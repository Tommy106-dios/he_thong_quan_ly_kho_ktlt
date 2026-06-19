# -*- coding: utf-8 -*-
from datetime import datetime
from ..models import Transaction, TransactionDetail, Product

class InboundService:
    """Xử lý nghiệp vụ Nhập kho hàng hóa"""
    def __init__(self, file_handler, products, transactions, transaction_details, suppliers):
        """Đầu vào: file_handler (FileHandler) – Đối tượng xử lý đọc/ghi file dữ liệu.
            products (list[Product]) – Danh sách sản phẩm hiện có trong hệ thống.
            transactions (list[Transaction]) – Danh sách giao dịch đã ghi nhận.
            transaction_details (list[TransactionDetail]) – Danh sách chi tiết giao dịch.
            suppliers (list[Supplier]) – Danh sách nhà cung cấp.
        Đầu ra: Không có giá trị trả về. Khởi tạo các thuộc tính dịch vụ.
        Mô tả chức năng: Thiết lập dịch vụ nhập kho với tham chiếu đến các danh sách dữ liệu dùng chung,
            cho phép cập nhật trực tiếp dữ liệu trong bộ nhớ.
        """
        self.file_handler = file_handler
        self.products = products
        self.transactions = transactions
        self.transaction_details = transaction_details
        self.suppliers = suppliers

    def _generate_pn_id(self):
        """Đầu vào: self – Đối tượng InboundService hiện tại.
        Đầu ra: str – Mã phiếu nhập mới theo định dạng "PNxxxx" (ví dụ: "PN1001", "PN1002").
        Mô tả chức năng: Duyệt toàn bộ danh sách giao dịch, tìm mã phiếu nhập (bắt đầu bằng "PN")
            có số thứ tự lớn nhất, rồi tăng thêm 1 để sinh mã mới.
            Giá trị khởi đầu là 1000, nên mã đầu tiên là PN1001.
        """
        max_num = 1000
        for t in self.transactions:
            if t.type == "NHAP" and t.id.startswith("PN"):
                try:
                    num = int(t.id[2:])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        return f"PN{max_num + 1}"

    def check_product_exists(self, product_id):
        """Đầu vào: self – Đối tượng InboundService hiện tại.
            product_id (str) – Mã sản phẩm cần kiểm tra.
        Đầu ra: bool – True nếu sản phẩm đã tồn tại trong danh sách, False nếu chưa.
        Mô tả chức năng: Kiểm tra xem mã sản phẩm đã có trong danh sách self.products hay chưa,
            sử dụng hàm any() để so khớp theo trường id. Kết quả quyết định giao diện yêu cầu
            người dùng nhập thông tin bổ sung (nếu sản phẩm mới).
        """
        return any(p.id == product_id for p in self.products)

    def import_stock(self, supplier_id, user_id, items_data):
        """Đầu vào: supplier_id (str) – Mã nhà cung cấp.
            user_id (str) – Mã người dùng thực hiện nhập kho.
            items_data (list[dict]) – Danh sách các mặt hàng cần nhập, mỗi phần tử gồm:
                product_id (str), quantity (int), unit_price (float).
                Nếu sản phẩm mới: name, category_id, min_stock_level, max_stock_level.
        Đầu ra: str – Mã phiếu nhập kho vừa tạo (ví dụ: "PN1001").
        Mô tả chức năng: Thực hiện toàn bộ quy trình nhập kho: sinh mã phiếu tự động, tạo đối tượng
            Transaction (loại "NHAP"), duyệt từng mặt hàng để cộng dồn tồn kho (nếu đã tồn tại)
            hoặc thêm sản phẩm mới (nếu chưa có), tạo các bản ghi TransactionDetail tương ứng,
            và cuối cùng lưu toàn bộ thay đổi xuống file JSON.
        """
        tx_id = self._generate_pn_id()
        created_date = datetime.now().isoformat()

        # Tạo phiếu nhập
        transaction = Transaction(
            id=tx_id,
            tx_type="NHAP",
            created_date=created_date,
            user_id=user_id,
            supplier_id=supplier_id
        )

        for item in items_data:
            p_id = item["product_id"]
            qty = item["quantity"]
            price = item["unit_price"]

            product = next((p for p in self.products if p.id == p_id), None)
            if product:
                # Trường hợp A: Đã tồn tại -> cộng dồn và cập nhật giá bán hiện tại
                product.stock_quantity += qty
                product.price = price
            else:
                # Trường hợp B: Chưa tồn tại -> thêm mới
                new_prod = Product(
                    id=p_id,
                    name=item["name"],
                    category_id=item["category_id"],
                    price=price,
                    stock_quantity=qty,
                    min_stock_level=item["min_stock_level"],
                    max_stock_level=item["max_stock_level"]
                )
                self.products.append(new_prod)

            # Tạo chi tiết giao dịch
            detail = TransactionDetail(
                transaction_id=tx_id,
                product_id=p_id,
                quantity=qty,
                unit_price=price
            )
            self.transaction_details.append(detail)

        self.transactions.append(transaction)

        # Lưu xuống CSDL JSON
        self.file_handler.save_products(self.products)
        self.file_handler.save_transactions(self.transactions)
        self.file_handler.save_transaction_details(self.transaction_details)

        return tx_id
