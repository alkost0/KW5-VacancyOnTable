from src.utils import get_employers, get_employer_vacancies
from src.database_utils import create_database, create_table_employer, insert_table_data
from src.manager import DBManager
from src.config import config


def main():
    """
    Главная функция работы с вакансиями с сайта поиска работы hh.ru (HeadHunter.ru) и записью выборок в БД на Postgre
    Показаны выводами на экран основные взаимодействия с пользователем
    """
    db_name = "vacancy_hh"
    params = config()

    create_database(params, db_name)
    print(f"БД {db_name} успешно создана")

    params.update({'dbname': db_name})
    names_employers = ["Газпромбанк", "skyeng", "Открытие", "Яндекс", "GMS", "Росатом", "Тинькофф", "VK", "ВТБ",
                       "Сбертех"]
    employers = get_employers(names_employers)
    create_table_employer(params, employers)
    print("Таблицы успешно созданы")
    index_employer = 1
    for employer in employers:
        employer_vacancies = get_employer_vacancies(employer["id"])["items"]
        insert_table_data(params, employer_vacancies, f'employer{index_employer}')
        index_employer += 1
    print("Данные в таблицы успешно добавлены")
    print()

    bd = DBManager(**params)
    print("Список всех компаний и количество вакансий в каждой компании: ")
    print(bd.get_companies_and_vacancies_count())
    print()
    all_vacancies = bd.get_all_vacancies()
    print(f"Список всех вакансий: {all_vacancies}")
    avg_salary = bd.get_avg_salary()
    print(f"Средняя зарплата по всем вакансиям(для которых она указана): {avg_salary} руб.")
    print()
    print("Список вакансий, где з/п больше средней: ")
    print(bd.get_vacancies_with_higher_salary(avg_salary, all_vacancies))
    print()
    print("Список вакансий по ключевому слову: например, Python: ")
    print(bd.get_vacancies_with_keyword("python", all_vacancies))


if __name__ == "__main__":
    main()
