# import requests
# from bs4 import BeautifulSoup
# from rich.console import Console
# from rich.progress import track
# from rich.table import Table
#
#
# def check_url(url):
#     console = Console()
#     keywords = ['price', 'cost', 'product', 'model', 'manufacturer', 'image', 'src']
#     tasks = {'price': False, 'product_name': False, 'manufacturer': False, 'image_url': False}
#     product_details = {}
#
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#     except (requests.exceptions.HTTPError, requests.exceptions.RequestException):
#         console.print("The provided URL is invalid or not responding!", style="bold red")
#         return "Nothing"
#
#     soup = BeautifulSoup(response.text, 'html.parser')
#
#     for keyword in track(keywords, description="Processing..."):
#         for tag in soup.find_all(True):
#             if keyword in tag.name or keyword in str(tag.get('class')):
#                 if keyword in ['price', 'cost'] and 'price' not in product_details:
#                     product_details['price'] = tag.text.strip()
#                     tasks['price'] = True
#                 elif keyword in ['product', 'model'] and 'product_name' not in product_details:
#                     product_details['product_name'] = tag.text.strip()
#                     tasks['product_name'] = True
#                 elif keyword == 'manufacturer' and 'manufacturer' not in product_details:
#                     product_details['manufacturer'] = tag.text.strip()
#                     tasks['manufacturer'] = True
#                 elif keyword in ['image', 'src'] and 'image_url' not in product_details and 'http' in tag.get(keyword):
#                     product_details['image_url'] = tag.get(keyword)
#                     tasks['image_url'] = True
#
#         print_tasks(tasks)
#
#     if not product_details:
#         console.print("No product details found in the URL!", style="bold red")
#         return "Nothing"
#
#     console.print("Found product details:", style="bold green")
#     print_product_details(product_details)
#     return product_details
#
#
# def print_tasks(tasks):
#     console = Console()
#     table = Table(show_header=True, header_style="bold magenta")
#     table.add_column("Task")
#     table.add_column("Status")
#
#     for task, status in tasks.items():
#         if status:
#             table.add_row(task, "[green]Done[/green]")
#         else:
#             table.add_row(task, "[red]Not Done[/red]")
#     console.print(table)
#
#
# def print_product_details(details):
#     console = Console()
#     table = Table(show_header=True, header_style="bold magenta")
#     table.add_column("Detail")
#     table.add_column("Value")
#
#     for detail, value in details.items():
#         table.add_row(detail, value)
#     console.print(table)

# import httpx
# from bs4 import BeautifulSoup
#
#
# async def parse_url(url):
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
#     timeout = httpx.Timeout(10.0, connect=2.0)
#     try:
#         async with httpx.AsyncClient(timeout=timeout) as session:
#             response = await session.get(url, headers=headers)
#         response.raise_for_status()
#     except (httpx.RequestError, ValueError):
#         return "Nothing"
#
#     soup = BeautifulSoup(response.text, 'html.parser')
#
#     data = {}
#     data_keywords = {
#         "title": ["name", "title", "product"],
#         "model": ["model"],
#         "manufacturer": ["manufacturer", "brand"],
#         "image": ["image", "img"],
#         "price": ["price", "cost"]
#     }
#
#     for tag in soup.find_all():
#         for key, keywords in data_keywords.items():
#             if key not in data:
#                 for keyword in keywords:
#                     if keyword in tag.get('class', '') or keyword in tag.name:
#                         if key == "image" and tag.get('src'):
#                             data[key] = tag['src']
#                         else:
#                             data[key] = tag.text.strip()
#                         break
#     return data
#
#
# urls = ["https://www.adidas.com/us/nmd_r1-shoes/IF8029.html",
#         "https://myreact.ru/shop/jordan-1-low-black-toe/",
#         "https://street-beat.ru/d/krossovki-nike-dj6189-100/"]
#
#
# async def main():
#     tasks = (parse_url(url) for url in urls)
#     for result in await asyncio.gather(*tasks):
#         print(result)
#
#
# import asyncio
#
# asyncio.run(main())
start_urls = ["https://www.adidas.com/us/nmd_r1-shoes/IF8029.html",
              "https://myreact.ru/shop/jordan-1-low-black-toe/",
              "https://street-beat.ru/d/krossovki-nike-dj6189-100/"]

import scrapy
from scrapy.crawler import CrawlerProcess

class MySpider(scrapy.Spider):
    name = 'myspider'

    def parse(self, response):
        data = {}
        data_keywords = {
            "title": ["name", "title", "product"],
            "model": ["model"],
            "manufacturer": ["manufacturer", "brand"],
            "image": ["image", "img"],
            "price": ["price", "cost"]
        }

        for key, keywords in data_keywords.items():
            for keyword in keywords:
                if key not in data:
                    element = response.xpath(f'//*[contains(@class, "{keyword}") or name()="{keyword}"]')
                    if element:
                        if key == "image":
                            data[key] = element.xpath('./@src').get()
                        else:
                            text_content = element.xpath('./text()').get()
                            data[key] = text_content.strip() if text_content else None
                        break
        yield data

process = CrawlerProcess()
process.crawl(MySpider)
process.start() # the script will block here until the crawling is finished
