import requests
from dotenv import load_dotenv
import os
from terminaltables import DoubleTable
from contextlib import suppress
from itertools import count


def predict_rub_salary(min_salary, max_salary):
    if min_salary and max_salary:
        return int((min_salary + max_salary) / 2)
    elif max_salary:
        return int(max_salary * 0.8)
    elif min_salary:
        return int(min_salary * 1.2)


def check_division_by_zero(first_number, second_number):
    with suppress(ZeroDivisionError):
        result = int(first_number / second_number)
        return result


def statistics_salary_for_hh(languages, hh_token, city_id):
    statistics_vacancies_hh = {}
    for language in languages:
        salaries = []
        hh_address = 'https://api.hh.ru/vacancies/'
        payload = {
            'text': language,
            'area': city_id,
            'period': '30',
            'api_key': hh_token,
        }
        response = requests.get(hh_address, params=payload)
        resp_json = response.json()
        vacancies = resp_json['items']
        found = resp_json['found']
        pages = resp_json['pages']
        page = 0
        vacancies_info = {
            'vacancies_processed': '',
            'average_salary': '',
            'vacancies_found': '',
        }
        while page < pages:
            page += 1
            for vacancy in vacancies:
                if vacancy['salary'] and vacancy['salary']['currency'] == 'RUR':
                    if vacancy['salary']['currency'] == 'RUR':
                        min_salary = vacancy['salary']['from']
                        max_salary = vacancy['salary']['to']
                        salaries.append(predict_rub_salary(min_salary, max_salary))
        vacancies_info['average_salary'] = check_division_by_zero(sum(salaries),
                                                                  len(salaries))
        vacancies_info['vacancies_processed'] = len(salaries)
        vacancies_info['vacancies_found'] = found
        statistics_vacancies_hh[language] = vacancies_info
    return statistics_vacancies_hh


def get_sj_page(language, super_job_token, page, town):
    url = 'https://api.superjob.ru/2.0/vacancies/catalogues/'
    headers = {
        'X-Api-App-Id': super_job_token
    }

    payload = {
        'town': town,
        'keyword': language,
        'vacancies_filter': 'it-internet-svyaz-telekom',
        'page': page,
        'count': 5,
    }
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    vacancies_response = response.json()
    return vacancies_response


def statistics_salary_for_super_job(languages, super_job_token, city_id):
    statistics_vacancies_sj = {}
    vacancies_limit = 500
    vacancies_on_page = 5
    stop_page = vacancies_limit / vacancies_on_page

    for language in languages:
        vacancies_info = {
            'vacancies_processed': '',
            'average_salary': '',
            'vacancies_found': '',
        }
        salaries = []
        for page in count():
            vacancies_response_from_sj = get_sj_page(
                language, super_job_token, page, city_id)
            vacancies_total = vacancies_response_from_sj['total']
            vacancies = vacancies_response_from_sj['objects']
            for vacancy in vacancies:
                min_salary = vacancy['payment_from']
                max_salary = vacancy['payment_to']
                if min_salary and max_salary:
                     salaries.append(predict_rub_salary(min_salary, max_salary))
            if page >= vacancies_response_from_sj['total']//vacancies_on_page:
                break
            elif page >= stop_page:
                break
            vacancies_info['average_salary'] = check_division_by_zero(sum(salaries),
                                                                             len(salaries))
        
            vacancies_info['vacancies_found'] = vacancies_total
        vacancies_info['vacancies_processed'] = len(salaries)
        statistics_vacancies_sj[language] = vacancies_info
    return statistics_vacancies_sj


def generate_table(statistics_vacancies):
    tabel_info_about_filtered_vacancies = list()
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

    all_statistics_for_sj = statistics_salary_for_super_job(programming_languages,
                                                            secret_key_super_job,
                                                            city_id_for_sj)
    title_sj = "SuperJob (Moscow)"
    table = generate_table(all_statistics_for_sj)
    table_statistics_sj = DoubleTable(table, title_sj)
    print(table_statistics_sj.table)

    all_statistics_for_hh = statistics_salary_for_hh(programming_languages,
                                                     secret_key_hh,
                                                     city_id_for_hh)
    title_hh = "HeadHunter (Moscow)"
    table = generate_table(all_statistics_for_hh)
    table_statistics_hh = DoubleTable(table, title_hh)
    print(table_statistics_hh.table)


