query = """select * from notes where userid = 2"""
query += "order by updated_at desc"
print(query)