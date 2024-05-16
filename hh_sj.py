import requests
from dotenv import load_dotenv
import os
import math
from terminaltables import DoubleTable


def predict_rub_salary(min_salary, max_salary):
    if min_salary and max_salary:
        return int((min_salary + max_salary) / 2)
    elif max_salary:
        return int(max_salary * 0.8)
    elif min_salary:
        return int(min_salary * 1.2)


def checking_division_by_zero(first_number, second_number):
    with suppress(ZeroDivisionError):
        result = int(first_number / second_number)
        return result


def predict_rub_salary_for_hh(language, hh_token, city_id):
    hh_address = 'https://api.hh.ru/vacancies/'
    payload = {
        'text': language,
        'area': city_id,
        'period': '30',
        'salary.from': 'true',
        'salary.to': 'true',
        'api_key': hh_token,
    }
    response = requests.get(hh_address, params=payload)
    relevant_vacancies = 0
    resp_json = response.json()
    vacancies = resp_json['items']
    pages = resp_json['pages']
    page = 0
    while page < pages:
        page += 1
        for vacancy in vacancies:
            with suppress(TypeError):
                if vacancy['salary']['currency'] == 'RUR':
                    min_salary = vacancy['salary']['from']
                    max_salary = vacancy['salary']['to']
                    if min_salary and max_salary:
                        average_salary.append(predict_rub_salary(min_salary, max_salary))
                        relevant_vacancies += 1
    vacancies_info = {
        'vacancies_processed': relevant_vacancies,
        'average_salary': checking_division_by_zero(sum(average_salary), len(average_salary)),
        'vacancies_found':  len(average_salary)
    }
    statistics_vacancies_hh[language] = vacancies_info
    return statistics_vacancies_hh


def predict_rub_salary_for_super_job(language, super_job_token, city_id):
    url = 'https://api.superjob.ru/2.0/vacancies/catalogues/'
    headers = {
        'X-Api-App-Id': super_job_token
    }

    payload = {
        'city_id': city_id,
        'keyword': language,
        'vacancies_filter': 'it-internet-svyaz-telekom'
    }
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    resp_json = response.json()
    vacancies_total = resp_json['total']
    vacancies_on_page = 20
    pages = math.ceil(vacancies_total / vacancies_on_page)
    relevant_vacancies = 0
    page = 0
    while page < pages:
        page += 1
        vacancies = resp_json['objects']
        for vacancy in vacancies:
            min_salary = vacancy['payment_from']
            max_salary = vacancy['payment_to']
            if not min_salary and not max_salary:
                pass
            else:
                average_salary.append(predict_rub_salary(min_salary, max_salary))
                relevant_vacancies += 1
        vacancies_info = {
            'vacancies_processed': relevant_vacancies,
            'average_salary': checking_division_by_zero(sum(average_salary), len(average_salary)),
            'vacancies_found':  vacancies_total,
        }
        statistics_vacancies_sj[language] = vacancies_info
        return statistics_vacancies_sj


def generate_table(statistics_vacancies):
    tabel_info_about_filtered_vacancies.append(('Язык программирования',
                                                'Вакансий найдено',
                                                'Вакансий обработано',
                                                'Средняя зарплата'
                                                ))

    search_vacancies_info = statistics_vacancies.items()
    for language_for_table, statistic_vacancies_for_table in search_vacancies_info:
        row_table = (language_for_table, statistic_vacancies_for_table['vacancies_found'],
                     statistic_vacancies_for_table['vacancies_processed'],
                     statistic_vacancies_for_table['average_salary'])
        tabel_info_about_filtered_vacancies.append(row_table)
    return tabel_info_about_filtered_vacancies


if __name__ == "__main__":
    load_dotenv()
    city_id_for_sj, city_id_for_hh = '4', '1'
    secret_key_super_job = os.getenv("SUPER_JOB_SECRET_KEY")
    secret_key_hh = os.getenv("HH_SECRET_KEY")
    programming_languages = ('Python', 'C', 'C++', 'C#', 'Javascript', 'Java', 'PHP', 'Go')
    statistics_vacancies_sj = {}
    statistics_vacancies_hh = {}
    average_salary = []
    tabel_info_about_filtered_vacancies = []

    try:
        for language in programming_languages:
            predict_rub_salary_for_super_job(language, secret_key_super_job, city_id_for_sj)
    except requests.exceptions.HTTPError as http_err:
        print(f'Проверьте корректность ввода ключа API\n {http_err}')
    title_sj = "SuperJob (Moscow)"
    table = generate_table(statistics_vacancies_sj)
    table_statistics = DoubleTable(table, title_sj)
    print(table_statistics.table)

    try:
        for language in programming_languages:
            predict_rub_salary_for_hh(language, secret_key_hh, city_id_for_hh)
    except requests.exceptions.HTTPError as http_err:
        print(f'Проверьте корректность ввода ключа API\n {http_err}')
    tabel_info_about_filtered_vacancies.clear()
    title_hh = "HeadHunter (Moscow)"
    table = generate_table(statistics_vacancies_hh)
    table_statistics = DoubleTable(table, title_hh)
    print(table_statistics.table)


