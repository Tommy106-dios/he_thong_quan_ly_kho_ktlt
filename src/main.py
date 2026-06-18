import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_access.file_handler import FileHandler
from src.services.inbound_service import InboundService
from src.services.outbound_service import OutboundService
from src.services.management_service import ManagementService
from src.views.console_menu import ConsoleMenu

def main():
    # 1. Tải cơ sở dữ liệu
    file_handler = FileHandler()
    
    users = file_handler.load_users()
    categories = file_handler.load_categories()
    suppliers = file_handler.load_suppliers()
    products = file_handler.load_products()
    transactions = file_handler.load_transactions()
    transaction_details = file_handler.load_transaction_details()

    # 2. Khởi tạo các dịch vụ nghiệp vụ (Services)
    inbound_service = InboundService(
        file_handler, products, transactions, transaction_details, suppliers
    )
    outbound_service = OutboundService(
        file_handler, products, transactions, transaction_details
    )
    management_service = ManagementService(
        file_handler, products, transactions, transaction_details, categories, suppliers, users
    )

    # 3. Chạy giao diện Console Menu
    menu = ConsoleMenu(inbound_service, outbound_service, management_service, users)
    try:
        menu.run()
    except KeyboardInterrupt:
        print("\n\n⚠️ Hệ thống bị dừng bởi phím tắt. Tạm biệt!")
        sys.exit(0)

if __name__ == "__main__":
    main()
