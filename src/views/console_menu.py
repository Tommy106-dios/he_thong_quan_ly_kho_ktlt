# -*- coding: utf-8 -*-
import sys

# Cấu hình hiển thị unicode cho terminal Windows
try:
    if sys.platform.startswith('win'):
        import ctypes
        ctypes.windll.kernel32.SetConsoleMode(ctypes.windll.kernel32.GetStdHandle(-11), 7)
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

class ConsoleMenu:
    """Giao diện điều khiển Console Menu hiển thị dạng dòng phân cách bởi |"""
    def __init__(self, inbound_service, outbound_service, management_service, users):
        self.inbound_service = inbound_service
        self.outbound_service = outbound_service
        self.management_service = management_service
        self.users = users
        self.current_user = None

    def login(self):
        """Đăng nhập hệ thống"""
        print("--- ĐĂNG NHẬP WMS ---")
        while True:
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            user = next((u for u in self.users if u.username == username and u.password == password), None)
            if user:
                self.current_user = user
                print(f"Chào {user.full_name} ({user.role})\n")
                break
            print("❌ Sai Username/Password. Thử lại.")

    def run(self):
        self.login()
        while True:
            print(f"\n--- WMS MENU | {self.current_user.full_name} ({self.current_user.role}) ---")
            print("1. Nhập kho          5. Xem lịch sử")
            print("2. Xuất kho          6. Danh mục sản phẩm")
            print("3. Cảnh báo tồn      7. Thêm danh mục mới")
            print("4. Tìm kiếm          8. Báo cáo Xuất-Nhập-Tồn")
            print("0. Thoát")
            
            choice = input("Chọn chức năng (0-8): ").strip()
            if choice == '1':
                self.menu_import_stock()
            elif choice == '2':
                self.menu_export_stock()
            elif choice == '3':
                self.menu_stock_warnings()
            elif choice == '4':
                self.menu_search_products()
            elif choice == '5':
                self.menu_transaction_history()
            elif choice == '6':
                self.menu_list_categories()
            elif choice == '7':
                self.menu_add_category()
            elif choice == '8':
                self.menu_xnt_report()
            elif choice == '0':
                print("Tạm biệt!")
                break
            else:
                input("❌ Lựa chọn sai. Nhấn Enter để chọn lại...")

    # 1. Nhập kho
    def menu_import_stock(self):
        print("\n--- NHẬP KHO ---")
        supplier_id = input("Mã nhà cung cấp: ").strip()
        
        items = []
        while True:
            p_id = input("Mã sản phẩm ProductId (Enter để dừng): ").strip()
            if not p_id:
                break
                
            exists = self.inbound_service.check_product_exists(p_id)
            item_data = {"product_id": p_id}
            
            if exists:
                try:
                    qty = int(input("Số lượng nhập: "))
                    price = float(input("Đơn giá nhập (VND): "))
                    item_data.update({"quantity": qty, "unit_price": price})
                except ValueError:
                    print("❌ Lỗi: Phải nhập số!")
                    continue
            else:
                print("📌 Sản phẩm mới! Nhập bổ sung:")
                name = input("Tên sản phẩm: ").strip()
                cat_id = input("Mã danh mục: ").strip()
                try:
                    min_stock = int(input("Mức tồn tối thiểu: "))
                    max_stock = int(input("Mức tồn tối đa: "))
                    qty = int(input("Số lượng nhập: "))
                    price = float(input("Đơn giá nhập (VND): "))
                    
                    item_data.update({
                        "name": name,
                        "category_id": cat_id,
                        "min_stock_level": min_stock,
                        "max_stock_level": max_stock,
                        "quantity": qty,
                        "unit_price": price
                    })
                except ValueError:
                    print("❌ Lỗi: Nhập sai định dạng số.")
                    continue
            items.append(item_data)
            
        if items:
            tx_id = self.inbound_service.import_stock(supplier_id, self.current_user.id, items)
            print(f"✅ Thành công! (Phiếu nhập: {tx_id})")
        else:
            print("⚠️ Không nhập mặt hàng nào.")
        input("Nhấn Enter để quay lại...")

    # 2. Xuất kho
    def menu_export_stock(self):
        print("\n--- XUẤT KHO ---")
        receiver = input("Người nhận / Ghi chú: ").strip()
        
        items = []
        while True:
            p_id = input("Mã sản phẩm ProductId (Enter để dừng): ").strip()
            if not p_id:
                break
                
            product = self.outbound_service.get_product(p_id)
            if not product:
                print("❌ Lỗi: Không tìm thấy sản phẩm!")
                continue
                
            try:
                qty = int(input("Số lượng xuất: "))
                if qty > product.stock_quantity:
                    print(f"❌ Lỗi: Kho không đủ hàng (Còn: {product.stock_quantity})!")
                    continue
                items.append({"product_id": p_id, "quantity": qty})
            except ValueError:
                print("❌ Lỗi: Phải nhập số nguyên!")
                continue
                
        if items:
            try:
                tx_id = self.outbound_service.export_stock(receiver, self.current_user.id, items)
                print(f"✅ Thành công! (Phiếu xuất: {tx_id})")
            except Exception as e:
                print(f"❌ Lỗi: {e}")
        else:
            print("⚠️ Không xuất mặt hàng nào.")
        input("Nhấn Enter để quay lại...")

    # 3. Cảnh báo tồn kho
    def menu_stock_warnings(self):
        print("\n--- CẢNH BÁO TỒN KHO ---")
        low, over = self.management_service.get_stock_warnings()
        
        if not low and not over:
            print("Tình trạng kho ổn định. Không có cảnh báo nào.")
        else:
            if low:
                print("\n⚠️ CẦN NHẬP THÊM (Tồn < Min):")
                print("Mã SP | Tên sản phẩm | Tồn kho | Mức tối thiểu")
                for p in low:
                    print(f"{p.id} | {p.name} | {p.stock_quantity} | {p.min_stock_level}")
                
            if over:
                print("\n⚠️ CẦN ĐẨY BÁN (Tồn > Max):")
                print("Mã SP | Tên sản phẩm | Tồn kho | Mức tối đa")
                for p in over:
                    print(f"{p.id} | {p.name} | {p.stock_quantity} | {p.max_stock_level}")
                
        input("Nhấn Enter để quay lại...")

    # 4. Tìm kiếm sản phẩm theo Name/ID
    def menu_search_products(self):
        print("\n--- TÌM KIẾM SẢN PHẨM ---")
        kw = input("Nhập từ khóa tìm kiếm: ").strip()
        results = self.management_service.search_products(kw)
        
        if not results:
            print("❌ Không tìm thấy sản phẩm")
        else:
            print("Mã SP | Tên sản phẩm | Danh mục | Đơn giá | Tồn kho")
            for p in results:
                print(f"{p.id} | {p.name} | {p.category_id} | {p.price:,.0f} VND | {p.stock_quantity}")
            
        input("Nhấn Enter để quay lại...")

    # 5. Xem lịch sử nhập xuất
    def menu_transaction_history(self):
        print("\n--- LỊCH SỬ GIAO DỊCH ---")
        print("1. Chỉ xem giao dịch NHẬP")
        print("2. Chỉ xem giao dịch XUẤT")
        print("3. Xem toàn bộ giao dịch")
        type_choice = input("Chọn bộ lọc (1-3): ").strip()
        
        filter_type = None
        if type_choice == '1':
            filter_type = "NHAP"
        elif type_choice == '2':
            filter_type = "XUAT"
            
        history = self.management_service.get_transaction_history(filter_type)
        
        if not history:
            print("Chưa có lịch sử giao dịch.")
        else:
            print("Mã phiếu | Loại | Thời gian | Người lập | Đối tác")
            for t in history:
                username = self.management_service.get_user_name(t.user_id)
                time_str = t.created_date.replace("T", " ")[:19]
                partner = self.management_service.get_supplier_name(t.supplier_id) if t.type == "NHAP" else (t.receiver_or_note or "-")
                print(f"{t.id} | {t.type} | {time_str} | {username} | {partner}")
            
        input("Nhấn Enter để quay lại...")

    # 6. Hiển thị danh mục sản phẩm
    def menu_list_categories(self):
        print("\n--- DANH MỤC SẢN PHẨM ---")
        cats_with_counts = self.management_service.get_categories_with_counts()
        
        if not cats_with_counts:
            print("Chưa có danh mục nào!")
        else:
            print("Mã DM | Tên danh mục | Mô tả | Số mã SP")
            for c in cats_with_counts:
                cat = c["category"]
                print(f"{cat.id} | {cat.name} | {cat.description} | {c['product_count']}")
            
        input("Nhấn Enter để quay lại...")

    # 7. Thêm 1 danh mục mặt hàng mới
    def menu_add_category(self):
        print("\n--- THÊM DANH MỤC MỚI ---")
        while True:
            cat_id = input("Mã danh mục mới (Id): ").strip()
            if not cat_id:
                print("❌ Mã không được trống!")
                continue
            name = input("Tên danh mục: ").strip()
            desc = input("Mô tả: ").strip()
            
            try:
                self.management_service.add_category(cat_id, name, desc)
                print("✅ Thêm danh mục thành công!")
                break
            except ValueError as e:
                print(f"❌ {e} Thử mã khác.")
                
        input("Nhấn Enter để quay lại...")

    # 8. Báo cáo Xuất - Nhập - Tồn
    def menu_xnt_report(self):
        print("\n--- BÁO CÁO XUẤT NHẬP TỒN ---")
        start_date = input("Ngày bắt đầu (YYYY-MM-DD): ").strip()
        end_date = input("Ngày kết thúc (YYYY-MM-DD): ").strip()
        
        try:
            report = self.management_service.calculate_xnt(start_date, end_date)
            print(f"\n📊 Báo cáo XNT từ {start_date} đến {end_date}:")
            print("Mã SP | Tên sản phẩm | Tồn đầu | Nhập | Xuất | Tồn cuối")
            for r in report:
                print(f"{r['id']} | {r['name']} | {r['tonDau']} | {r['tongNhap']} | {r['tongXuat']} | {r['tonCuoi']}")
        except Exception as e:
            print(f"❌ Lỗi: {e}. Kiểm tra định dạng ngày.")
            
        input("Nhấn Enter để quay lại...")
