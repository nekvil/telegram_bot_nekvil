import requests
from bs4 import BeautifulSoup
import json

URL = 'https://www.rbc.ru/crypto/'


def get_soup(url):
    r = requests.get(url).text
    return BeautifulSoup(r, 'html.parser')


def save_json(data):
    with open('rbk_data.json', "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def main():
    news_data = {}
    soup = get_soup(URL)

    # Получаем все ссылки на новости
    news_links = soup.find('div', class_='l-col-main').find_all('a', {'class': ['item__link', 'main__feed__link']})
    #     print(len(news_links),news_links)

    # Для каждой ссылки получаем информацию и записываем в news_data
    for i in range(9):

        link = news_links[i].get('href').split('?')[0]
        name = link
        news_data[name] = {}
        soup = get_soup(link)

        # Переходим на страницу для дальнейшенго парсинга
        article = soup.find('div', class_='article')
        category = article.find('a', class_='article__header__category')
        date = article.find('span', class_='article__header__date').get('content').replace('T', ' ').split('+')[0]
        title = article.find('h1', class_='js-slide-title')
        image = article.find('div', class_='article__main-image')

        overview = article.find('div', class_='article__text__overview')
        overview_paragraphs = overview.find_all('span')
        overview_text = ''
        for paragraph in overview_paragraphs:
            overview_text += paragraph.text

        article_paragraphs = article.find_all('p')
        article_text = ''
        for paragraph in article_paragraphs:
            article_text += paragraph.text

        # Заполняем полученными данными news_data
        news_data[name]['link'] = link
        news_data[name]['date'] = date
        news_data[name]['overview'] = overview_text.replace('\xa0', '').replace('\n', '').replace('\r', '')
        news_data[name]['text'] = article_text.replace('\xa0', '').replace('\n', '').replace('\r', '')

        try:
            news_data[name]['title'] = title.text
        except AttributeError:
            news_data[name]['title'] = 'Без заголовка'
        try:
            news_data[name]['category'] = category.text.replace('\n', '')
        except AttributeError:
            news_data[name]['category'] = 'Без категории'
        try:
            news_data[name]['image'] = image.find('img').get('src')
        except AttributeError:
            news_data[name]['image'] = 'Без обложки'

    return news_data
    #     print(news_data)

    # for key, value in news_data.items():
    #     print("№" + str(list(news_data.keys()).index(key) + 1))
    #     print(value['link'], "\n", value['title'], "\n", value['category'], "\n", value['image'], "\n", value['date'],
    #           "\n", value['overview'], "\n")
    #     save_json(news_data)

# main()
