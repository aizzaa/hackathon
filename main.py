import requests
from bs4 import BeautifulSoup, Tag
from typing import List


url = 'https://kaktus.media/?lable=8'

def get_html(url: str) -> str:
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception('Сайт не отвечает')
    

def get_soup_from_html(html: str) -> BeautifulSoup:
    soup = BeautifulSoup(html, 'lxml')
    return soup


def get_tags_from_soup(soup: BeautifulSoup) -> List[Tag]:
    tags = soup.find_all('div', {'class': 'Tag--article'})
    return tags

def get_data_from_tags(tags: List[Tag]) -> List[dict]:
    data_list = []
    news_number = 0
    for tag in tags:
        try:
            image_element = tag.find('a', {'class': 'ArticleItem--image'})
            news_number += 1
            data ={
                'news_number': news_number,
                'title': tag.find('a', {'class': 'ArticleItem--name'}).text,
                'description': tag.find('a', {'class': 'ArticleItem--name'}).get('href'),
                'image': image_element.find('img').get('src'),
            }
            data_list.append(data)
        except Exception:
            data['title'] = 'Нет заголовка'
            data['description'] = 'Нет описания'
            data['image'] = 'Нет изображения'
    return data_list


def get_data_str(data_list: List[dict]) -> str:
    data_str_list = []
    for data in data_list:
        news_number = data['news_number']
        title = data['title']
        image = data['image']
        description = data['description']
        data_str = f"{news_number}. {title}\nОписание: {description}\nИзображение: {image}"
        data_str_list.append(data_str)
    data_result = '\n'.join(data_str_list)
    return data_result

    
def parse_info():
    html = get_html(url)
    soup = get_soup_from_html(html)
    tags = get_tags_from_soup(soup)
    data = get_data_from_tags(tags)

    str_data = get_data_str(data)
    return str_data

def main():
    str_data = parse_info()
    print(str_data)

if __name__ == '__main__':
    main()