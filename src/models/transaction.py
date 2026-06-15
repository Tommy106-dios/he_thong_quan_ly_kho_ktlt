# -*- coding: utf-8 -*-

class Transaction:
    """Thực thể Giao dịch (Phiếu Nhập/Xuất)"""
    def __init__(self, id, tx_type, created_date, user_id, supplier_id=None, receiver_or_note=None):
        self.id = id
        self.type = tx_type  # "NHAP" hoặc "XUAT"
        self.created_date = created_date
        self.user_id = user_id
        self.supplier_id = supplier_id
        self.receiver_or_note = receiver_or_note

    def to_dict(self):
        data = {
            "id": self.id,
            "type": self.type,
            "createdDate": self.created_date,
            "userId": self.user_id
        }
        if self.type == "NHAP":
            data["supplierId"] = self.supplier_id
        elif self.type == "XUAT":
            data["receiverOrNote"] = self.receiver_or_note
        return data

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            id=data.get("id"),
            tx_type=data.get("type"),
            created_date=data.get("createdDate"),
            user_id=data.get("userId"),
            supplier_id=data.get("supplierId"),
            receiver_or_note=data.get("receiverOrNote")
        )
