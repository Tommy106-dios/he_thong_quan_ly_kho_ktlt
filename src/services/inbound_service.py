# -*- coding: utf-8 -*-
from datetime import datetime
from ..models import Transaction, TransactionDetail, Product

class InboundService:
    """Xử lý nghiệp vụ Nhập kho hàng hóa"""
    def __init__(self, file_handler, products, transactions, transaction_details, suppliers):
        self.file_handler = file_handler
        self.products = products
        self.transactions = transactions
        self.transaction_details = transaction_details
        self.suppliers = suppliers

    def _generate_pn_id(self):
        """Sinh mã phiếu nhập tự tăng bắt đầu từ PN1001"""
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
        """Kiểm tra sản phẩm đã tồn tại hay chưa"""
        return any(p.id == product_id for p in self.products)

    def import_stock(self, supplier_id, user_id, items_data):
        """
        Thực hiện nhập kho danh sách hàng hóa
        items_data: danh sách dict gồm:
           - product_id
           - quantity
           - unit_price
           - (nếu mới): name, category_id, min_stock_level, max_stock_level
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
