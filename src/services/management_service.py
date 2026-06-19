# -*- coding: utf-8 -*-
from datetime import datetime
from ..models import Category

class ManagementService:
    """Xử lý các nghiệp vụ quản lý hệ thống: Cảnh báo, Tìm kiếm, Lịch sử, Báo cáo"""
    def __init__(self, file_handler, products, transactions, transaction_details, categories, suppliers, users):
        self.file_handler = file_handler
        self.products = products
        self.transactions = transactions
        self.transaction_details = transaction_details
        self.categories = categories
        self.suppliers = suppliers
        self.users = users

    # 1. Cảnh báo tồn kho
    def get_stock_warnings(self):
        """Đầu vào: self – Đối tượng ManagementService hiện tại.
        Đầu ra: tuple(list[Product], list[Product]) – Bộ hai danh sách: danh sách sản phẩm có tồn kho
            thấp hơn mức tối thiểu (low_stock) và danh sách sản phẩm vượt mức tối đa (overstock).
        Mô tả chức năng: Duyệt toàn bộ danh sách sản phẩm, so sánh stock_quantity với min_stock_level
            và max_stock_level để phân loại cảnh báo. Phục vụ chức năng giám sát tồn kho.
        """
        low_stock = [p for p in self.products if p.stock_quantity < p.min_stock_level]
        overstock = [p for p in self.products if p.stock_quantity > p.max_stock_level]
        return low_stock, overstock

    # 2. Tìm kiếm sản phẩm theo Name/ID
    def search_products(self, keyword):
        """Đầu vào: self – Đối tượng ManagementService hiện tại.
            keyword (str) – Từ khóa tìm kiếm (theo mã hoặc tên sản phẩm).
        Đầu ra: list[Product] – Danh sách sản phẩm có mã hoặc tên chứa từ khóa (không phân biệt hoa thường),
            hoặc danh sách rỗng nếu từ khóa trống hoặc không tìm thấy.
        Mô tả chức năng: Chuẩn hóa từ khóa về chữ thường, sau đó lọc danh sách sản phẩm bằng phép
            so khớp chuỗi con (in) trên cả id và name. Hỗ trợ tìm kiếm linh hoạt, không phân biệt hoa/thường.
        """
        kw = keyword.strip().lower()
        if not kw:
            return []
        return [p for p in self.products if kw in p.id.lower() or kw in p.name.lower()]

    # 3. Xem lịch sử nhập xuất
    def get_transaction_history(self, filter_type=None):
        """Đầu vào: self – Đối tượng ManagementService hiện tại.
            filter_type (str | None, optional) – Bộ lọc loại giao dịch: "NHAP", "XUAT",
                hoặc None (hiển thị tất cả).
        Đầu ra: list[Transaction] – Danh sách giao dịch đã lọc và sắp xếp theo ngày tạo giảm dần
            (mới nhất lên đầu).
        Mô tả chức năng: Lọc danh sách giao dịch theo loại (nếu có), sau đó sắp xếp kết quả
            theo created_date giảm dần bằng sorted() với key=lambda. Cho phép xem toàn bộ
            hoặc chỉ nhập/xuất.
        """
        filtered = self.transactions
        if filter_type in ("NHAP", "XUAT"):
            filtered = [t for t in self.transactions if t.type == filter_type]
            
        # Sắp xếp theo CreatedDate giảm dần (mới nhất lên đầu)
        return sorted(filtered, key=lambda x: x.created_date, reverse=True)

    def get_user_name(self, user_id):
        user = next((u for u in self.users if u.id == user_id), None)
        return user.username if user else user_id

    def get_supplier_name(self, supplier_id):
        supplier = next((s for s in self.suppliers if s.id == supplier_id), None)
        return supplier.name if supplier else supplier_id

    # 4. Hiển thị danh mục sản phẩm
    def get_categories_with_counts(self):
        result = []
        for cat in self.categories:
            count = sum(1 for p in self.products if p.category_id == cat.id)
            result.append({
                "category": cat,
                "product_count": count
            })
        return result

    # 5. Thêm 1 danh mục mặt hàng mới
    def add_category(self, cat_id, name, description=""):
        """Đầu vào: cat_id (str) – Mã danh mục mới.
            name (str) – Tên danh mục.
            description (str, optional) – Mô tả danh mục, mặc định là chuỗi rỗng.
        Đầu ra: Category – Đối tượng Category vừa được tạo.
        Mô tả chức năng: Kiểm tra trùng lặp mã danh mục bằng any(). Nếu trùng, ném ValueError.
            Nếu không trùng, tạo đối tượng Category mới, thêm vào danh sách và lưu xuống file JSON.
        """
        # Kiểm tra trùng lặp
        if any(c.id == cat_id for c in self.categories):
            raise ValueError(f"Mã danh mục {cat_id} đã tồn tại.")

        new_cat = Category(id=cat_id, name=name, description=description)
        self.categories.append(new_cat)
        self.file_handler.save_categories(self.categories)
        return new_cat

    # 6. Báo cáo Xuất - Nhập - Tồn (XNT)
    def calculate_xnt(self, start_date_str, end_date_str):
        """Đầu vào: start_date_str (str) – Ngày bắt đầu kỳ báo cáo, định dạng "YYYY-MM-DD".
            end_date_str (str) – Ngày kết thúc kỳ báo cáo, định dạng "YYYY-MM-DD".
        Đầu ra: list[dict] – Danh sách dictionary, mỗi phần tử chứa: "id", "name",
            "tonDau" (tồn đầu kỳ), "tongNhap" (tổng nhập trong kỳ), "tongXuat" (tổng xuất trong kỳ),
            "tonCuoi" (tồn cuối kỳ = tồn đầu + nhập − xuất).
        Mô tả chức năng: Tính toán báo cáo Xuất–Nhập–Tồn cho từng sản phẩm trong khoảng thời gian
            chỉ định. Validate định dạng ngày và kiểm tra ngày bắt đầu ≤ ngày kết thúc
            (ném ValueError nếu vi phạm). Duyệt toàn bộ giao dịch, phân loại thành hai mốc:
            giao dịch trước kỳ (tính tồn đầu kỳ) và giao dịch trong kỳ (tính tổng nhập/xuất).
            Cuối cùng tổng hợp công thức: Tồn cuối = Tồn đầu + Tổng nhập − Tổng xuất.
        """
        # Kiểm tra định dạng ngày không hợp lệ
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Ngày bắt đầu không hợp lệ hoặc không đúng định dạng YYYY-MM-DD.")

        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Ngày kết thúc không hợp lệ hoặc không đúng định dạng YYYY-MM-DD.")

        # Kiểm tra ngày bắt đầu không lớn hơn ngày kết thúc
        if start_date > end_date:
            raise ValueError("Ngày bắt đầu không được lớn hơn ngày kết thúc.")

        # Chuẩn hóa ngày nhập dạng YYYY-MM-DD thành mốc ISO
        start_iso = start_date_str + "T00:00:00"
        end_iso = end_date_str + "T23:59:59"

        stats = {p.id: {"start": 0, "import": 0, "export": 0} for p in self.products}

        # Quét giao dịch
        for tx in self.transactions:
            tx_date = tx.created_date
            # Tìm chi tiết giao dịch tương ứng
            tx_details = [d for d in self.transaction_details if d.transaction_id == tx.id]

            for d in tx_details:
                p_id = d.product_id
                if p_id not in stats:
                    continue
                qty = d.quantity

                if tx_date < start_iso:
                    # Mốc 1: Trước kỳ báo cáo -> tính Tồn đầu kỳ
                    if tx.type == "NHAP":
                        stats[p_id]["start"] += qty
                    elif tx.type == "XUAT":
                        stats[p_id]["start"] -= qty
                elif start_iso <= tx_date <= end_iso:
                    # Mốc 2: Trong kỳ báo cáo -> tính Tổng Nhập/Tổng Xuất
                    if tx.type == "NHAP":
                        stats[p_id]["import"] += qty
                    elif tx.type == "XUAT":
                        stats[p_id]["export"] += qty

        # Tổng hợp kết quả
        report = []
        for p in self.products:
            s_data = stats[p.id]
            ton_dau = s_data["start"]
            t_nhap = s_data["import"]
            t_xuat = s_data["export"]
            ton_cuoi = ton_dau + t_nhap - t_xuat

            report.append({
                "id": p.id,
                "name": p.name,
                "tonDau": ton_dau,
                "tongNhap": t_nhap,
                "tongXuat": t_xuat,
                "tonCuoi": ton_cuoi
            })
        return report
