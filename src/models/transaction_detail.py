# -*- coding: utf-8 -*-

class TransactionDetail:
    """Thực thể Chi tiết Giao dịch"""
    def __init__(self, transaction_id, product_id, quantity, unit_price):
        self.transaction_id = transaction_id
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price

    def to_dict(self):
        return {
            "transactionId": self.transaction_id,
            "productId": self.product_id,
            "quantity": self.quantity,
            "unitPrice": self.unit_price
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            transaction_id=data.get("transactionId"),
            product_id=data.get("productId"),
            quantity=data.get("quantity"),
            unit_price=data.get("unitPrice")
        )
