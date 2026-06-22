# 📦 Hệ thống Quản lý Kho hàng WMS (Python Layered Architecture)

[![Language](https://img.shields.io/badge/Language-Python%203-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-JSON%20Files-orange.svg)](https://www.json.org/)
[![Architecture](https://img.shields.io/badge/Architecture-4--Layer-green.svg)](#-kiến-trúc-phân-lớp-layered-architecture)

Ứng dụng quản lý kho hàng (WMS - Warehouse Management System) dòng lệnh (Console UI) viết bằng ngôn ngữ **Python** theo kiến trúc phân lớp hướng đối tượng (OOP). Dự án này bám sát 100% các yêu cầu nghiệp vụ, thực thể dữ liệu và thuộc tính được đặc tả trong tài liệu môn học Kỹ thuật Lập trình.

---

## 🌟 Tính năng chính của Hệ thống

1. **Đăng nhập hệ thống (Authentication)**: Xác thực nhân viên đăng nhập dựa trên danh sách tài khoản được quản lý trong cơ sở dữ liệu để phục vụ việc ghi dấu vết người dùng lập phiếu.
2. **Nghiệp vụ Nhập kho (Inbound)**: 
   - Nhập hàng theo Nhà cung cấp (`supplierId`).
   - Tự động cộng dồn số lượng đối với sản phẩm đã có và cập nhật giá bán hiện thời.
   - Hỗ trợ thêm mới sản phẩm mới ngay trong luồng nhập kho nếu phát hiện sản phẩm chưa tồn tại.
   - Tự động sinh mã phiếu nhập `PNxxxx` tăng dần và lưu giữ chi tiết dòng giao dịch lịch sử.
3. **Nghiệp vụ Xuất kho (Outbound)**:
   - Xuất hàng ghi nhận người nhận hoặc lý do (`receiverOrNote`).
   - Đối chiếu số lượng xuất với tồn kho thực tế, ngăn chặn xuất kho quá định mức (ném lỗi cảnh báo).
   - Tự động sinh mã phiếu xuất `PXxxxx` tăng dần, áp đơn giá xuất theo giá niêm yết hiện thời.
4. **Cảnh báo tồn kho định mức (Alerts)**:
   - Quét danh sách sản phẩm và tự động đưa ra cảnh báo khi tồn kho tụt dưới ngưỡng tối thiểu (`minStockLevel`) hoặc vượt ngưỡng tồn tối đa (`maxStockLevel`).
5. **Tìm kiếm sản phẩm linh hoạt**:
   - Tìm kiếm sản phẩm theo Mã sản phẩm hoặc Tên sản phẩm không phân biệt chữ hoa, chữ thường và tự động chuẩn hóa khoảng trắng đầu cuối (`strip()`).
6. **Xem lịch sử giao dịch**:
   - Cho phép lọc xem toàn bộ giao dịch, hoặc chỉ xem giao dịch `NHẬP`, `XUẤT`.
   - Sắp xếp giao dịch theo thời gian giảm dần (giao dịch mới nhất hiển thị lên đầu).
7. **Báo cáo Xuất - Nhập - Tồn (XNT) lịch sử**:
   - Cho phép người dùng nhập khoảng thời gian (Ngày bắt đầu - Ngày kết thúc).
   - Áp dụng thuật toán phân rã thời gian: Tính toán chính xác tồn kho đầu kỳ (trước ngày bắt đầu), lượng nhập/xuất trong kỳ, và tồn kho cuối kỳ của toàn bộ sản phẩm.
8. **Hiển thị & Quản lý Danh mục**:
   - Thống kê danh sách danh mục kèm số lượng mã sản phẩm đang thuộc danh mục đó.
   - Thêm mới danh mục hàng hóa và kiểm tra trùng mã ID danh mục để ngăn chặn trùng lặp khóa chính.

---

## 📁 Cấu trúc Thư mục Dự án

```text
warehouse_management/
│
├── docs/
│   ├── Hệ thống quản lý kho hàng.docx    # Nơi lưu tài liệu tham chiếu gốc của dự án
│   └── Báo cáo Hệ thống WMS.docx         # Báo cáo BTL Kỹ thuật Lập trình (Python)
│
├── src/
│   │
│   ├── models/                           # Chứa định nghĩa các lớp (class) thực thể
│   │   ├── __init__.py
│   │   ├── user.py                       # Thực thể User
│   │   ├── category.py                   # Thực thể Danh mục (Mới bổ sung)
│   │   ├── supplier.py                   # Thực thể Nhà cung cấp
│   │   ├── product.py                    # Thực thể Sản phẩm
│   │   ├── warehouse.py                  # Thực thể Kho
│   │   ├── transaction.py                # Thực thể Giao dịch (Đã tích hợp trường Ghi chú/Người nhận)
│   │   └── transaction_detail.py         # Thực thể Chi tiết giao dịch (Mới bổ sung)
│   │
│   ├── services/                         # Chứa logic xử lý 3 NGHIỆP VỤ CHÍNH
│   │   ├── __init__.py
│   │   ├── inbound_service.py            # Chức năng NHẬP KHO: Thêm hàng, lưu lịch sử...
│   │   ├── management_service.py         # Chức năng QUẢN LÝ: Cảnh báo, tìm kiếm, báo cáo...
│   │   └── outbound_service.py           # Chức năng XUẤT KHO: Xuất hàng, lưu lịch sử...
│   │
│   ├── views/                            # Chuyên xử lý đầu vào/đầu ra trên màn hình Console
│   │   ├── __init__.py
│   │   ├── console_menu.py               # Hiển thị các danh mục menu (1. Nhập kho, 2. Xuất kho...)
│   │   └── printer_util.py               # Tiện ích kẻ bảng in danh sách sản phẩm, in phiếu nhập/xuất
│   │
│   ├── data_access/                      # (Tùy chọn) Tách riêng phần đọc/ghi dữ liệu
│   │   ├── __init__.py
│   │   └── file_handler.py               # Xử lý lưu các danh sách đối tượng (List/Array) xuống file
│   │
│   └── main.py                           # File gốc chứa vòng lặp vô hạn (while True) khởi chạy ứng dụng
│   
├── data/                                 # Thư mục chứa các file cơ sở dữ liệu vật lý (nếu lưu file)
│   ├── products.json
│   └── transactions.json
│
├── .gitignore                            # Cấu hình bỏ qua tệp tin rác của Git
└── README.md                             # Tài liệu hướng dẫn này
```

---

## 🛠️ Hướng dẫn Khởi chạy & Sử dụng

### 1. Yêu cầu hệ thống
- Máy tính đã cài đặt **Python 3.8** trở lên.

### 2. Khởi chạy ứng dụng
Mở terminal/cmd tại thư mục gốc của dự án `warehouse_management/` và chạy lệnh sau:
```bash
python src/main.py
```

### 3. Tài khoản Đăng nhập Hệ thống
Khi khởi chạy, hệ thống sẽ yêu cầu tài khoản để đăng nhập:
* **Tài khoản Thủ kho**: Username `kho` / Password `123`
* **Tài khoản Quản lý**: Username `admin` / Password `123`

---

## 🧪 Kịch bản Kiểm thử Tự động (Testing)

Dự án tích hợp kịch bản kiểm thử tự động toàn diện giúp kiểm chứng độ chính xác 100% của toàn bộ 20/20 luồng nghiệp vụ (tạo mã phiếu tự tăng, cộng dồn nhập kho, trừ kho an toàn, chặn xuất vượt tồn, lọc phân loại cảnh báo, tìm kiếm chuẩn hóa chuỗi và báo cáo lùi lịch sử XNT).

Để chạy kiểm thử tự động, sử dụng lệnh:
```bash
python tests/verify_refactored_logic.py
```

