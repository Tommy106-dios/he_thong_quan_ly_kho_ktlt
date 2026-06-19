# -*- coding: utf-8 -*-

class Transaction:
    """Thực thể Giao dịch (Phiếu Nhập/Xuất)"""
    def __init__(self, id, tx_type, created_date, user_id, supplier_id=None, receiver_or_note=None):
        """Đầu vào: id (str) – Mã định danh duy nhất của giao dịch.
            tx_type (str) – Loại giao dịch, nhận giá trị "NHAP" hoặc "XUAT".
            created_date (str) – Ngày tạo giao dịch theo định dạng ISO.
            user_id (str) – Mã người dùng thực hiện giao dịch (khóa ngoại liên kết đến User).
            supplier_id (str | None, optional) – Mã nhà cung cấp, chỉ áp dụng cho phiếu nhập kho, mặc định là None.
            receiver_or_note (str | None, optional) – Người nhận hoặc ghi chú, chỉ áp dụng cho phiếu xuất kho, mặc định là None.
        Đầu ra: Không có giá trị trả về. Khởi tạo các thuộc tính cho đối tượng.
        Mô tả chức năng: Phương thức khởi tạo gán các giá trị đầu vào cho đối tượng Transaction.
            Thuộc tính supplier_id chỉ có ý nghĩa khi type = "NHAP" và receiver_or_note chỉ có ý nghĩa khi type = "XUAT".
        """
        self.id = id
        self.type = tx_type  # "NHAP" hoặc "XUAT"
        self.created_date = created_date
        self.user_id = user_id
        self.supplier_id = supplier_id
        self.receiver_or_note = receiver_or_note

    def to_dict(self):
        """Đầu vào: self – Đối tượng Transaction hiện tại.
        Đầu ra: dict – Dictionary luôn chứa: "id", "type", "createdDate", "userId".
            Nếu type là "NHAP" → bổ sung "supplierId". Nếu type là "XUAT" → bổ sung "receiverOrNote".
        Mô tả chức năng: Serialize đối tượng sang dictionary với logic điều kiện: tùy loại giao dịch,
            dictionary kết quả chứa các trường dữ liệu khác nhau, giúp tối ưu dung lượng lưu trữ.
        """
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
        """Đầu vào: cls – Tham chiếu đến lớp Transaction.
            data (dict | None) – Dictionary chứa dữ liệu giao dịch.
        Đầu ra: Transaction | None – Đối tượng Transaction hoặc None nếu data rỗng.
        Mô tả chức năng: Deserialize từ dictionary sang đối tượng Transaction. Đọc tất cả các trường
            có thể có và để constructor xử lý giá trị None cho các trường không tồn tại,
            tương thích với cả hai loại giao dịch.
        """
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
