import psycopg2
class DBManager:
def init(self):
self.connection = None
self.cursor = None
def connect_to_db(self, host, port, database, user, password):
    try:
        connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        self.connection = connection
        self.cursor = connection.cursor()
        return True
    except psycopg2.OperationalError as e:
        print("Ошибка подключения к базе данных:", e)
        return False

# метод для получения списка всех компаний и количества вакансий у каждой из них
def get_companies_and_vacancy_count(self):
    query = "SELECT company_name, COUNT(*) AS vacancy_count FROM vacancies GROUP BY company_name"
    result = self.cursor.execute(query)
    companies_and_vacancy_counts = []
    for row in result:
        companies_and_vacancy_counts.append({
            "company_name": row[0],
            "vacancy_count": row[1]
        })
    return companies_and_vacancy_counts

# метод для получения списка всех вакансий с названием компании, названием вакансии и зарплатой и ссылкой на вакансию
def get_all_vacancies(self, company_id):
    query = "SELECT * FROM vacancies WHERE company_id = %s"
    parameters = (company_id,)
    result = self.cursor.execute(query, parameters)
