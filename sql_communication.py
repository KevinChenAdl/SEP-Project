from pymssql import connect
from typing import Union


class MSSQLHandler:
    """
    The handler for MSSQL communication.

    Attributes:
        db_connection (Connection): The current connection to the server.
        db_cursor (Cursor): The connection's cursor.
    """

    def __init__(self):
        self.db_connection = None
        self.db_cursor = None

    def connect_to_mssql(
        self,
        arg_server: str = r'localhost',
        port: int = 1433,
    ) -> None:
        """
        Connect to an MSSQL RDBMS via a connection string.

        Args:
            arg_server (str): The server to connect to. Defaults to localhost.
            port (int): The server port to connect to. Defaults to 1433.
        """
        self.db_connection = connect(server=arg_server, port=port)
        self.db_cursor = self.db_connection.cursor()

    def send_query(self, query: str, fetch: bool = True) -> Union[list, None]:
        """
        Send a query to a MSSQL RDBMS connection and recieve the return result.

        Args:
            query (str): The T-SQL query to send.
            fetch (bool): If a return dataset should be fetched.

        Returns:
            Union[list, None]: The return dataset if fetch is true, or nothing.
        """
        self.db_cursor.execute(query)
        if fetch:
            fetched = self.db_cursor.fetchall()
            self.db_connection.commit()
            return fetched
        self.db_connection.commit()
    
    def call_procedure(self, proc_name: str, arg_list: list = None) -> list:
        """
        Call a saved procedure.

        Args:
            proc_name (str): The procedure name.
            arg_list (list): The argument list for the procedure.

        Returns:
            list: The return dataset from the procedure call.
        """
        self.db_cursor.callproc(proc_name, arg_list)
        fetched = self.db_cursor.fetchall()
        self.db_connection.commit()
        return fetched
    
    def update_column(self, table_name, change_column, change_value, condition_column, condition) -> None:
        update_query = f"""
        UPDATE {table_name}
        SET {change_column} = {change_value}
        WHERE {condition_column} = '{condition}'
        """
        self.send_query(update_query, False)
        return

    def get_column_max(self, table_name, column_name) -> None:
        update_query = f"""
        SELECT MAX({column_name})
        FROM {table_name}
        """
        return self.send_query(update_query, True)
