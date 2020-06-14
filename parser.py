import requests
import re
from bs4 import BeautifulSoup

HEADERS = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
(KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
           'Accept': 'application/json, text/javascript, */*; q=0.01',
           'Accept - Encoding': 'gzip, deflate, br',
            'Accept - Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
           'Referer': 'https://jobs.dou.ua/vacancies/?category=Python'}

URL = "https://jobs.dou.ua/vacancies/?category=Python"

session = requests.Session()

links_for_vacancies = []


def get_html(url):
    r = session.get(url, headers=HEADERS)
    return r.text


def get_links(content):
    html = BeautifulSoup(content, "html.parser")
    for li in html.find_all('li', class_="l-vacancy"):
        links_for_vacancies.append(li.find('a', class_="vt").get('href'))
    return links_for_vacancies


def get_csrf(content):
    html = BeautifulSoup(content, "html.parser")
    scripts = html.find_all("script")
    data = {
        'csrfmiddlewaretoken': str(re.findall("window.CSRF_TOKEN = \"(.*)\"", str(scripts))[0]),
        'count': 20}
    return data


def get_vacancy_count(content):
    html = BeautifulSoup(content, "html.parser")
    count = int(re.search("[0-9]+", html.find("h1").get_text()).group())
    return count


def get_ajax_response():
    while load_data['count'] <= count_of_vacancy:
        post_response = session.post("https://jobs.dou.ua/vacancies/xhr-load/?category=Python", data=load_data,
                                     headers=HEADERS).json()
        get_links(post_response["html"])
        load_data["count"] += 40


if __name__ == "__main__":
    count_of_vacancy = get_vacancy_count(get_html(URL))
    load_data = get_csrf(get_html(URL))
    get_links(get_html(URL))
    print(links_for_vacancies)
    get_ajax_response()
    print(links_for_vacancies)
