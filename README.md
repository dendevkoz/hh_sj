# Прикиньте будущую зарплату

Скрипт выведет статистику по вакансиям программирования по наиболее популярным языкам по версии GitHub.

(данный скрипт работет только для Москвы)

### Как установить

- Зарегестрироваться на [SuperJob](https://api.superjob.ru/)
- Зарегестрироваться на [HadHunter](https://dev.hh.ru/admin/)
    - можно обойтись и без этого, но HH ограничивает кол-во вакансий
- Создайте файл `.env` и записать в него настройки:
    ```python
    SUPER_JOB_SECRET_KEY="Ваш ключ"
    ```
    ```python
    HH_SECRET_KEY="Ваш ключ"
    ```
- Потом создаём виртуальное окружение
    ```python
    python -m venv venv
    ```
    Путь до корневой папки 
    ```python 
    venv/scripts/activate
    ```
- Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:
    ```python
    pip install -r requirements.txt
    ```

### Запуск скрипта:

- Скрипт выдает статистику только по этим языкам:
    ```python
    'Python', 'C', 'C++', 'C#', 'Javascript', 'Java', 'PHP', 'Go'
    ```
- Команда для запуска
    ```python
      python3 main.py
    ```

