import requests
from dotenv import load_dotenv
import os
import math
from terminaltables import DoubleTable

STATISTICS_VACANCIES_SJ = {}
STATISTICS_VACANCIES_HH = {}
AVERAGE_SALARY = []
TABLE_DATA_VACANCIES = []


def predict_rub_salary(min_salary, max_salary, average_salary):
    if min_salary and max_salary is not None:
        average = int((min_salary + max_salary) / 2)
        average_salary.append(average)
    elif min_salary is None:
        average = int(max_salary * 0.8)
        average_salary.append(average)
    else:
        average = int(min_salary * 1.2)
        average_salary.append(average)
    return average_salary


def predict_rub_salary_for_hh(language, hh_token):
    hh_address = 'https://api.hh.ru/vacancies/'
    payload = {
        'api_key': hh_token,
        'text': language,
        'area': '1',
        'period': '30',
        "only_with_salary": "true",
        "salary.from": "true",
        "salary.to": "true"
    }
    response = requests.get(hh_address, params=payload)
    relevant_vacancies = 0
    vacancies = response.json()['items']
    found = response.json()['found']
    vacancies_info = dict(vacancies_found=found)
    pages = response.json()['pages']
    page = 0
    while page < pages:
        response = requests.get(hh_address, params={'page': page})
        response.raise_for_status()
        page += 1
        for vacancy in vacancies:
            if vacancy['salary']['currency'] != 'RUR':
                pass
            else:
                salary = vacancy['salary']
                min_salary = salary['from']
                max_salary = salary['to']
                if min_salary and max_salary is None:
                    pass
                else:
                    predict_rub_salary(min_salary, max_salary, AVERAGE_SALARY)
                    relevant_vacancies += 1
    vacancies_info['vacancies_processed'] = relevant_vacancies
    vacancies_info['average_salary'] = int(sum(AVERAGE_SALARY) / len(AVERAGE_SALARY))
    STATISTICS_VACANCIES_HH[language] = vacancies_info
    return STATISTICS_VACANCIES_HH


def predict_rub_salary_for_super_job(language, super_job_token):
    url = "https://api.superjob.ru/2.0/vacancies/catalogues/"
    headers = {
        "X-Api-App-Id": super_job_token
    }

    payload = {
        "t": "4",
        'keyword': language
    }
    vacancies_info = {}
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    vacancies_total = response.json()['total']
    vacancies_info['vacancies_found'] = vacancies_total
    vacancies_on_page = 20
    pages = math.ceil(vacancies_total / vacancies_on_page)
    relevant_vacancies = 0
    page = 0
    while page < pages:
        response = requests.get(url, headers=headers,
                                params={'page': page, 'keyword': language, "t": "4"})
        response.raise_for_status()
        page += 1
        vacancies = response.json()['objects']
        for vacancy in vacancies:
            professions = vacancy['catalogues']
            for profession in professions:
                if profession['title'] == "IT, Интернет, связь, телеком":
                    if vacancy['currency'] == 'rub':
                        min_salary = vacancy['payment_from']
                        max_salary = vacancy['payment_to']
                        if min_salary + max_salary == 0:
                            pass
                        else:
                            relevant_vacancies += 1
                            predict_rub_salary(min_salary, max_salary, AVERAGE_SALARY)
        vacancies_info['vacancies_processed'] = relevant_vacancies
        vacancies_info['average_salary'] = int(sum(AVERAGE_SALARY) / len(AVERAGE_SALARY))
        STATISTICS_VACANCIES_SJ[language] = vacancies_info
        return STATISTICS_VACANCIES_SJ


def generate_tables(statistics_vacancies):
    TABLE_DATA_VACANCIES.append(("Язык программирования", "Вакансий найдено", "Вакансий обработано", "Средняя зарплата"))

    data_vacancies = statistics_vacancies.items()
    for statistics in data_vacancies:
        row_table = (statistics[0], statistics[1]['vacancies_found'], statistics[1]['vacancies_processed'],
                     statistics[1]['average_salary'])
        TABLE_DATA_VACANCIES.append(row_table)

    return TABLE_DATA_VACANCIES


if __name__ == "__main__":
    load_dotenv()
    secret_key_super_job = os.getenv("SUPER_JOB_SECRET_KEY")
    secret_key_hh = os.getenv("HH_SECRET_KEY")
    programming_languages = ('Python', 'C', 'C++', 'C#', 'Javascript', 'Java', 'PHP', 'Go')
    try:
        # for language in programming_languages:
        #     predict_rub_salary_for_super_job(language, secret_key_super_job)
        # title_sj = "SuperJob (Moscow)"
        # table = generate_tables(STATISTICS_VACANCIES_SJ)
        # table_statistics = DoubleTable(table, title_sj)
        # print(table_statistics.table)
        for language in programming_languages:
            predict_rub_salary_for_hh(language, secret_key_hh)
        print(predict_rub_salary_for_hh)
        # TABLE_DATA_VACANCIES.clear()
        # title_hh = "HeadHunter (Moscow)"
        # table = generate_tables(STATISTICS_VACANCIES_HH)
        # table_statistics = DoubleTable(table, title_hh)
        # print(table_statistics.table)
    except requests.exceptions.RequestException as err:
        print(f'Что то не так!\n {err}')

