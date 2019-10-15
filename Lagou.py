import pymongo
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from pyquery import PyQuery as pq
from config import *
from urllib.parse import quote
import time


MONGO_URL = 'localhost'
MONGO_DB = 'lagou'
MONGO_COLLECTION = 'work'

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]


# browser = webdriver.Chrome()
# browser = webdriver.PhantomJS(service_args=SERVICE_ARGS)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(chrome_options=chrome_options)

wait = WebDriverWait(browser, 10)



def index_page():
    url = 'https://www.lagou.com'
    browser.get(url)
    City = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#changeCityBox > ul > li:nth-child(2) > a')))
    City.click()
    input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#search_input')))
    submit = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#search_button')))
    input.clear()
    input.send_keys('python')
    submit.click()
    time.sleep(2)
    get_work()


def get_work():
    html = browser.page_source
    doc = pq(html)
    items = doc('#s_position_list > ul > li.con_list_item').items()
    for item in items:
        work = {
            'position': item.find('div.list_item_top > div.position > div.p_top > a > h3').text(),
            'company': item.find('div.list_item_top > div.company > div.company_name > a').text(),
            'money': item.find('div.list_item_top > div.position > div.p_bot > div > span').text(),
            'work_required': item.find('div.list_item_top > div.position > div.p_bot > div').text(),
            'industry': item.find('div.list_item_top > div.company > div.industry').text(),
            'tag': item.find('div.list_item_bot > div.li_b_l').text()
        }
        print(work)
        save_to_mongo(work)
        
def next_page():
    next_page = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#s_position_list > div.item_con_pager > div > span.pager_next')))
    next_page.click()
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#s_position_list > div.item_con_pager > div > span.pager_next')))
    get_work()

def save_to_mongo(result):
    try:
        if db[MONGO_COLLECTION].insert(result):
            print('存储到MongoDB成功')
    except Exception:
        print('存储到MongoDB失败')    

def main():
    index_page()
    for i in range(0, 29):
        next_page()
        time.sleep(2)
    browser.close()


main()




