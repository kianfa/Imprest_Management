from data.data_base import create_tables, insert_record, get_all_records

create_tables()

insert_record(
    Invoice_NO="Test from Python",
    explanation="This was inserted using sqlite3",
    amount=123.45,
    record_date="2026-01-01",
    image_path=None,
    source_pc="PC-1"
)

records = get_all_records()
for r in records:
    print(r)

