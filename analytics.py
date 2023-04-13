import psycopg2
from sshtunnel import SSHTunnelForwarder
import csv

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

    def FetchData(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM rating")

        return cursor.fetchall()

    def ConnectionClose(self):
        self.server.close()
        self.connection.close()
        print("Closed")


if __name__ == '__main__':
    RAW_DATA_FILENAME = "raw_ratings_data.csv"

    DATABASE = Connection()
    rows = DATABASE.FetchData() # Returns array of tuples

    with open(RAW_DATA_FILENAME, 'w', newline='') as out:
        csv_out=csv.writer(out)

        # Write header
        csv_out.writerow(['user_id','book_id', 'rating'])

        # Write data
        for row in rows:
            csv_out.writerow(row)

    DATABASE.ConnectionClose()