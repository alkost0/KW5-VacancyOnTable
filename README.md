# KW5-VacancyOnTable

В рамках проекта получаем данные о компаниях и вакансиях с сайта hh.ru, спроектировать таблицы в БД PostgreSQL и загрузить полученные данные в созданные таблицы.

В файле database.ini нужно указать настройки доступа к БазеДанных, в указанном стандартном порядке, например: [postgresql]
user=postgres, password=ваш_пароль, host=127.0.0.1, port=5432

Вспомогательные main-файлу файлы вынесены в папку src, а именно: utils для работы с вакансиями, manager - для менеджера работы с БД, database_utils для функций для работы с БД и config с парсером(использующий внутренний пайтон-алгоритм).
