# -*- coding: utf-8 -*-

class Product:
    """Thực thể Sản phẩm"""
    def __init__(self, id, name, category_id, price, stock_quantity=0, min_stock_level=0, max_stock_level=0):
        self.id = id
        self.name = name
        self.category_id = category_id
        self.price = price
        self.stock_quantity = stock_quantity
        self.min_stock_level = min_stock_level
        self.max_stock_level = max_stock_level

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "categoryId": self.category_id,
            "price": self.price,
            "stockQuantity": self.stock_quantity,
            "minStockLevel": self.min_stock_level,
            "maxStockLevel": self.max_stock_level
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            category_id=data.get("categoryId"),
            price=data.get("price"),
            stock_quantity=data.get("stockQuantity", 0),
            min_stock_level=data.get("minStockLevel", 0),
            max_stock_level=data.get("maxStockLevel", 0)
        )
