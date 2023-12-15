import scrapy
import json
import urllib.parse

class FestoSpider(scrapy.Spider):
    """
    Spider to scrape product information from Festo website.
    """ 

    name = "festo"
    allowed_domains = ["festo.com"]
    start_urls = ["https://www.festo.com/gb/en/search/categories/pim380/products/"]

    def parse(self, response):
        """
        Parse the main page and initiate requests for product details.
        """
        # Assuming response is JSON
        script = json.loads(response.text)
        
        for product in script.get('productList', []):
            url = product.get('url')
            if url:
                yield scrapy.Request(url, callback=self.parse_info, dont_filter=True)

    def parse_info(self, response):
        """
        Parse product details page and yield product information.
        """
        product_name = response.xpath('//h1[@id="main-headline"]/text()').get().strip()
        description = response.xpath('//div[@class="copytext promo-text product-summary__promo-text"]/text()').get().strip()

        # Extracting text content from <li> items
        li_elements = response.xpath('//ul[@class="text-list product-summary__list"]/li')
        items = [li.xpath('normalize-space(.//span/text())').get().strip() for li in li_elements]

        # Extracting PDF link
        pdf_data = response.xpath('//div[@class="jsx-download-dropdown"]/@data-documents').get()
        try:
            if pdf_data:
                pdf_link = json.loads(pdf_data)[0].get('link').strip()
                if pdf_link:
                    # Construct the complete PDF link
                    base_url = response.urljoin('/')
                    complete_pdf_link = urllib.parse.urljoin(base_url, pdf_link)

                    # Yielding the items
                    yield {
                        'product_name': product_name,
                        'description': description,
                        'items': items,
                        'pdf_link': complete_pdf_link
                    }
        except (json.JSONDecodeError, IndexError, TypeError) as e:
            self.log(f"Error parsing JSON data or extracting PDF link: {e}")

    # Specify the output file with the FEEDS setting
    custom_settings = {
        'FEEDS': {
            'scrapy_festo.json': {
                'format': 'json',
                'indent': 4,  # Set the indentation to 4 spaces
                'overwrite': True,  # Overwrite the file if it already exists
            },
        },
    }