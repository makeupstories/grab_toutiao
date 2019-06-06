import time
from urllib.parse import urlencode, quote
import requests
from pymongo import MongoClient

offset = 0
client = MongoClient()
db = client['toutiao']
collection = db['toutiao']
timestamp = int(time.time() * 1000)

def get_url(keyword, offset):
    basic_url = "https://www.toutiao.com/api/search/content/?"
    params = {
        "aid": "24",
        "app_name": "web_search",
        "offset": offset,
        "format": "json",
        "keyword": keyword,
        "autoload": "true",
        "count": "20",
        "en_qc": "1",
        "cur_tab": "1",
        "from": "search_tab",
        "pd": "synthesis",
        "timestamp": timestamp
    }
    url = basic_url + urlencode(params)
    return url


def get_page(url, keyword):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        "referer": "https://www.toutiao.com/search/?keyword=" + quote(keyword),
        "cookie": "csrftoken=a215f543182d0357a665e3ecf0f6423d; tt_webid=6699070454386165255; UM_distinctid=16b2847a40359b-0de755c66f67b5-37647e03-1fa400-16b2847a4043d3; s_v_web_id=e2ddf73d91f53090cee9e1e2af2e14eb; __tasessionId=8t9vh39jg1559754932545; CNZZDATA1259612802=2020814729-1559746729-%7C1559752129",
        "x-requested-with": "XMLHttpRequest"
    }
    response = requests.get(url=url, headers=headers)
    try:
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e:
        print("Error", e.args)


def parse_page(json):
    if json:
        items = json.get('data')
        for item in items:
            toutiao = {}
            toutiao['id'] = item.get('id')
            toutiao['image_list'] = item.get('image_list')
            toutiao['source'] = item.get('source')
            toutiao['title'] = item.get('title')
            toutiao['detail_url'] = item.get('article_url')
            if item.get('title') is None:
                continue
            yield toutiao

def save_to_mongo(result):
    if collection.insert(result):
        print('Saved to Mongo')

if __name__ == '__main__':
    keyword = input("请输入你想搜索的内容：")
    for i in range(3):

        url = get_url(keyword, offset=0)
        json = get_page(url, keyword)
        results = parse_page(json)
        for result in results:
            print(result)
            save_to_mongo(result)

        offset += 20
        i += 1
