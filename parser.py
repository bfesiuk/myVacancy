import requests
import re
import csv
import datetime
from bs4 import BeautifulSoup

# Request headers
headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
(KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
           'Accept': 'application/json, text/javascript, */*; q=0.01',
           'Accept - Encoding': 'gzip, deflate, br',
            'Accept - Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
           'Referer': ''}

# Creating session
session = requests.Session()

# List with dictionaries with information about each vacancy
vacancy_info = []

# link to main page
link_to_main = 'https://jobs.dou.ua/'


def get_html(url):
    """
    connecting to website
    :param url: link to site
    :return: page content
    """
    r = session.get(url, headers=headers)
    return r.text


def get_categories(content):
    """
    search all categories names and links
    :param content: page content
    :return: list of dictionaries with category link and name
    """
    categories = []

    # creating a BeautifulSoup object based on the received content
    html = BeautifulSoup(content, "html.parser")

    for category in html.find_all("a", class_="cat-link"):
        name = category.text
        link = str(category.get("href"))

        # regular expression to search for url
        link = re.findall("vacancies/(.*)", link)[0]

        categories.append({"name": name, "url": link})
    return categories


def get_links(content):
    """
    add to list vacancy link
    :param content: page content
    """

    html = BeautifulSoup(content, "html.parser")

    for li in html.find_all('li', class_="l-vacancy"):
        link = li.find('a', class_="vt").get('href')
        links_to_vacancies.append(link)


def get_csrf(content):
    """
    get CSRF token and data generation for ajax request
    :param content: page content
    :return: dictionary with Form Data
    """

    html = BeautifulSoup(content, "html.parser")

    scripts = html.find_all("script")
    data = {
        'csrfmiddlewaretoken': str(re.findall("window.CSRF_TOKEN = \"(.*)\"", str(scripts))[0]),
        'count': 20}
    return data


def get_vacancy_count(content):
    """
    get count of vacancies in selected category
    :param content: page content
    :return: count of vacancies
    """

    html = BeautifulSoup(content, "html.parser")

    count = int(re.search("[0-9]+", html.find("h1").get_text()).group())
    return count


def get_ajax_response(link):
    """
    post ajax request, get ajax response and call the function to get links to vacancies
    :param link: link for ajax request
    :return:
    """
    headers['Referer'] = link

    while load_data['count'] <= count_of_vacancy:
        post_response = session.post(link, data=load_data, headers=headers).json()
        get_links(post_response["html"])
        load_data["count"] += 40


def get_info(content, link, vacancy_category):
    """
    Get all information about the each vacancy
    :param content: page content
    :param vacancy_category: vacancy category
    :param link: link to vacancy
    """

    html = BeautifulSoup(content, "html.parser")
    vacancy_name = html.find("h1", class_="g-h2").text
    company_name = html.find("div", class_="l-n").find("a").text
    city = html.find("div", class_="sh-info").find("span").text.lstrip()
    date = html.find("div", class_="date").text
    vacancy_info.append({"vacancy_name": vacancy_name, "url": link, "vacancy_category": vacancy_category,
                         "company_name": company_name, "city": city, "date": date})


def import_csv(items, path):
    """
    Import all vacancies to csv file
    :param items: list with vacancies
    :param path: path to file
    """
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')

        # add headers
        writer.writerow(['Vacancy name', 'Link', 'Category', 'Company name', 'City', 'Publish date'])

        for item in items:
            writer.writerow([item['vacancy_name'], item['url'], item['vacancy_category'], item['company_name'],
                             item['city'], item['date']])


if __name__ == "__main__":

    # get categories
    vacancy_categories = get_categories(get_html(link_to_main))

    for category in vacancy_categories[:1]:
        # list in which we add links to vacancies
        links_to_vacancies = []

        category_name = category['name']

        # create links to webpage and ajax request
        vacancy_link = 'https://jobs.dou.ua/vacancies/'+category['url']
        ajax_link = 'https://jobs.dou.ua/vacancies/xhr-load/'+category['url']

        # get count of vacancies in current category
        count_of_vacancy = get_vacancy_count(get_html(vacancy_link))

        # get Form Data for ajax request
        load_data = get_csrf(get_html(vacancy_link))

        # add links to links_to_vacancies from webpage and ajax response
        get_links(get_html(vacancy_link))
        get_ajax_response(ajax_link)

        for vacancy in links_to_vacancies:
            get_info(get_html(vacancy), vacancy, category_name)

    # сreate file name using сurrent date and time
    date = datetime.date.today()
    file_name = 'vacancies ' + date.strftime("%Y-%m-%d") + '.csv'

    import_csv(vacancy_info, file_name)
    print(len(vacancy_info))
    print(vacancy_info)
