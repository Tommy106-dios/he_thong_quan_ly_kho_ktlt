# -*- coding: utf-8 -*-

class Product:
    """Thực thể Sản phẩm"""
    def __init__(self, id, name, category_id, price, stock_quantity=0, min_stock_level=0, max_stock_level=0):
        """Đầu vào: id (str) – Mã định danh duy nhất của sản phẩm.
            name (str) – Tên sản phẩm.
            category_id (str) – Mã danh mục mà sản phẩm thuộc về (khóa ngoại liên kết đến Category).
            price (float) – Đơn giá của sản phẩm.
            stock_quantity (int, optional) – Số lượng tồn kho hiện tại, mặc định là 0.
            min_stock_level (int, optional) – Mức tồn kho tối thiểu cho phép, mặc định là 0.
            max_stock_level (int, optional) – Mức tồn kho tối đa cho phép, mặc định là 0.
        Đầu ra: Không có giá trị trả về. Khởi tạo các thuộc tính tương ứng cho đối tượng.
        Mô tả chức năng: Phương thức khởi tạo (constructor) gán các giá trị đầu vào cho các thuộc tính
            của đối tượng Product. Các thuộc tính min_stock_level và max_stock_level phục vụ chức năng
            cảnh báo tồn kho khi số lượng vượt ngưỡng cho phép.
        """
        self.id = id
        self.name = name
        self.category_id = category_id
        self.price = price
        self.stock_quantity = stock_quantity
        self.min_stock_level = min_stock_level
        self.max_stock_level = max_stock_level

    def to_dict(self):
        """Đầu vào: self – Đối tượng Product hiện tại.
        Đầu ra: dict – Dictionary chứa các cặp khóa-giá trị: "id", "name", "categoryId", "price", "stockQuantity", "minStockLevel", "maxStockLevel".
        Mô tả chức năng: Chuyển đổi đối tượng Product sang dictionary.
            Các tên thuộc tính snake_case của Python được ánh xạ sang camelCase phù hợp với quy ước lưu trữ JSON.
        """
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
        """Đầu vào: cls – Tham chiếu đến lớp Product.
            data (dict | None) – Dictionary chứa dữ liệu sản phẩm.
        Đầu ra: Product | None – Đối tượng Product hoặc None nếu data rỗng.
        Mô tả chức năng: Chuyển đổi ngược (deserialize) từ dictionary sang đối tượng Product.
            Các thuộc tính tồn kho có giá trị mặc định 0 nếu không tồn tại trong dữ liệu đầu vào,
            đảm bảo tương thích ngược.
        """
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
