# ParserMETRO
***
## Что это?
Парсер товаров в различных категориях на сайте 'https://online.metro-cc.ru/'. Способ использования подробно описан в файле [main.py](main.py).
## Принцип работы?
Принцип работы построен на отдельном парсинге каждого бренда в категории, что позволяет не парстить все страницы товаров, чтобы извлечь информацию о 
бренде, которой нет на странице просмотра товаров.
## Вывод результата?
После успешного парсинга, в папке 'result', создаётся файл с указаным при запуске названием, где находится
необходимая информация о товарах, которые есть в наличии. Также создаётся файл с приставкой 'sold_out_', в котором
собраны товары не в наличии.

### Примеры вывода результатов?
1. Результаты парсинга категории 'Свинина' в формате JSON.
    * [pork.json](pork.json)
    * [sold_out_pork.json](sold_out_pork.json)
2. Результаты парсинга категории 'Кофе' в формате CSV.
    * [coffee.csv](coffee.csv)
    * [sold_out_coffee.csv](sold_out_coffee.csv)

   **Указанный адрес доставки при парсинге** - *Москва, Кремлёвская набережная, 1с3*

