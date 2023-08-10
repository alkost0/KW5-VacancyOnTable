import psycopg2
from typing import List, Optional

class DBManager(object):
    def __init__(
        self,
        conn_string: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """
        :param conn_string: строка подключения к базе данных
        :type conn_string: str
        :param username: имя пользователя для подключения к БД
        :type username: Optional[str]
        :param password: пароль для подключения к БД
        :type password: Optional[str]
        """

        if not conn_string.startswith("postgresql://"):
            raise ValueError("Некорректная строка подключения")

        self.__conn = psycopg2.connect(**dict(conn_string))

    @property
    def cursor(self) -> psycopg2.extras.RealDictCursor:
        """Возвращает курсор для работы с таблицей"""
        return self.__conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def execute(self, sql: str) -> int:
        """Выполняет запрос к БД"""
        cursor = self.cursor()

        try:
            cursor.execute(sql)
        finally:
            if cursor is not None:
                cursor.close()

        return cursor.rowcount

    def _get_company_vacancies(self, company_id: int) -> List[dict]:
        """Получает список вакансий у компании"""
        sql = """
        SELECT job_title, salary, link
        FROM jobs
        WHERE company_id = %s
        ORDER BY salary DESC
