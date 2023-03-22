
import psycopg2
from sshtunnel import SSHTunnelForwarder


class Connection:
    def __init__(self):
        with open("DataCredentials.txt", "r") as file:
            self.__username = file.readline()[:-1]
            self.__password = file.readline()[:-1]
            self.__dbName = file.readline()

        

    def Query(self, Query: str):

        try:
            with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                                    ssh_username=self.__username,
                                    ssh_password=self.__password,
                                    remote_bind_address=('localhost', 5432)) as server:
                server.start()
                print("SSH tunnel established")
                params = {
                    'database': self.__dbName,
                    'user': self.__username,
                    'password': self.__password,
                    'host': 'localhost',
                    'port': server.local_bind_port
                }


                conn = psycopg2.connect(**params)
                print("Database connection established")
                curr = conn.cursor()
                curr.execute(Query)
                rows = curr.fetchall()
                curr.close()
                conn.close()
                return rows
        except:
            print("Connection failed")   

# class Connection:
#     def __init__(self):
#         with open("DataCredentials.txt", "r") as file:
#             username = file.readline()[:-1]
#             password = file.readline()[:-1]
#             dbName = file.readline()
#         try:
#             with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
#                                     ssh_username=username,
#                                     ssh_password=password,
#                                     remote_bind_address=('localhost', 5432)) as server:
#                 server.start()
#                 print("SSH tunnel established")
#                 params = {
#                     'database': dbName,
#                     'user': username,
#                     'password': password,
#                     'host': 'localhost',
#                     'port': server.local_bind_port
#                 }
#                 self.conn = psycopg2.connect(**params)
#                 print("Database connection established")
                
#         except:
#             print("Connection failed")   
            

#     def Query(self, Query: str):
#         curr = self.conn.cursor()
#         curr.execute(Query)
#         rows = curr.fetchall
#         curr.close
#         return rows

#     def ConnClose(self):
#         self.conn.close

