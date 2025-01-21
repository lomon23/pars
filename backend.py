import requests
from bs4 import BeautifulSoup
import mysql.connector

class JobParser:
    def __init__(self, url):
        self.url = url

    def fetch_jobs(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            jobs = []
            for job_element in soup.find_all('div', class_='card-content'):
                title = job_element.find('h2', class_='title').text.strip()
                company = job_element.find('h3', class_='subtitle').text.strip()
                location = job_element.find('p', class_='location').text.strip()
                date = job_element.find('time')['datetime']
                jobs.append((title, company, location, date))
            return jobs
        else:
            raise Exception(f"Failed to fetch data from {self.url}, status code: {response.status_code}")

class MySQLHandler:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.connection.cursor()

    def create_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS jobs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255),
            company VARCHAR(255),
            location VARCHAR(255),
            date DATE
        )
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()

    def insert_jobs(self, jobs):
        insert_query = "INSERT INTO jobs (title, company, location, date) VALUES (%s, %s, %s, %s)"
        self.cursor.executemany(insert_query, jobs)
        self.connection.commit()

    def close_connection(self):
        self.cursor.close()
        self.connection.close()

class JobToDatabase:
    def __init__(self, parser, db_handler):
        self.parser = parser
        self.db_handler = db_handler

    def run(self):
        jobs = self.parser.fetch_jobs()
        self.db_handler.connect()
        self.db_handler.create_table()
        self.db_handler.insert_jobs(jobs)
        self.db_handler.close_connection()

# URL для парсингу
url = "https://realpython.github.io/fake-jobs/"

# Налаштування для підключення до MySQL
host = "localhost"
user = "root"
password = "lo123TAV"
database = "my_database"

# Ініціалізація об'єктів
parser = JobParser(url)
db_handler = MySQLHandler(host, user, password, database)
job_to_db = JobToDatabase(parser, db_handler)

# Виконання парсингу та збереження в базу даних
if __name__ == "__main__":
    try:
        job_to_db.run()
        print("Дані успішно збережено в базу даних!")
    except Exception as e:
        print(f"Помилка: {e}")
