import requests
import re
import csv
import datetime
import pyfiglet
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

# Creating session
session = requests.Session()

# List with dictionaries with information about each vacancy
vacancy_info = []

# link to main page
link_to_main = 'https://jobs.dou.ua/'


def create_user_agent():
    """
    get random user-agent
    :return: return dictionary with headers
    """
    ua = UserAgent()
    return ua.random


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

    # get csrf token using regular expression
    csrf = str(re.findall("window.CSRF_TOKEN = \"(.*)\"", str(scripts))[0])

    # create load data for ajax request
    data = {
        'csrfmiddlewaretoken': csrf,
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

    # get all links to vacancies in category
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

    # get vacancy name
    try:
        vacancy_name = html.find("h1", class_="g-h2").text
    except:
        vacancy_name = ''

    # get comany name
    try:
        company_name = html.find("div", class_="l-n").find("a").text
    except:
        company_name = ''

    # get city name
    try:
        city = html.find("div", class_="sh-info").find("span").text.lstrip()
    except:
        city = ''

    # get posting date
    try:
        date = html.find("div", class_="date").text
    except:
        date = ''

    # import to csv file
    write_row_to_csv(vacancy_name, link, vacancy_category, company_name, city, date)


def write_row_to_csv(vacancy_name, link, vacancy_category, company_name, city, date):
    """
    Import all info to csv file
    """
    date = datetime.date.today()
    path = date.strftime("%Y-%m-%d") + '.csv'

    with open(path, 'a', newline='', encoding='utf8') as f:
        writer = csv.writer(f, delimiter=';')

        writer.writerow([vacancy_name, link, vacancy_category, company_name, city, date])


if __name__ == "__main__":
    print(pyfiglet.figlet_format('jobs . dou', font="slant"))

    # get header and user_agent
    user_agent = create_user_agent()

    # Request headers
    headers = {"user-agent": user_agent,
               'Accept': 'application/json, text/javascript, */*; q=0.01',
               'Accept - Encoding': 'gzip, deflate, br',
               'Accept - Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
               'Referer': ''}

    # get categories
    vacancy_categories = get_categories(get_html(link_to_main))
    print(f"\nCount of categories: {len(vacancy_categories)}")

    for category in vacancy_categories:
        # list in which we add links to vacancies
        links_to_vacancies = []

        category_name = category['name']
        print(f"\nParsing category: {category_name}")

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

        # parsing information of vacancies
        for vacancy_url in links_to_vacancies:
            print(f"Parsing vacancy: {vacancy_url}")

            try:
                # get content on page
                page_content = get_html(vacancy_url)

                get_info(page_content, vacancy_url, category_name)

            except Exception as e:
                print(f"{e} - {vacancy_url}")
