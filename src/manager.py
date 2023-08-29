import psycopg2

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

