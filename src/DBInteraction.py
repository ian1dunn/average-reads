import psycopg2
from sshtunnel import SSHTunnelForwarder


class Connection:
    def __init__(self):
        with open("DataCredentials.txt", "r") as file:
            username = file.readline().strip()
            password = file.readline().strip()
            dbName = file.readline().strip()

        try:
            self.server = server = SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                                             ssh_username=username,
                                             ssh_password=password,
                                             remote_bind_address=('localhost', 5432))
            server.start()
            print("SSH tunnel established")
            params = {
                'database': dbName,
                'user': username,
                'password': password,
                'host': 'localhost',
                'port': server.local_bind_port
            }

            self.connection = psycopg2.connect(**params)
            print("Database connection established")
        except:
            print("Connection failed")

    def Query(self, query: str, fetch_all=True, data=None, special_return=False) -> list[tuple] | None:
        cur = self.connection.cursor()
        cur.execute(query, data)
        results = None
        if query.startswith("SELECT") or "RETURNING" in query or special_return:
            # Select is the only query which returns data (I think)
            if fetch_all:
                results = cur.fetchall()
            else:
                results = cur.fetchone()
            
            if "RETURNING" in query:
                # If we are returning data, we need to commit our changes
                self.connection.commit()
        else:
            # Made a change to the database, let's commit our changes
            self.connection.commit()
        cur.close()
        return results

    def ConnectionClose(self):
        self.server.close()
        self.connection.close()
        print("Closed")


if __name__ == '__main__':
    DATABASE = Connection()
    cursor = DATABASE.connection.cursor()
    for i in range(10):
        cursor.execute("SELECT * FROM users")
    DATABASE.ConnectionClose()


