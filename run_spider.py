# better_run_spider.py
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def run_spider_blocking():
    process = CrawlerProcess(get_project_settings())
    
    # Replace 'tkh_all_clean' with your spider name
    process.crawl('tkh_all_clean')
    process.start()  # This blocks until spider finishes
