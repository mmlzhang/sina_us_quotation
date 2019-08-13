import time
import re
import json
import datetime
import csv
import traceback

import requests

from dingtalk import send_dingding, Colors


CSV_DELIMITER = "\t"

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

keys = ['symbol', 'market', 'name', 'cname', 'category', 'category_id', 'open', 'preclose',  'price', 'low', 'high',
        'volume', 'mktcap', 'chg', 'diff', 'pe', 'amplitude', "date"]
"""
category=行业板块
volume=成交量
mktcap=市值
chg=涨跌幅
diff=涨跌额
pe=市盈率
amplitude=振幅
"""

log_file = "log.log"


def write_file(data, header=False):
    mode = "a" if not header else "w"
    filename = "./data/{}.csv".format(datetime.datetime.utcnow().strftime("%Y-%m-%d"))
    with open(filename, mode, encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=CSV_DELIMITER)
        if header:
            writer.writerow(data)
        else:
            writer.writerows(data)


def handler_data(data_dict):
    data = data_dict.get("data")
    result = []
    for item in data:
        d = []
        for key in keys[:-1]:
            d.append(item.get(key))
        d.append(datetime.datetime.now().strftime(DATE_FORMAT))
        result.append(d)
    write_file(result)


def quotation_us_sina():
    page = 0
    per_page = 60
    # 美股开始时间: 北京时间22:30到次日5:00
    # 美股开始时间: utc时间14:30到21:00  夏天为 20:00
    while True:
        try:
            page += 1
            u = "http://stock.finance.sina.com.cn/usstock/api/jsonp.php/IO.XSRV2.CallbackList['18LBE3q_rMW3lVH$']/" \
                "US_CategoryService.getList?page={}&num={}&sort=&asc=0&market=&id="
            url = u.format(page, per_page)

            resp = requests.get(url)
            data = re.findall("\({(.*?)}\)", resp.text)[0]
            data_dict = json.loads("{" + data + "}")
            handler_data(data_dict)
            print("page: {}, per_page: {}, data: {}".format(page, len(data_dict.get("data")), data_dict))

            total_page = int(data_dict.get("count")) // per_page + 1
            if page >= total_page:
                break
        except Exception:
            err = str(traceback.format_exc())
            # send_dingding(title="US-Quotaion error", text=err)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(err)


def main():
    write_file(data=keys, header=True)
    # 美股开始时间: 北京时间22:30到次日5:00
    # 美股开始时间: utc时间14:30到21:00  夏天为 20:00
    while True:
        if datetime.datetime.utcnow().hour > 14 and \
                datetime.datetime.utcnow().hour < 21:
            # send_dingding(title="开市了!", text="", color=Colors.INFO)
            quotation_us_sina()
            # time.sleep(2)
        else:
            send_dingding(title="休市时间", text=str(datetime.datetime.utcnow().strftime(DATE_FORMAT)),
                          color=Colors.WARNING)
            time.sleep(60 * 60)


if __name__ == '__main__':
    main()
