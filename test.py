import os
import struct
from datetime import datetime

# กำหนดโครงสร้างข้อมูล (date, income_item, income_amount, expense_item, expense_amount)
DATA_FORMAT = '10s 30s i 30s i'

def add_income(file_path, date, income_item, income_amount):
    if not date or not income_item or income_amount is None:
        print("กรุณากรอกข้อมูลให้ครบถ้วน (วันที่, รายการรายรับ, จำนวนเงิน)")
        return

    record = (date.encode('utf-8'), income_item.encode('utf-8'), income_amount, b'', 0)
    with open(file_path, 'ab') as f:
        f.write(struct.pack(DATA_FORMAT, *record))

    print("เพิ่มข้อมูลรายรับเรียบร้อยแล้ว")

def add_expense(file_path, date, expense_item, expense_amount):
    if not date or not expense_item or expense_amount is None:
        print("กรุณากรอกข้อมูลให้ครบถ้วน (วันที่, รายการรายจ่าย, จำนวนเงิน)")
        return

    record = (date.encode('utf-8'), b'', 0, expense_item.encode('utf-8'), expense_amount)
    with open(file_path, 'ab') as f:
        f.write(struct.pack(DATA_FORMAT, *record))

    print("เพิ่มข้อมูลรายจ่ายเรียบร้อยแล้ว")

def show_records(file_path):
    if not os.path.exists(file_path):
        print("ไม่มีข้อมูลในไฟล์")
        return

    # ปรับความยาวของคอลัมน์
    print(f"{'Date':<12}{'Income Item':<32}{'Income Amount':<20}{'Expense Item':<32}{'Expense Amount':<20}")
    print("-" * 140)

    with open(file_path, 'rb') as f:
        while True:
            data = f.read(struct.calcsize(DATA_FORMAT))
            if not data:
                break
            unpacked_data = struct.unpack(DATA_FORMAT, data)
            date, income_item, income_amount, expense_item, expense_amount = unpacked_data
            print(f"{date.decode('utf-8').rstrip('\x00'):<12}"  # ปรับช่องว่างให้วันที่
                  f"{income_item.decode('utf-8').rstrip('\x00'):<32}"  # ปรับความกว้างของรายการรายรับ
                  f"{income_amount:<20}"
                  f"{expense_item.decode('utf-8').rstrip('\x00'):<32}"  # ปรับความกว้างของรายการรายจ่าย
                  f"{expense_amount:<20}")


def generate_report(file_path):
    if not os.path.exists(file_path):
        print("ไม่มีข้อมูลในไฟล์")
        return

    total_income = 0
    total_expense = 0
    records = []

    with open(file_path, 'rb') as f:
        while True:
            data = f.read(struct.calcsize(DATA_FORMAT))
            if not data:
                break
            unpacked_data = struct.unpack(DATA_FORMAT, data)
            date, income_item, income_amount, expense_item, expense_amount = unpacked_data
            records.append((date.decode('utf-8').rstrip('\x00'), 
                            income_item.decode('utf-8').rstrip('\x00'), 
                            income_amount, 
                            expense_item.decode('utf-8').rstrip('\x00'), 
                            expense_amount))
            total_income += income_amount
            total_expense += expense_amount

    ending_balance = total_income - total_expense

    with open('financial_report.txt', 'w', encoding='utf-8') as report_file:
        report_file.write(f"{'Date':<12}{'Income Item':<32}{'Income Amount':<20}{'Expense Item':<32}{'Expense Amount':<20}\n")
        report_file.write("-" * 140 + "\n")

        last_date = None
        for record in records:
            date, income_item, income_amount, expense_item, expense_amount = record
            
            if last_date != date:
                if last_date is not None:
                    report_file.write("\n")
                last_date = date
            
            report_file.write(f"{date:<12}  {income_item:<32}  {income_amount:<20}  {expense_item:<32}  {expense_amount:<20}\n")
        
        report_file.write(f"{'Total Income:':<70}{total_income}\n")
        report_file.write(f"{'Total Expense:':<70}{total_expense}\n")
        report_file.write(f"{'Ending Balance:':<70}{ending_balance}\n")
        report_file.write(f"\nMonth: {datetime.now().strftime('%B %Y')}\n")

    print("รายงานถูกสร้างเรียบร้อยแล้วในไฟล์ 'financial_report.txt'")






def delete_record_by_item(file_path):
    if not os.path.exists(file_path):
        print("ไม่มีข้อมูลในไฟล์")
        return

    item_to_delete = input("ป้อนรายการที่ต้องการลบ: ")

    new_records = []
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(struct.calcsize(DATA_FORMAT))
            if not data:
                break
            unpacked_data = struct.unpack(DATA_FORMAT, data)

            # เก็บเฉพาะข้อมูลที่ไม่ใช่รายการที่ต้องการลบ
            if unpacked_data[1].decode('utf-8').strip() != item_to_delete and unpacked_data[3].decode('utf-8').strip() != item_to_delete:
                new_records.append(unpacked_data)

    # เขียนข้อมูลใหม่ไปยังไฟล์
    with open(file_path, 'wb') as f:
        for record in new_records:
            f.write(struct.pack(DATA_FORMAT, *record))

    print(f"ลบข้อมูลรายการ '{item_to_delete}' เรียบร้อยแล้ว")

def main():
    file_path = 'financial_records.bin'
    
    while True:
        print("\nเมนู:")
        print("1. เพิ่มข้อมูลรายรับ")
        print("2. เพิ่มข้อมูลรายจ่าย")
        print("3. แสดงข้อมูลทั้งหมด")
        print("4. สร้างรายงาน")
        print("5. ลบข้อมูลตามรายการ")
        print("6. ออกโปรแกรม")
        choice = input("เลือกตัวเลือก (1-6): ")

        if choice == '1':
            date = input("ป้อนวันที่ (dd/mm/yyyy): ")
            income_item = input("ป้อนรายการรายรับ: ")
            income_amount = int(input("ป้อนจำนวนเงินรายรับ: "))
            add_income(file_path, date, income_item, income_amount)

        elif choice == '2':
            date = input("ป้อนวันที่ (dd/mm/yyyy): ")
            expense_item = input("ป้อนรายการรายจ่าย: ")
            expense_amount = int(input("ป้อนจำนวนเงินรายจ่าย: "))
            add_expense(file_path, date, expense_item, expense_amount)

        elif choice == '3':
            show_records(file_path)

        elif choice == '4':
            generate_report(file_path)

        elif choice == '5':
            delete_record_by_item(file_path)

        elif choice == '6':
            print("ออกจากโปรแกรม")
            break

        else:
            print("ตัวเลือกไม่ถูกต้อง กรุณาลองอีกครั้ง")

if __name__ == "__main__":
    main()
