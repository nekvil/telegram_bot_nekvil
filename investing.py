import logging
import requests
from bs4 import BeautifulSoup
import json


URL = 'https://ru.investing.com/news/cryptocurrency-news/'


def get_soup(url):
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
    return BeautifulSoup(r, 'html.parser')


def save_json(data):
    with open('investing_data.json', "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def main():
    news_data = {}
    soup = get_soup(URL)
    i = -1
    # Получаем все ссылки на новости
    news_links = soup.find('div', class_='largeTitle').find_all('a', {'class': ['title']})
    type_links = soup.find('div', class_='largeTitle').find_all('article', {'class': ['articleItem']})

    # Для каждой ссылки получаем информацию и записываем в news_data
    while len(news_data) < 10:

        i += 1

        investing = False
        forklog = False
        prime = False
        ihodl = False
        article = ""
        title = "Без заголовка"
        image = "Без обложки"
        date = "Без даты"
        category = "Без категории"

        link = news_links[i].get('href').split('?')[0]
        news_maker = type_links[i].get('data-provider-name')

        # print(news_maker)

        if "Forklog" == news_maker:
            forklog = True
        elif "ПРАЙМ" == news_maker:
            prime = True
        elif "ihodl" == news_maker:
            ihodl = True
        elif news_maker is None:
            investing = True
            link = "https://ru.investing.com" + news_links[i].get('href').split('?')[0]
        else:
            continue

        name = link
        news_data[name] = {}
        soup = get_soup(link)
        try:
            if investing:
                # Переходим на страницу для дальнейшенго парсинга
                article = soup.find('section', id='leftColumn')
                # category = article.find('a', class_='article__header__category')
                title = article.find('h1', class_='articleHeader')
                image = article.find('img', id='carouselImage').get('src')
                date = article.find('span').text
            elif forklog:
                # Переходим на страницу для дальнейшенго парсинга
                article = soup.find('div', class_='post_content')
                # category = article.find('a', class_='article__header__category')
                title = article.find('h1')
                image = article.find('img').get('src')
                date = article.find('span', class_='article_date').text
            elif prime:
                # Переходим на страницу для дальнейшенго парсинга
                article = soup.find('article', class_='article')
                # category = article.find('a', class_='article__header__category')
                title = article.find('div', class_='article-header__title')
                image = "https://1prime.ru" + article.find('img', class_='article-header__media-image_desktop').\
                    get('src')
                date = article.find('time', class_='article-header__datetime').text
            elif ihodl:
                # Переходим на страницу для дальнейшенго парсинга
                article = soup.find('section', class_='article-lt__main')
                # category = article.find('a', class_='article__header__category')
                title = article.find('h1', itemprop='name')
                date = article.find('div', class_='article__date').text
        except Exception as e:
            logging.exception(e)
            news_data.pop(name)
            continue

        article_paragraphs = article.find_all('p')
        article_text = ''
        for paragraph in article_paragraphs:
            article_text += paragraph.text

        # Заполняем полученными данными news_data
        news_data[name]['link'] = link
        news_data[name]['date'] = date
        news_data[name]['text'] = article_text.replace('\xa0', '').replace('\n', '').replace('\r', '')

        try:
            news_data[name]['title'] = title.text
        except AttributeError:
            news_data[name]['title'] = 'Без заголовка'
        # try:
        #     news_data[name]['category'] = category.text.replace('\n', '')
        # except AttributeError:
        #     news_data[name]['category'] = 'Без категории'
        try:
            news_data[name]['image'] = image
        except AttributeError:
            news_data[name]['image'] = 'Без обложки'

    return news_data
    #     print(news_data)

    # for key, value in news_data.items():
    #     print("№" + str(list(news_data.keys()).index(key) + 1))
    #     print(value['link'], "\n", value['title'], "\n", value['image'], "\n", value['date'],
    #           "\n", value['text'], "\n")
    #     save_json(news_data)

# main()
