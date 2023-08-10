import requests

# Получаем данные о компаниях и вакансиях
response = requests.get(
    "https://api.hh.ru/vacancies/search?q=название компании&page=1&per_page=10"
)
data = response.json()["items"]

for company in data:
    print(company["name"])

    # Получаем список вакансий для этой компании
    response = requests.get(f"https://api.hh.ru/vacancies/{company['id']}")
    data = response.json()
    for job in data["jobs"]:
        print(job["title"])