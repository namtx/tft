import os
import scrapy
from thefuzz import process
from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image
from io import BytesIO
import base64

class ChampionsSpider(scrapy.Spider):
    name = "champions"
    allowed_domains = ["lolchess.gg"]
    start_urls = ["https://lolchess.gg/champions/set9.5/poppy"]

    def parse(self, response):
        self.logger.info(self.name)
        champions = response.css('.guide-champion-list .guide-champion-list__item').xpath('@data-keyword').getall()
        matched = process.extractOne(self.name, champions)

        if matched:
            driver = webdriver.Edge()
            driver.get(f'https://lolchess.gg/champions/set9.5/{matched[0]}')
            champion_name = driver.find_element(By.CSS_SELECTOR, '.guide-champion-detail__name').text
            self.logger.info(champion_name)
            items_table = driver.find_element(By.CSS_SELECTOR, '.table.guide-champion-detail__recommend-items__pair-items-table')
            items_image = Image.open(BytesIO(base64.b64decode(items_table.screenshot_as_base64)))
            driver.get('https://lolchess.gg/meta')
            comps = driver.find_elements(By.CSS_SELECTOR, '.guide-meta__deck-box')

            images = []
            total_h = items_image.size[1]
            total_w = 0
            for comp in comps:
                if champion_name in comp.text:
                    base64_encoded_screenshot = comp.screenshot_as_base64
                    image = Image.open(BytesIO(base64.b64decode(base64_encoded_screenshot)))
                    total_h = total_h + image.size[1]
                    if (image.size[0] > total_w):
                        total_w = image.size[0]
                    images.append(image)

            comps_image = Image.new('RGB', (total_w, total_h))
            comps_image.paste(items_image, (0, 0))

            y = items_image.size[1]
            for image in images:
                comps_image.paste(image, (0, y))
                y = y + image.size[1]

            comps_image.save(f'{self.name}.png')

            os.system(f'open ./{self.name}.png')

