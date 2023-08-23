import requests
import psycopg2

class Api(ABC):
    """
    Класс для работы с API сайтов с вакансиями
    """
    @abstractmethod
    def get_vacancies(self, vacancy):
        pass

class ApiHH(Api):
    def get_vacancies(self, vacancy):
        hh_dict = {}
        for page in range(0, 3):
            params = {
                "text": vacancy,
                "per_page": 100,
                "page": page,
            }
            response = requests.get("https://api.hh.ru/vacancies", params=params).json()
            hh_dict.update(response)
        return hh_dict

def get_hh_vacancies_list(raw_hh_data):
    """
    Преобразование вакансий из HeadHunter в значения атрибутов экземпляров класса Vacancy
    :param raw_hh_data:
    :return:
    """
    vacancies = []
    for raw_hh_vacancy in raw_hh_data:
        try:
            title = raw_hh_vacancy['name']
            url = raw_hh_vacancy['alternate_url']
            salary = raw_hh_vacancy['salary'].get('from')
            if raw_hh_vacancy['snippet']['requirement'] is None:
                requirements = "Описание не указано"
            else:
                requirements = raw_hh_vacancy['snippet']['requirement']
        except AttributeError:
            title = raw_hh_vacancy['name']
            url = raw_hh_vacancy['alternate_url']
            salary = None
            if raw_hh_vacancy['snippet']['requirement'] is None:
                requirements = "Описание не указано"
            else:
                requirements = raw_hh_vacancy['snippet']['requirement']
        validate_salary = Vacancy.validate_salary(salary)
        validate_requirements = Vacancy.validate_requirements(requirements)
        hh_vacancy = Vacancy(title, url, validate_salary, validate_requirements)
        vacancies.append(hh_vacancy)
    return vacancies



class DBManager:
    """
    Класс для работы с данными в PostgreSQL
    """
    def __init__(self, dbname: str, user: str, password: str, host: str = 'localhost', port: str = '5432'):
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        self.cur = self.conn.cursor()

    def get_companies_and_vacancies_count(self):
        """
        получает список всех компаний и количество вакансий у каждой компании
        """
        with self.conn:
            employers_list = []
            for i in range(1, 11):
                self.cur.execute(f"""
                SELECT name_employer, COUNT(*) FROM employer{i}
                GROUP BY name_employer
                """)
                data = self.cur.fetchall()
                for item in data:
                    data_dict = {"Компания": item[0], "Кол-во": item[1]}
                    employers_list.append(data_dict)
            return employers_list

    def get_all_vacancies(self):
        """
        получает список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию
        """
        with self.conn:
            vacancy_list = []
            for i in range(1, 11):
                self.cur.execute(f"""
                SELECT name_employer, title_vacancy, salary, url_vacancy FROM employer{i}
                """)
                data = self.cur.fetchall()
                for item in data:
                    vacancy_dict = {"компания": item[0], "вакансия": item[1], "зарплата": item[2], "сслыка": item[3]}
                    vacancy_list.append(vacancy_dict)
            return vacancy_list

    def get_avg_salary(self):
        """
        получает среднюю зарплату по вакансиям
        """
        with self.conn:
            total_sum_salary = 0
            count = 0
            for i in range(1, 11):
                self.cur.execute(f"""
                SELECT SUM(salary), COUNT(salary) FROM employer{i}
                WHERE salary IS NOT NULL
                """)
                data = self.cur.fetchall()
                for d in data:
                    if d[0] is not None:
                        total_sum_salary += d[0]
                        count += d[1]
            avg_salary = total_sum_salary//count
            return avg_salary

    @staticmethod
    def get_vacancies_with_higher_salary(avg_salary, all_vacancies):
        """
        получает список всех вакансий, у которых зарплата выше средней по всем вакансиям
        """
        choice_vacancy = []
        for vac in all_vacancies:
            if vac["зарплата"] is not None and vac["зарплата"] > avg_salary:
                choice_vacancy.append(vac)
        sorted_vacancies = sorted(choice_vacancy, key=lambda x: x["зарплата"], reverse=False)
        return sorted_vacancies

    @staticmethod
    def get_vacancies_with_keyword(keyword, all_vacancies):
        """
        получает список всех вакансий, в названии которых содержатся переданные в метод слова, например python
        """
        vac_in_keyword = []
        for vac in all_vacancies:
            if keyword in vac["вакансия"].lower():
                vac_in_keyword.append(vac)
        return vac_in_keyword


def get_employers(employers_names: list):
    """
    Функция получения id компаний
    """
    employers = []
    for emp_name in employers_names:
        params = {
            "text": emp_name,
            "only_with_vacancies": True,
            "per_page": 100,
        }
        response = requests.get("https://api.hh.ru/employers", params=params).json()
        for item in response["items"]:
            if emp_name == item["name"]:
                emp_dict = {"id": item["id"], "name": item["name"]}
                employers.append(emp_dict)
                break
    return employers

def get_employer_vacancies(employer_id):
    """
    Функция получения вакансий компании
    """
    params = {
        "employer_id": employer_id,
        "area": 113,
        "per_page": 100,
    }
    response = requests.get("https://api.hh.ru/vacancies", params=params).json()
    return response


def create_database(params, db_name):
    """Создает новую базу данных"""
    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE {db_name}")
    cur.execute(f"CREATE DATABASE {db_name}")
    conn.close()

def create_table_employer(params, employers):
    """Проектирует таблицы в БД"""
    with psycopg2.connect(**params) as conn:
        with conn.cursor() as cur:
            for i in range(0, len(employers)):
                cur.execute(f"""
                CREATE TABLE IF NOT EXISTS employer{i + 1}(
                id serial PRIMARY KEY,
                id_employer int,
                name_employer varchar(255),
                title_vacancy varchar(255),
                city varchar(255),
                salary int,
                url_vacancy varchar(255),
                requirements text,
                responsibility text
                );
                """)

def insert_table_data(params, employer_vacancies: list[dict], table_name) -> None:
    """Вставляет данные с API в таблицы работодателей"""
    with psycopg2.connect(**params) as conn:
        with conn.cursor() as cur:
            for emp_vac in employer_vacancies:
                try:
                    id_employer = emp_vac['employer']['id']
                    name_employer = emp_vac['employer']['name']
                    title_vacancy = emp_vac['name']
                    city = emp_vac['area']['name']
                    salary = emp_vac['salary'].get('from')
                    url_vacancy = emp_vac['alternate_url']
                    if emp_vac['snippet']['requirement'] is None:
                        requirements = "Описание не указано"
                    else:
                        requirements = emp_vac['snippet']['requirement']
                    if emp_vac['snippet']['responsibility'] is None:
                        responsibility = "Описание не указано"
                    else:
                        responsibility = emp_vac['snippet']['responsibility']
                except AttributeError:
                    id_employer = emp_vac['employer']['id']
                    name_employer = emp_vac['employer']['name']
                    title_vacancy = emp_vac['name']
                    city = emp_vac['area']['name']
                    salary = None
                    url_vacancy = emp_vac['alternate_url']
                    if emp_vac['snippet']['requirement'] is None:
                        requirements = "Описание не указано"
                    else:
                        requirements = emp_vac['snippet']['requirement']
                    if emp_vac['snippet']['responsibility'] is None:
                        responsibility = "Описание не указано"
                    else:
                        responsibility = emp_vac['snippet']['responsibility']
                cur.execute(f"""
                INSERT INTO  {table_name}(id_employer, name_employer, title_vacancy, city, salary, url_vacancy, requirements, responsibility)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (id_employer, name_employer, title_vacancy, city, salary, url_vacancy, requirements, responsibility))
