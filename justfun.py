import pyodbc
import os

# Database Configuration - Ensure this matches your app.py
server = r'DESKTOP-17P73P0\SQLEXPRESS'
database = 'faults_list'
conn_str = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    'Trusted_Connection=yes;'
)

def truncate_tables():
    """
    Connects to the database and clears data from specified tables.
    WARNING: This will permanently delete all data from these tables.
    For 'fault_reports', it uses DELETE FROM to handle foreign key constraints
    and then reseeds the identity column.
    """
    conn = None
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Tables to truncate in dependency order (children first)
        tables_to_truncate_children = [
            "report_photos",
            "report_materials"
        ]
        
        parent_table = "fault_reports"

        # Truncate child tables first using TRUNCATE TABLE
        for table_name in tables_to_truncate_children:
            print(f"Truncating table: {table_name}...")
            cursor.execute(f"TRUNCATE TABLE {table_name}")
            print(f"Table {table_name} truncated successfully.")

        # For the parent table, use DELETE FROM to bypass foreign key truncation issues
        print(f"Deleting all rows from table: {parent_table}...")
        cursor.execute(f"DELETE FROM {parent_table}")
        print(f"Table {parent_table} cleared successfully using DELETE FROM.")

        # Reseed the identity column for fault_reports to start from 1
        # 'RESEED, 0' means the next identity value will be 1.
        print(f"Reseeding identity for {parent_table}...")
        cursor.execute(f"DBCC CHECKIDENT ('{parent_table}', RESEED, 0);")
        print(f"Identity for {parent_table} reseeded. Next ID will be 1.")


        conn.commit()
        print("\nAll specified tables cleared and reseeded successfully!")

    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        if conn:
            conn.rollback()
        print(f"\nDatabase error occurred: {sqlstate}")
        print(f"Error details: {ex.args[1]}")
        print("Please ensure you have the necessary permissions and the tables exist.")
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == '__main__':
    truncate_tables()
