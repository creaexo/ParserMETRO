"""
    Парсер товаров в различных категориях на сайте 'https://online.metro-cc.ru/'. Принцип работы построен на отдельном
    парсинге каждого бренда в категории, что позволяет не парстить все страницы товаров, чтобы извлечь информацию о 
    бренде, которой нет на странице просмотра товаров.
    После успешного парсинга, в папке 'result', создаётся файл с указаным при запуске названием, где находится
    необходимая информация о товарах, которые есть в наличии. Также создаётся файл с приставкой 'sold_out_', в котором
    собраны товары не в наличии.
"""""

import datetime
import json
import os
import requests
from bs4 import BeautifulSoup as BS
# Словарь с названиями городов и их значениями в cookies сайта
CITIES = {
    'Moscow': '356',
    'Saint_Petersburg': '16'
}


def start_parsing(city: str, url: str, url_attributes: str or int, file_format: str, filename: str,
                  csv_separator: str = ';', save_html: bool = True):
    """

    :param city: Значение города в cookies сайта. Собраны в CITIES.
    :type city: Str.
    :param url: Ссылка на категорию, которую нужно парсить.
    :type url: Str.
    :param url_attributes: Чтобы получить это значение, нужно перейти на страницу категории, выбрать любой
    бренд в фильтре товаров и скопировать число из адресной строки, идущее после attributes=. Пример:
    https://online.metro-cc.ru/category/myasnye/myaso/svinina?from=under_search&attributes=1710012482%3A12482-cr-metro-chef
    url_attributes=1710012482
    :type url_attributes: Str or Int.
    :param file_format: Желаемый формат файла, в который запишется результат
    :type file_format: Str.
    :param filename: Название файла с результатом. Этим же названием назовётся папка с html страницами
    :type filename: Str.
    :param csv_separator: Каким символом будут разделены данные в csv
    :type csv_separator: Str.
    :param save_html: True - Сохранятся все скачанные для парсинга страницы, False - будут удалены
    :type save_html: Bool.
    :return:
    """
    if not os.path.exists(filename):
        os.mkdir('result')
        print('Создана папка result')
    if not os.path.exists(filename):
        os.mkdir(filename)
        print('Создана папка для хранения выгруженных страниц')

    if '?' in url:
        get_params = '&'
    else:
        get_params = '?'

    if file_format == 'csv':
        with open(f'result/{filename}.{file_format}', 'w', encoding='utf-8') as file:
            file.write(f'id{csv_separator}title{csv_separator}link{csv_separator}regular_price{csv_separator}'
                       f'promotional_price{csv_separator}brand')
        with open(f'result/sold_out_{filename}.{file_format}', 'w', encoding='utf-8') as file:
            file.write(f'id{csv_separator}title{csv_separator}link{csv_separator}brand')
    elif file_format != 'json':
        file_format = 'json'
        print('Не указан корректный формат файла. Результат будет выведен в json.')
    json_list = []
    json_sold_list = []
    time_start = datetime.datetime.now()

    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.686 YaBrowser/23.9.5.686 Yowser/2.5 Safari/537.36"
    }
    cookies = {'metroStoreId': city}
    req = requests.get(url=url, headers=headers, cookies=cookies)

    src = req.text

    with open(f'{filename}/index.html', 'w', encoding='utf-8') as file:
        file.write(src)
    with open(f'{filename}/index.html', encoding='utf-8') as file:
        src = file.read()

    soup = BS(src, "lxml")

    brands = soup.find('div', {'data-filter-group': 'Бренд'})

    brands_divs = brands.find_all('div', class_='catalog-checkbox-group__item')
    i = 0
    for brand in brands_divs:
        brand_slug = brand.get('data-filter-slug')
        brand_name = brand.text.strip()
        req = requests.get(url=url+f'{get_params}attributes={url_attributes}%3A{brand_slug}', headers=headers,
                           cookies=cookies)
        with open(f'{filename}/{brand_name}.html', 'w', encoding='utf-8') as file:
            file.write(req.text)
        with open(f'{filename}/{brand_name}.html', encoding='utf-8') as file:
            page = file.read()
        soup = BS(page, "lxml")

        products_inner = soup.find('div', {'id': 'products-inner'})
        pagination = soup.find('ul', {'class': 'catalog-paginate v-pagination'})
        if pagination is not None:
            pages = pagination.find_all('li')
            pages_list = []
            for page in pages:
                if page.text != '':
                    pages_list.append(page.text)
        else:
            pages_list = ['1']
        for page in pages_list:
            print('***************')
            print('Страница - ' + page)
            print('***************')
            first_page = True
            if page != '1':
                first_page = False
                req = requests.get(url=url + f'{get_params}attributes={url_attributes}%3A{brand_slug}' + f'&page={page}',
                                   headers=headers, cookies=cookies)
                src = req.text
                with open(f'{filename}/{brand_name}_p_{page}.html', 'w', encoding='utf-8') as file:
                    file.write(src)
                with open(f'{filename}/{brand_name}_p_{page}.html', encoding='utf-8') as file:
                    src = file.read()

                soup = BS(src, "lxml")

                products_inner = soup.find('div', {'id': 'products-inner'})
            products = products_inner.find_all('div', {'data-sku': True})
            for product in products:
                i += 1
                print(i)
                print('------------------')
                product_id = product.get('data-sku')
                print(f'id - {product_id}')
                product_href = ('https://online.metro-cc.ru' +
                                product.findChild("a", attrs={'class': 'product-card-photo__link'},
                                                  recursive=True).get('href'))
                print(f'ссылка - {product_href}')
                product_name = product.findChild("span", attrs={'class': 'product-card-name__text'},
                                                 recursive=True).text.strip()
                print(f'Имя - {product_name}')
                old_price = product.findChild("div", attrs={'class': 'product-unit-prices__old-wrapper'},
                                              recursive=True)
                promotional_price = product.findChild("div", attrs={'class': 'product-unit-prices__actual-wrapper'},
                                                      recursive=True)
                if old_price is not None:
                    old_price = old_price.findChild("span", attrs={'class': 'product-price__sum-rubles'},
                                                    recursive=True)
                    if old_price is not None:
                        old_price = old_price.text.strip()
                if promotional_price is not None:
                    promotional_price = promotional_price.findChild("span", attrs={'class': 'product-price__sum-rubles'},
                                                                    recursive=True).text.strip()
                else:
                    if file_format == 'csv':
                        promotional_price = ''
                    else:
                        promotional_price = 'null'
                if (promotional_price != '' or promotional_price != 'null') and old_price:
                    print(f'Цена по скидке - {promotional_price}')
                    print(f'Старая цена - {old_price}')
                elif (promotional_price == '' or promotional_price == 'null') and old_price is None:
                    if file_format == 'csv':
                        with open(f'result/sold_out_{filename}.{file_format}', 'a+', encoding='utf-8') as file:
                            file.write(
                                f'\n{product_id}{csv_separator}{product_name}{csv_separator}{product_href}{csv_separator}'
                                f'{brand_name}')
                    else:
                        json_sold_list.append(
                            {
                                "id": product_id,
                                "title": product_name,
                                "link": product_href,
                                "brand": brand_name
                            }
                        )
                    continue
                else:
                    old_price = promotional_price
                old_price = old_price.replace(' ', '')
                promotional_price = promotional_price.replace(' ','')
                print(f'Бренд - {brand_name}')
                if file_format == 'csv':
                    with open(f'result/{filename}.{file_format}', 'a+', encoding='utf-8') as file:
                        file.write(
                            f'\n{product_id}{csv_separator}{product_name}{csv_separator}{product_href}{csv_separator}'
                            f'{old_price}{csv_separator}'
                            f'{promotional_price}{csv_separator}{brand_name}')
                else:
                    json_list.append(
                        {
                            "id": product_id,
                            "title": product_name,
                            "link": product_href,
                            "regular_price": old_price,
                            "promotional_price": promotional_price,
                            "brand": brand_name
                        }
                    )
                print('------------------')
            if not save_html:
                if first_page:
                    os.remove(f'{filename}/{brand_name}.html')
                else:
                    os.remove(f'{filename}/{brand_name}_p_{page}.html')
    if file_format == 'json':
        with open(f'result/{filename}.{file_format}', 'a', encoding='utf-8') as file:
            json.dump(json_list, file, indent=4, ensure_ascii=False)
        with open(f'result/sold_out_{filename}.{file_format}', 'a', encoding='utf-8') as file:
            json.dump(json_sold_list, file, indent=4, ensure_ascii=False)

    if not save_html:
        # Удаление html страницы
        os.remove(f'{filename}/index.html')
        os.rmdir(filename)
    print(f'Парсинг продлился - {str(datetime.datetime.now()-time_start)}')


if __name__ == '__main__':
    start_parsing(CITIES['Moscow'], url='https://online.metro-cc.ru/category/chaj-kofe-kakao/kofe',
                  url_attributes='', file_format='csv', filename='', csv_separator=';', save_html=False)