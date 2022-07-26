import httpx
import lxml.html
from pprint import pprint


def get_data():
    url = 'https://emojipedia.org/emoji/'
    res = httpx.get(url)
    tree = lxml.html.fromstring(res.text)
    data = [
        {
            "emoji": tr.xpath('./td[1]/a/span/text()')[0],
            "title": tr.xpath('./td[1]/a/text()')[0].strip(),
            "unicode_list": tr.xpath('./td[2]/text()')[0].split(', ')
        }
        for tr in tree.xpath(r'//table[@class="emoji-list"]/tr')
    ]
    return data


