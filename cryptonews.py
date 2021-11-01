import requests
from bs4 import BeautifulSoup
import json
import re

URL = 'https://cryptonews.net/ru/news/'


def get_soup(url):
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
    return BeautifulSoup(r, 'html.parser')


def save_json(data):
    with open('cryptonews_data.json', "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def main():
    news_data = {}

    soup = get_soup(URL)

    # Получаем все ссылки на новости
    news_links = soup.find('section', class_='col-xs-12 col-sm').find_all('a', {'class': ['title']})

    # Для каждой ссылки получаем информацию и записываем в news_data
    for i in range(10):

        link = "https://cryptonews.net" + news_links[i].get('href').split('?')[0]
        name = link
        news_data[name] = {}
        soup = get_soup(link)

        # Переходим на страницу для дальнейшенго парсинга
        article = soup.find('section', class_='col-xs-12 col-sm')
        category = soup.find('span', class_='flex middle-xs')
        title = article.find('h1')
        url_pattern = r'https://[\S]+'
        image = article.find('div', class_='detail-image-wrap').get('style')
        image = re.findall(url_pattern, image.rstrip(')'))[0]

        date = article.find('span', class_='datetime flex middle-xs').text

        article_paragraphs = soup.find('div', class_='news-item detail content_text').find_all('p')
        article_text = ''
        for paragraph in article_paragraphs:
            article_text += paragraph.text

        # Заполняем полученными данными news_data
        news_data[name]['link'] = link
        news_data[name]['date'] = date.strip() + " назад"
        news_data[name]['text'] = article_text.replace('\xa0', '').replace('\r', '')

        try:
            news_data[name]['title'] = title.text
        except AttributeError:
            news_data[name]['title'] = 'Без заголовка'
        try:
            news_data[name]['category'] = category.text.replace('\n', '')
        except AttributeError:
            news_data[name]['category'] = 'Без категории'
        try:
            news_data[name]['image'] = image
        except AttributeError:
            news_data[name]['image'] = 'Без обложки'

    return news_data
    #     print(news_data)

    # for key, value in news_data.items():
    #     print("№" + str(list(news_data.keys()).index(key) + 1))
    #     print(value['link'], "\n", value['title'], "\n", value['category'], "\n", value['image'], "\n", value['date'],
    #           "\n", value['text'], "\n")

    #     save_json(news_data)

# main()
