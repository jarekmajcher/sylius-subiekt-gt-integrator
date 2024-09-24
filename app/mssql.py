import pyodbc
from app.config import AppConfig

class MSSQL:
    def __init__(self):
        self.config = AppConfig()
        self.connection = self._connect()

    def _connect(self):
        conn_str = f'DRIVER=ODBC Driver 17 for SQL Server;SERVER={self.config.MSSQL_SERVER};DATABASE={self.config.MSSQL_DB};UID={self.config.MSSQL_USER};PWD={self.config.MSSQL_PASS}'
        return pyodbc.connect(conn_str)

    def fetch_data(self, query):

        # Connect and get rows
        cursor = self.connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        # Convert to associative
        data = []
        for row in rows:
            row_dict = {}
            for idx, col in enumerate(cursor.description):
                row_dict[col[0]] = row[idx]
            data.append(row_dict)

        # Close connection
        cursor.close()

        # Return
        return data