import requests
import psycopg2


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