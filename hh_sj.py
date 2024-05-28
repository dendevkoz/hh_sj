import requests
from dotenv import load_dotenv
import os
from terminaltables import DoubleTable
from contextlib import suppress
from time import sleep



def predict_rub_salary(min_salary, max_salary):
    if min_salary and max_salary:
        return int((min_salary + max_salary) / 2)
    elif max_salary:
        return int(max_salary * 0.8)
    elif min_salary:
        return int(min_salary * 1.2)


def check_division_by_zero(first_number, second_number):
    with suppress(ZeroDivisionError):
        answer = int(first_number / second_number)
        return answer


def get_statistics_salary_for_hh(languages, hh_token, city_id):
    statistics_vacancies_hh = {}
    for language in languages:
        hh_address = 'https://api.hh.ru/vacancies/'
        payload = {
            'text': language,
            'area': city_id,
            'period': '30',
            'api_key': hh_token,
        }
        salaries = []
        response = requests.get(hh_address, params=payload)
        vacancies_response = response.json()
        found = vacancies_response['found']
        pages = vacancies_response['pages']
        page = 1
        while page < pages:
            payload = {
                'professional_roles': [
                    {
                        'id': '96',
                        'name': 'Программист, разработчик'
                    }
                ],
                'text': language,
                'area': city_id,
                'period': '30',
                'api_key': hh_token,
                'page': page
            }
            vacancies_from_one_page = requests.get(hh_address, params=payload)
            with suppress(KeyError):
                vacancies = vacancies_from_one_page.json()['items']
            page += 1
            for vacancy in vacancies:
                if vacancy['salary'] and vacancy['salary']['currency'] == 'RUR':
                    min_salary = vacancy['salary']['from']
                    max_salary = vacancy['salary']['to']
                    salaries.append(predict_rub_salary(min_salary, max_salary))
        vacancies_statistics = {
                'vacancies_processed': len(salaries),
                'average_salary': check_division_by_zero(sum(salaries), len(salaries)),
                'vacancies_found': found,
            }
        sleep(5)
        statistics_vacancies_hh[language] = vacancies_statistics
    return statistics_vacancies_hh



def get_statistics_for_all_languages_by_sj(languages, sj_token, city_id):
    statistics_vacancies_sj = {}
    for language in languages:
        statistics_vacancies_sj[language] = get_statistics_salary_for_super_job(language, sj_token, city_id)
    return statistics_vacancies_sj


def get_statistics_salary_for_super_job(language, super_job_token, city_id):
    salaries = []
    url = 'https://api.superjob.ru/2.0/vacancies/catalogues/'
    headers = {
        'X-Api-App-Id': super_job_token
    }
    payload = {
        'town': city_id,
        'keyword': language,
        'vacancies_filter': 'it-internet-svyaz-telekom',
        'more': True,
    }
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    vacancies_response = response.json()
    vacancies_total = vacancies_response['total']
    if vacancies_response['more'] is True:
        vacancies = vacancies_response['objects']
        for vacancy in vacancies:
            min_salary = vacancy['payment_from']
            max_salary = vacancy['payment_to']
            if min_salary and max_salary:
                salaries.append(predict_rub_salary(min_salary, max_salary))
    vacancies_statistics = {
        'vacancies_processed': len(salaries),
        'average_salary': check_division_by_zero(sum(salaries), len(salaries)),
        'vacancies_found': vacancies_total,
    }
    return vacancies_statistics


def generate_table(statistics_vacancies):
    tabel_statistics_about_filtered_vacancies = list()
    tabel_statistics_about_filtered_vacancies.append(('Язык программирования', 'Вакансий найдено',
                                                      'Вакансий обработано', 'Средняя зарплата'))

    search_vacancies_info = statistics_vacancies.items()
    for language_for_table, statistic_vacancies_for_table in search_vacancies_info:
        row_table = (language_for_table, statistic_vacancies_for_table['vacancies_found'],
                     statistic_vacancies_for_table['vacancies_processed'],
                     statistic_vacancies_for_table['average_salary'])
        tabel_statistics_about_filtered_vacancies.append(row_table)
    return tabel_statistics_about_filtered_vacancies


if __name__ == "__main__":
    load_dotenv()
    city_id_for_sj, city_id_for_hh = '4', '1'
    secret_key_super_job = os.getenv("SUPER_JOB_SECRET_KEY")
    secret_key_hh = os.getenv("HH_SECRET_KEY")
    programming_languages = ('Python', 'C', 'C++', 'C#', 'Javascript', 'Java', 'PHP', 'Go')

    all_statistics_for_sj = get_statistics_for_all_languages_by_sj(programming_languages,
                                                                   secret_key_super_job,
                                                                   city_id_for_sj)
    title_sj = "SuperJob (Moscow)"
    table = generate_table(all_statistics_for_sj)
    table_statistics_sj = DoubleTable(table, title_sj)
    print(table_statistics_sj.table)

    all_statistics_for_hh = get_statistics_salary_for_hh(programming_languages, secret_key_hh, city_id_for_hh)
    title_hh = "HeadHunter (Moscow)"
    table = generate_table(all_statistics_for_hh)
    table_statistics_hh = DoubleTable(table, title_hh)
    print(table_statistics_hh.table)
