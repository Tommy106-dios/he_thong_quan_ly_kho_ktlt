# -*- coding: utf-8 -*-
"""
Kịch bản kiểm thử tự động bám sát đặc tả mới của tài liệu Hệ thống quản lý kho hàng.docx.
"""

import sys
import os
import shutil

# Thêm thư mục gốc vào đường dẫn hệ thống để import các package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import User, Category, Supplier, Product, Transaction, TransactionDetail
from src.data_access.file_handler import FileHandler
from src.services.inbound_service import InboundService
from src.services.outbound_service import OutboundService
from src.services.management_service import ManagementService

sys.stdout.reconfigure(encoding='utf-8')

print("==========================================================")
print("   BẮT ĐẦU KIỂM THỬ WMS TINH GỌN (BÁM SÁT 100% ĐẶC TẢ)    ")
print("==========================================================\n")

# Tạo thư mục test dữ liệu tạm
TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_db")
if os.path.exists(TEST_DATA_DIR):
    shutil.rmtree(TEST_DATA_DIR)
os.makedirs(TEST_DATA_DIR)

# Khởi tạo mock data
mock_users = [
    {"id": "US001", "username": "admin", "password": "123", "fullName": "Nguyễn Văn A", "role": "Admin"},
    {"id": "US002", "username": "kho", "password": "123", "fullName": "Lê Văn B", "role": "NhanVienKho"}
]

mock_categories = [
    {"id": "CAT01", "name": "Vật liệu", "description": "Thép, xi măng, gạch"}
]

mock_suppliers = [
    {"id": "SUP01", "name": "Công ty Thép Hòa Phát", "phone": "090", "address": "Hà Nội"}
]

mock_products = [
    {"id": "SP001", "name": "Thép Hòa Phát D10", "categoryId": "CAT01", "price": 15000.0, "stockQuantity": 100, "minStockLevel": 50, "maxStockLevel": 500},
    {"id": "SP002", "name": "Xi măng Vicem Hà Tiên", "categoryId": "CAT01", "price": 80000.0, "stockQuantity": 20, "minStockLevel": 40, "maxStockLevel": 300}
]

mock_transactions = [
    {"id": "TX001", "type": "NHAP", "createdDate": "2026-06-05T08:30:00Z", "userId": "US002", "supplierId": "SUP01"}
]

mock_transaction_details = [
    {"transactionId": "TX001", "productId": "SP001", "quantity": 100, "unitPrice": 15000.0}
]

file_handler = FileHandler(data_dir=TEST_DATA_DIR)
file_handler._write_file("users.json", mock_users)
file_handler._write_file("categories.json", mock_categories)
file_handler._write_file("suppliers.json", mock_suppliers)
file_handler._write_file("products.json", mock_products)
file_handler._write_file("transactions.json", mock_transactions)
file_handler._write_file("transaction_details.json", mock_transaction_details)

# Load dữ liệu dạng OOP
users = file_handler.load_users()
categories = file_handler.load_categories()
suppliers = file_handler.load_suppliers()
products = file_handler.load_products()
transactions = file_handler.load_transactions()
transaction_details = file_handler.load_transaction_details()

# Tạo các Services
inbound_service = InboundService(file_handler, products, transactions, transaction_details, suppliers)
outbound_service = OutboundService(file_handler, products, transactions, transaction_details)
management_service = ManagementService(file_handler, products, transactions, transaction_details, categories, suppliers, users)

tests_run = 0
tests_passed = 0

def run_assert(condition, message):
    global tests_run, tests_passed
    tests_run += 1
    if condition:
        tests_passed += 1
        print(f"✅ [ĐẠT] {message}")
    else:
        print(f"❌ [HỎNG] {message}")

# --- 1. THÊM DANH MỤC MỚI ---
def test_add_category():
    print("--- Test Case 1: Thêm danh mục mới ---")
    new_cat = management_service.add_category("CAT02", "Hóa chất", "Sơn Dulux")
    run_assert(new_cat.id == "CAT02", "Mã danh mục CAT02 được thiết lập đúng")
    
    # Kiểm tra trùng lặp
    try:
        management_service.add_category("CAT02", "Trùng", "Lỗi")
        run_assert(False, "Chấp nhận trùng mã danh mục (Lỗi logic)")
    except ValueError:
        run_assert(True, "Ngăn chặn thành công thêm danh mục trùng mã ID")

# --- 2. NHẬP KHO (SẢN PHẨM CŨ & SẢN PHẨM MỚI TOANH) ---
def test_import_stock():
    print("\n--- Test Case 2: Nghiệp vụ Nhập kho ---")
    # A. Nhập sản phẩm cũ (SP001)
    sp001 = next((p for p in products if p.id == "SP001"), None)
    old_stock = sp001.stock_quantity
    
    items = [
        {"product_id": "SP001", "quantity": 50, "unit_price": 16000.0}, # Nhập SP cũ, có thay đổi giá
        {"product_id": "SP003", "quantity": 10, "unit_price": 120000.0, "name": "Ống nhựa D90", "category_id": "CAT01", "min_stock_level": 5, "max_stock_level": 50} # Nhập SP mới toanh
    ]
    
    tx_id = inbound_service.import_stock("SUP01", "US002", items)
    run_assert(tx_id == "PN1001", f"Tự động sinh mã phiếu nhập PN1001 chính xác (mã PN tự tăng đầu tiên)")
    
    # Kiểm tra sản phẩm cũ SP001
    run_assert(sp001.stock_quantity == old_stock + 50, f"Cộng dồn số lượng SP001 thành công: {sp001.stock_quantity}")
    run_assert(sp001.price == 16000.0, f"Cập nhật lại giá niêm yết của SP001 thành công: {sp001.price}")
    
    # Kiểm tra sản phẩm mới SP003
    sp003 = next((p for p in products if p.id == "SP003"), None)
    run_assert(sp003 is not None, "Sản phẩm mới SP003 được tự động thêm vào danh mục sản phẩm hệ thống")
    run_assert(sp003.stock_quantity == 10, f"Thiết lập số lượng nhập cho sản phẩm mới chính xác: {sp003.stock_quantity}")

# --- 3. XUẤT KHO & RÀNG BUỘC SỐ LƯỢNG ---
def test_export_stock():
    print("\n--- Test Case 3: Nghiệp vụ Xuất kho ---")
    sp001 = next((p for p in products if p.id == "SP001"), None)
    old_stock = sp001.stock_quantity # 150
    
    # A. Xuất kho hợp lệ
    items = [{"product_id": "SP001", "quantity": 30}]
    tx_id = outbound_service.export_stock("Công trình Landmark", "US002", items)
    run_assert(tx_id == "PX1001", f"Tự động sinh mã phiếu xuất PX1001 chính xác: {tx_id}")
    run_assert(sp001.stock_quantity == old_stock - 30, f"Trừ số lượng tồn kho của SP001 chính xác: {sp001.stock_quantity}")
    
    # B. Kiểm tra lưu đơn giá xuất tự động lấy theo giá hiện tại
    detail = next((d for d in transaction_details if d.transaction_id == "PX1001" and d.product_id == "SP001"), None)
    run_assert(detail.unit_price == sp001.price, f"Tự động lấy đơn giá xuất theo giá bán hiện tại: {detail.unit_price} VND")

    # C. Kiểm tra xuất quá tồn kho
    try:
        outbound_service.export_stock("Test quá hạn", "US002", [{"product_id": "SP001", "quantity": 500}])
        run_assert(False, "Chấp nhận xuất kho vượt quá số lượng tồn kho (Lỗi logic)")
    except ValueError:
        run_assert(True, "Ngăn chặn thành công xuất kho vượt định mức tồn kho hiện tại")

# --- 4. CẢNH BÁO TỒN KHO ---
def test_warnings():
    print("\n--- Test Case 4: Cảnh báo tồn kho ---")
    # SP002 tồn kho 20, min_stock_level 40 -> Thiếu hụt (Cần nhập thêm)
    # SP001 tồn kho 120 (100 + 50 - 30), max_stock_level 500 -> Không dư thừa
    low, over = management_service.get_stock_warnings()
    
    has_sp002_low = any(p.id == "SP002" for p in low)
    has_sp001_over = any(p.id == "SP001" for p in over)
    
    run_assert(has_sp002_low, "SP002 được đưa vào DanhSachSapHet chính xác")
    run_assert(not has_sp001_over, "SP001 không bị đưa vào DanhSachTonDu")

# --- 5. TÌM KIẾM SẢN PHẨM THEO NAME/ID ---
def test_search():
    print("\n--- Test Case 5: Tìm kiếm sản phẩm (Không phân biệt hoa thường, cắt khoảng trắng) ---")
    results = management_service.search_products("  sp001  ")
    run_assert(len(results) == 1 and results[0].id == "SP001", "Tìm kiếm theo ID thành công")
    
    results2 = management_service.search_products("Thép")
    run_assert(len(results2) == 1 and results2[0].id == "SP001", "Tìm kiếm theo chuỗi con của Tên thành công")

# --- 6. BÁO CÁO XUẤT NHẬP TỒN (XNT) LỊCH SỬ ---
def test_xnt_report():
    print("\n--- Test Case 6: Thuật toán báo cáo XNT phân rã thời gian ---")
    # Reset lại dữ liệu phục vụ test XNT chuẩn xác
    # SP001: Tồn đầu kỳ gốc là 100.
    # Trong kỳ (5/6 -> 7/6):
    #  - TX001 (5/6): Nhập 100 (unitPrice: 15000)
    #  - PX1001 (6/6): Xuất 30 (unitPrice: 16000)
    # Tồn cuối kỳ dự kiến = 100 + 100 - 30 = 170.
    # PN1001 (ngày 11/6 - sau kỳ báo cáo): Nhập 50 -> Bị bỏ qua.
    
    # Chỉnh lại ngày tạo các phiếu giao dịch để kiểm tra thuật toán phân rã thời gian
    t_tx001 = next((t for t in transactions if t.id == "TX001"), None)
    t_tx001.created_date = "2026-06-05T08:30:00Z"
    
    t_pn1001 = next((t for t in transactions if t.id == "PN1001"), None)
    t_pn1001.created_date = "2026-06-11T09:00:00Z"
    
    t_px1001 = next((t for t in transactions if t.id == "PX1001"), None)
    t_px1001.created_date = "2026-06-06T10:15:00Z"

    # Kỳ báo cáo từ 5/6 đến 7/6
    report = management_service.calculate_xnt("2026-06-05", "2026-06-07")
    
    r_sp001 = next((r for r in report if r["id"] == "SP001"), None)
    run_assert(r_sp001 is not None, "Đọc số liệu sản phẩm SP001 thành công")
    run_assert(r_sp001["tonDau"] == 0, f"Tồn đầu ngày 5/6: {r_sp001['tonDau']} (kỳ vọng: 0)")
    run_assert(r_sp001["tongNhap"] == 100, f"Tổng nhập trong kỳ: {r_sp001['tongNhap']} (kỳ vọng: 100)")
    run_assert(r_sp001["tongXuat"] == 30, f"Tổng xuất trong kỳ: {r_sp001['tongXuat']} (kỳ vọng: 30)")
    run_assert(r_sp001["tonCuoi"] == 70, f"Tồn cuối ngày 7/6: {r_sp001['tonCuoi']} (kỳ vọng: 70)")

# Thực thi tất cả các test case
test_add_category()
test_import_stock()
test_export_stock()
test_warnings()
test_search()
test_xnt_report()

# Dọn dẹp thư mục test
shutil.rmtree(TEST_DATA_DIR)

print("\n==========================================================")
print(f" KẾT QUẢ KIỂM THỬ: Đã vượt qua {tests_passed}/{tests_run} bài kiểm tra.")
print("==========================================================")
if tests_passed == tests_run:
    print("🎉 LOGIC NGHIỆP VỤ BÁM SÁT 100% ĐẶC TẢ HỒ SƠ ĐÃ HOÀN TOÀN CHÍNH XÁC!")
    sys.exit(0)
else:
    print("⚠️ THẤT BẠI: Một số bài kiểm thử không đạt kết quả mong muốn.")
    sys.exit(1)
