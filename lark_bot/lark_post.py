"""
HTTP POST request to Lark Webhook API
"""

import os
import json
import datetime
import time
import hashlib
import base64
import hmac
import requests

def gen_sign(timestamp, secret):
    # 拼接timestamp和secret
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
    
    # 对结果进行base64处理
    sign = base64.b64encode(hmac_code).decode('utf-8')
    
    return sign

def post_to_lark_webhook(tag: str, papers: list, config: dict):
    headers = {
        'Content-Type': 'application/json'
    }

    # Card Template Data
    today_date = datetime.date.today().strftime('%Y-%m-%d')
    table_rows = [
        {
            "index": i + 1,
            "title": paper['title'],
            "id": paper['id'],
            "published": today_date,
            "url": f"[{paper['pdf']}]({paper['pdf']})"
        }
        for i, paper in enumerate(papers)
    ]
    paper_list = [
        {
            "counter": i + 1,
            "title": paper['title'],
            "id": paper['id'],
            "abstract": paper['summary'],
            "zh_abstract": paper.get('zh_summary', None),
            "published": today_date,
            "url": paper['pdf'],
        }
        for i, paper in enumerate(papers)
    ]

    card_data = {
        "type": "template",
        "data": {
            "template_id": config['template_id'],
            "template_version_name": config['template_version_name'],
            "template_variable": {
                "today_date": today_date,
                "tag": tag,
                "total_paper": len(papers),
                "table_rows": table_rows,
                "paper_list": paper_list
            }
        }
    }

    data = {
        "msg_type": "interactive",
        "card": card_data
    }

    # Add signature if secret is provided
    if config.get('webhook_secret'):
        timestamp = str(int(time.time()))
        sign = gen_sign(timestamp, config['webhook_secret'])
        data['timestamp'] = timestamp
        data['sign'] = sign

    # Send HTTP POST request
    response = requests.post(config['webhook_url'], headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print("Request successful")
        print("Response:\n{}".format(response.json()))
    else:
        print("Request failed, status code: {}".format(response.status_code))
        print("Response:\n{}".format(response.text))


if __name__ == '__main__':
    papers = [
        {
            'title': 'Title 1',
            'id': '1234567890',
            'summary': 'Abstract 1',
            'pdf': 'https://arxiv.org/abs/1234567890',
            'published': '2021-01-01',
            'zh_summary': None
        },
        {
            'title': 'Title 2',
            'id': '2345678901',
            'summary': 'Abstract 2',
            'pdf': 'https://arxiv.org/abs/2345678901',
            'published': '2021-01-02',
            'zh_summary': '中文摘要 2'
        }
    ]
    from utils import load_config
    config = load_config()
    post_to_lark_webhook('test', papers, config)
