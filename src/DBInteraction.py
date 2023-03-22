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

    def Query(self, query: str) -> list[tuple] | None:
        cur = self.connection.cursor()
        cur.execute(query)
        results = None
        if query.startswith("SELECT"):
            # Select is the only query which returns data (I think)
            results = cur.fetchall()
        else:
            # Made a change to the database, let's commit our changes
            self.connection.commit()
        cur.close()
        return results

    def ConnectionClose(self):
        self.server.close()
        self.connection.close()
