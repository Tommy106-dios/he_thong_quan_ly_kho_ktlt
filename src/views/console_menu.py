import sys
try:
    if sys.platform.startswith('win'):
        import ctypes
        ctypes.windll.kernel32.SetConsoleMode(ctypes.windll.kernel32.GetStdHandle(-11), 7)
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

class ConsoleMenu:
    """Giao diện điều khiển Console Menu"""
    def __init__(self, inbound_service, outbound_service, management_service, users):
        self.inbound_service = inbound_service
        self.outbound_service = outbound_service
        self.management_service = management_service
        self.users = users
        self.current_user = None

    def login(self):
        """Đầu vào: self – Đối tượng ConsoleMenu hiện tại.
        Đầu ra: Không có giá trị trả về. Gán đối tượng User hợp lệ vào self.current_user.
        Mô tả chức năng: Hiển thị giao diện đăng nhập, yêu cầu nhập username và password.
            So khớp thông tin với danh sách users bằng next() và generator expression.
            Lặp lại cho đến khi đăng nhập thành công, in thông báo lỗi nếu sai.
        """
        print("--- ĐĂNG NHẬP WMS ---")
        while not self.current_user:
            u, p = input("Username: ").strip(), input("Password: ").strip()
            self.current_user = next((x for x in self.users if x.username == u and x.password == p), None)
            if self.current_user:
                print(f"Chào {self.current_user.full_name} ({self.current_user.role})\n")
            else:
                print("❌ Sai Username/Password. Thử lại.")

    def run(self):
        """Đầu vào: self – Đối tượng ConsoleMenu hiện tại.
        Đầu ra: Không có giá trị trả về. Chạy vòng lặp menu chính cho đến khi người dùng chọn thoát.
        Mô tả chức năng: Gọi login() để xác thực, sau đó hiển thị menu 8 chức năng trong vòng lặp
            while True. Sử dụng dictionary ánh xạ phím chọn ('1'–'8') sang phương thức xử lý
            tương ứng. Thoát khi người dùng nhập '0'.
        """
        self.login()
        actions = {
            '1': self.menu_import_stock, '2': self.menu_export_stock,
            '3': self.menu_stock_warnings, '4': self.menu_search_products,
            '5': self.menu_transaction_history, '6': self.menu_list_categories,
            '7': self.menu_add_category, '8': self.menu_xnt_report
        }
        
        menu_text = """
--- WMS MENU | {name} ({role}) ---
1. Nhập kho          5. Xem lịch sử
2. Xuất kho          6. Danh mục sản phẩm
3. Cảnh báo tồn      7. Thêm danh mục mới
4. Tìm kiếm          8. Báo cáo Xuất-Nhập-Tồn
0. Thoát"""

        while True:
            print(menu_text.format(name=self.current_user.full_name, role=self.current_user.role))
            choice = input("Chọn chức năng (0-8): ").strip()
            
            if choice == '0':
                print("Rời khỏi chương trình")
                break
            
            action = actions.get(choice)
            if action:
                action()
            else:
                input("❌ Lựa chọn sai. Nhấn Enter để chọn lại...")

    # 1. Nhập kho
    def menu_import_stock(self):
        """Đầu vào: self – Đối tượng ConsoleMenu hiện tại.
        Đầu ra: Không có giá trị trả về. In kết quả thao tác (thành công/thất bại) lên console.
        Mô tả chức năng: Giao diện nhập kho: yêu cầu mã nhà cung cấp, sau đó lặp nhập từng mặt hàng
            (mã SP, số lượng, đơn giá). Nếu sản phẩm chưa tồn tại, yêu cầu nhập thêm thông tin
            bổ sung (tên, danh mục, mức tồn min/max). Gọi InboundService.import_stock() để xử lý nghiệp vụ.
        """
        print("\n--- NHẬP KHO ---")
        supplier_id = input("Mã nhà cung cấp: ").strip()
        items = []
        
        while p_id := input("Mã sản phẩm ProductId (Enter để dừng): ").strip():
            exists = self.inbound_service.check_product_exists(p_id)
            item_data = {"product_id": p_id}
            
            try:
                if not exists:
                    print("Sản phẩm mới! Nhập bổ sung:")
                    item_data.update({
                        "name": input("Tên sản phẩm: ").strip(),
                        "category_id": input("Mã danh mục: ").strip(),
                        "min_stock_level": int(input("Mức tồn tối thiểu: ")),
                        "max_stock_level": int(input("Mức tồn tối đa: "))
                    })
                
                item_data.update({
                    "quantity": int(input("Số lượng nhập: ")),
                    "unit_price": float(input("Đơn giá nhập (VND): "))
                })
                items.append(item_data)
            except ValueError:
                print("❌ Lỗi: Nhập sai định dạng số.")
                
        if items:
            tx_id = self.inbound_service.import_stock(supplier_id, self.current_user.id, items)
            print(f"✅ Thành công! (Phiếu nhập: {tx_id})")
        else:
            print("Không nhập mặt hàng nào.")
        input("Nhấn Enter để quay lại...")

    # 2. Xuất kho
    def menu_export_stock(self):
        """Đầu vào: self – Đối tượng ConsoleMenu hiện tại.
        Đầu ra: Không có giá trị trả về. In kết quả thao tác lên console.
        Mô tả chức năng: Giao diện xuất kho: yêu cầu thông tin người nhận, sau đó lặp nhập từng mặt hàng.
            Kiểm tra sản phẩm tồn tại và đủ tồn kho trước khi thêm vào danh sách.
            Gọi OutboundService.export_stock() để xử lý, bắt lỗi ValueError nếu không đủ hàng.
        """
        print("\n--- XUẤT KHO ---")
        receiver = input("Người nhận / Ghi chú: ").strip()
        items = []
        
        while p_id := input("Mã sản phẩm ProductId (Enter để dừng): ").strip():
            product = self.outbound_service.get_product(p_id)
            if not product:
                print("❌ Lỗi: Không tìm thấy sản phẩm!"); continue
                
            try:
                qty = int(input("Số lượng xuất: "))
                if qty > product.stock_quantity:
                    print(f"❌ Lỗi: Kho không đủ hàng (Còn: {product.stock_quantity})!"); continue
                items.append({"product_id": p_id, "quantity": qty})
            except ValueError:
                print("❌ Lỗi: Phải nhập số nguyên!")
                
        if items:
            try:
                tx_id = self.outbound_service.export_stock(receiver, self.current_user.id, items)
                print(f"✅ Thành công! (Phiếu xuất: {tx_id})")
            except Exception as e:
                print(f"❌ Lỗi: {e}")
        else:
            print("Không xuất mặt hàng nào.")
        input("Nhấn Enter để quay lại...")

    # 3. Cảnh báo tồn kho
    def menu_stock_warnings(self):
        print("\n--- CẢNH BÁO TỒN KHO ---")
        low, over = self.management_service.get_stock_warnings()
        
        if not low and not over:
            print("Tình trạng kho ổn định. Không có cảnh báo nào.")
        if low:
            print("\nCẦN NHẬP THÊM (Tồn < Min):\nMã SP | Tên sản phẩm | Tồn kho | Mức tối thiểu")
            for p in low: print(f"{p.id} | {p.name} | {p.stock_quantity} | {p.min_stock_level}")
        if over:
            print("\nCẦN ĐẨY BÁN (Tồn > Max):\nMã SP | Tên sản phẩm | Tồn kho | Mức tối đa")
            for p in over: print(f"{p.id} | {p.name} | {p.stock_quantity} | {p.max_stock_level}")
        input("Nhấn Enter để quay lại...")

    # 4. Tìm kiếm sản phẩm
    def menu_search_products(self):
        print("\n--- TÌM KIẾM SẢN PHẨM ---")
        results = self.management_service.search_products(input("Nhập từ khóa: ").strip())
        if results:
            print("Mã SP | Tên sản phẩm | Danh mục | Đơn giá | Tồn kho")
            for p in results: print(f"{p.id} | {p.name} | {p.category_id} | {p.price:,.0f} VND | {p.stock_quantity}")
        else:
            print("❌ Không tìm thấy sản phẩm")
        input("Nhấn Enter để quay lại...")

    # 5. Xem lịch sử
    def menu_transaction_history(self):
        print("\n--- LỊCH SỬ GIAO DỊCH ---\n1. Chỉ xem NHẬP\n2. Chỉ xem XUẤT\n3. Xem toàn bộ")
        filters = {'1': "NHAP", '2': "XUAT"}
        history = self.management_service.get_transaction_history(filters.get(input("Chọn bộ lọc (1-3): ").strip()))
        
        if history:
            print("Mã phiếu | Loại | Thời gian | Người lập | Đối tác")
            for t in history:
                username = self.management_service.get_user_name(t.user_id)
                partner = self.management_service.get_supplier_name(t.supplier_id) if t.type == "NHAP" else (t.receiver_or_note or "-")
                print(f"{t.id} | {t.type} | {t.created_date.replace('T', ' ')[:19]} | {username} | {partner}")
        else:
            print("Chưa có lịch sử giao dịch.")
        input("Nhấn Enter để quay lại...")

    # 6. Danh mục sản phẩm
    def menu_list_categories(self):
        print("\n--- DANH MỤC SẢN PHẨM ---")
        cats = self.management_service.get_categories_with_counts()
        if cats:
            print("Mã DM | Tên danh mục | Mô tả | Số mã SP")
            for c in cats: print(f"{c['category'].id} | {c['category'].name} | {c['category'].description} | {c['product_count']}")
        else:
            print("Chưa có danh mục nào!")
        input("Nhấn Enter để quay lại...")

    # 7. Thêm danh mục
    def menu_add_category(self):
        print("\n--- THÊM DANH MỤC MỚI ---")
        while cat_id := input("Mã danh mục mới (Id): ").strip():
            try:
                self.management_service.add_category(cat_id, input("Tên danh mục: ").strip(), input("Mô tả: ").strip())
                print("✅ Thêm danh mục thành công!"); break
            except ValueError as e:
                print(f"❌ {e} Thử mã khác.")
        if not cat_id: print("❌ Mã không được trống!")
        input("Nhấn Enter để quay lại...")

    # 8. Báo cáo XNT
    def menu_xnt_report(self):
        """Đầu vào: self – Đối tượng ConsoleMenu hiện tại.
        Đầu ra: Không có giá trị trả về. In bảng báo cáo Xuất–Nhập–Tồn lên console.
        Mô tả chức năng: Giao diện báo cáo XNT: yêu cầu nhập ngày bắt đầu và kết thúc
            (định dạng YYYY-MM-DD), gọi ManagementService.calculate_xnt() để tính toán,
            sau đó hiển thị kết quả dạng bảng gồm: Mã SP, Tên, Tồn đầu, Nhập, Xuất, Tồn cuối.
            Bắt lỗi ngoại lệ nếu định dạng ngày không hợp lệ.
        """
        print("\n--- BÁO CÁO XUẤT NHẬP TỒN ---")
        start, end = input("Ngày bắt đầu (YYYY-MM-DD): ").strip(), input("Ngày kết thúc (YYYY-MM-DD): ").strip()
        try:
            report = self.management_service.calculate_xnt(start, end)
            print(f"\n Báo cáo XNT từ {start} đến {end}:\nMã SP | Tên sản phẩm | Tồn đầu | Nhập | Xuất | Tồn cuối")
            for r in report: print(f"{r['id']} | {r['name']} | {r['tonDau']} | {r['tongNhap']} | {r['tongXuat']} | {r['tonCuoi']}")
        except Exception as e:
            print(f"❌ Lỗi: {e}. Kiểm tra định dạng ngày.")
        input("Nhấn Enter để quay lại...")