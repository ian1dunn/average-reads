

def select_from_table(table_name: str, attributes: str, condition: str = None):
    query = f"SELECT ({attributes}) FROM {table_name}" + (" " + condition if condition else "")