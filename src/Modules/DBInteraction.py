import psycopg2
from sshtunnel import SSHTunnelForwarder


class Connection:
    def __init__(self, DataCredFileName: str):
        with open("C:\\Users\\Alexb\\PycharmProjects\\average-reads2\\src\\Modules\\DataCredentials.txt", "r") as file:
            username = file.readline()
            password = file.readline()
            dbName = file.readline()


        try:
            with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                                    ssh_username=username,
                                    ssh_password=password,
                                    remote_bind_address=('localhost', 5432)) as server:
                server.start()
                print("SSH tunnel established")
                params = {
                    'database': dbName,
                    'user': username,
                    'password': password,
                    'host': 'localhost',
                    'port': server.local_bind_port
                }


                self.conn = psycopg2.connect(**params)
                print("Database connection established")
                
        except:
            print("Connection failed")

    def Query(self, query: str):
        cur = self.conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        return rows

    def ConnectionClose(self):
        self.conn.close()


