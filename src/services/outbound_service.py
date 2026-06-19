# -*- coding: utf-8 -*-
from datetime import datetime
from ..models import Transaction, TransactionDetail

class OutboundService:
    """Xử lý nghiệp vụ Xuất kho hàng hóa"""
    def __init__(self, file_handler, products, transactions, transaction_details):
        self.file_handler = file_handler
        self.products = products
        self.transactions = transactions
        self.transaction_details = transaction_details

    def _generate_px_id(self):
        """Đầu vào: self – Đối tượng OutboundService hiện tại.
        Đầu ra: str – Mã phiếu xuất mới theo định dạng "PXxxxx" (ví dụ: "PX1001").
        Mô tả chức năng: Tương tự _generate_pn_id() của InboundService nhưng dành cho phiếu xuất.
            Duyệt giao dịch loại "XUAT" có tiền tố "PX", tìm số thứ tự lớn nhất rồi tăng thêm 1.
        """
        max_num = 1000
        for t in self.transactions:
            if t.type == "XUAT" and t.id.startswith("PX"):
                try:
                    num = int(t.id[2:])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        return f"PX{max_num + 1}"

    def get_product(self, product_id):
        """Đầu vào: self – Đối tượng OutboundService hiện tại.
            product_id (str) – Mã sản phẩm cần tra cứu.
        Đầu ra: Product | None – Đối tượng Product nếu tìm thấy, None nếu không tồn tại.
        Mô tả chức năng: Tra cứu sản phẩm theo mã ID trong danh sách self.products,
            sử dụng hàm next() với generator expression.
            Được sử dụng bởi giao diện để kiểm tra tồn kho trước khi xuất.
        """
        return next((p for p in self.products if p.id == product_id), None)

    def export_stock(self, receiver_or_note, user_id, items_data):
        """Đầu vào: receiver_or_note (str) – Người nhận hàng hoặc ghi chú cho phiếu xuất.
            user_id (str) – Mã người dùng thực hiện xuất kho.
            items_data (list[dict]) – Danh sách mặt hàng cần xuất,
                mỗi phần tử gồm: product_id (str), quantity (int).
        Đầu ra: str – Mã phiếu xuất kho vừa tạo (ví dụ: "PX1001").
        Mô tả chức năng: Thực hiện quy trình xuất kho: sinh mã phiếu tự động, tạo Transaction
            (loại "XUAT"), duyệt từng mặt hàng để kiểm tra tồn kho đủ hay không
            (nếu không đủ, ném ValueError), trừ số lượng tồn kho, tạo TransactionDetail
            với đơn giá lấy từ giá hiện tại của sản phẩm, và lưu toàn bộ thay đổi xuống file JSON.
        """
        tx_id = self._generate_px_id()
        created_date = datetime.now().isoformat()

        # Tạo phiếu xuất
        transaction = Transaction(
            id=tx_id,
            tx_type="XUAT",
            created_date=created_date,
            user_id=user_id,
            receiver_or_note=receiver_or_note
        )

        for item in items_data:
            p_id = item["product_id"]
            qty = item["quantity"]

            product = self.get_product(p_id)
            if not product or product.stock_quantity < qty:
                raise ValueError("Không đủ hàng tồn kho hoặc sản phẩm không tồn tại.")

            # Cập nhật giảm lượng tồn kho
            product.stock_quantity -= qty

            # Tạo chi tiết giao dịch xuất kho với giá bán hiện tại
            detail = TransactionDetail(
                transaction_id=tx_id,
                product_id=p_id,
                quantity=qty,
                unit_price=product.price
            )
            self.transaction_details.append(detail)

        self.transactions.append(transaction)

        # Lưu dữ liệu
        self.file_handler.save_products(self.products)
        self.file_handler.save_transactions(self.transactions)
        self.file_handler.save_transaction_details(self.transaction_details)

        return tx_id
