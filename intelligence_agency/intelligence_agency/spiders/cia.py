import scrapy
import os

class SpiderCia(scrapy.Spider):

    if os.path.exists('cia.json'):
        os.remove('cia.json')

    name = 'cia'
    start_urls = [
        'https://www.cia.gov/readingroom/historical-collections'
    ]

    custom_settings= {
        'FEEDS':{'cia.json':
            {'format':'json',
            'encoding':'utf8',
            'store_empty': False,
            'fields': None,
            'indent': 4,
            'item_export_kwargs':{'export_empty_fields': True}}
        }
    }


    def parse(self, response):

        links_declassified = response.xpath('//a[starts-with(@href, "collection") and (parent::h3|parent::h2)]/@href').getall()

        for link in links_declassified:
            yield response.follow(link, callback=self.parse_link, cb_kwargs={'url':response.urljoin(link),'links':[]})


    def parse_link(self, response, **kwargs):
        
        link = kwargs['url']
        
        documents_links = response.xpath('//span[@class="file"]/a/@href').getall()
        next_button = response.xpath('//li[@class="pager-next"]/a/@href').get()
        documents_links.extend(kwargs['links'])

        if next_button:

            yield response.follow(next_button, callback=self.parse_link, cb_kwargs={'url':link, 'links':documents_links})

        else:
            title = response.xpath('//h1[@class="documentFirstHeading"]/text()').get()
            body = response.xpath('//div[@class="field-item even"]/p[not(@class) and not(@style)]//text()').getall()
            body = '\n'.join(body)
            
            yield {
                'link': link,
                'title': title,
                'body': body,
                'related documents links': documents_links
            }