from app.data.data_base import insert_record

def save_data(data: dict):
    insert_record(
        title=data["title"],
        description=data["description"],
        amount=float(data["amount"]),
        record_date=data["record_date"],
        image_path=data["image_path"],
        source_pc=data["source_pc"],
        expense_center=data["expense_center"],
        expense_type=data["expense_type"],
        company_name=data["company_name"]
    )
