# -*- coding: utf-8 -*-

class Supplier:
    """Thực thể Nhà cung cấp"""
    def __init__(self, id, name, phone="", address=""):
        self.id = id
        self.name = name
        self.phone = phone
        self.address = address

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "address": self.address
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            phone=data.get("phone", ""),
            address=data.get("address", "")
        )
