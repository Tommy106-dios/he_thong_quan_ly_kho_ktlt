# -*- coding: utf-8 -*-

class Category:
    """Thực thể Danh mục sản phẩm"""
    def __init__(self, id, name, description=""):
        self.id = id
        self.name = name
        self.description = description

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description", "")
        )
