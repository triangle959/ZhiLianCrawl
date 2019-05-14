#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# @Author   :triangle
# @Time     :2019/5/13 18:17
# @Filename :crawl.py
import csv
import json

import requests
import re
from pyquery import PyQuery as pq
from collections import OrderedDict


headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
}

def get_page(start, cityID, keyword):
    #url = "https://sou.zhaopin.com/?jl=765&kw=python&kt=3&sf=0&st=0"
    #调用api，接受四个参数，将pageSize设死，其余三个传参
    url = "https://fe-api.zhaopin.com/c/i/sou?pageSize=60&cityId={}&kw={}&kt=3&page=4&start={}".format(cityID,keyword,start)
    print(url)
    response = requests.get(url,headers=headers)
    url_list=[]
    if response.status_code == 200:
        j = json.loads(response.text)
        results = j.get('data').get('results')
        for job in results:
            url_list.append(job.get('positionURL'))
    print(url_list)
    return url_list


def get_parse(url):
    #返回信息在script>__INITIAL_STATE__>jobInfo>jobDetail,非xml形式用re
    # url = 'https://jobs.zhaopin.com/CC283432787J00286229307.htm'
    response = requests.get(url, headers=headers)
    html = response.text
    jobDetail = json.loads(re.search("\"jobDetail\":(.*?),\"jobPublisher", html).group(1))
    item = OrderedDict()
    #职位名
    item['name'] = jobDetail["detailedPosition"]["name"]
    #学历要求
    item['education'] = jobDetail["detailedPosition"]["education"]
    #工作年限
    item['workingExp'] = jobDetail["detailedPosition"]["workingExp"]
    #公司名
    item['companyName'] = jobDetail["detailedPosition"]["companyName"]
    #公司地址
    item['address'] = jobDetail["detailedPosition"]["workAddress"]
    #薪资
    item['salary'] = jobDetail["detailedPosition"]["salary60"]
    #职位描述 jobDesc里是html，利用pq匹配比正则匹配更好
    doc = pq(jobDetail["detailedPosition"]["jobDesc"].replace("&nbsp;",""))
    item['jobDetail'] = doc.text().replace("\n","")
    yield item

def save_csv(csv_filename,data):
    with open(csv_filename,'a+',newline='',encoding='utf-8') as f:
        f_csv = csv.DictWriter(f,data.keys())
        f_csv.writerow(data)

if __name__ == "__main__":
    cityName = input("请输入你要搜索的城市：")
    keyword = input("请输入你要搜索的职位关键字：")
    pageNum = input("请输入你要搜索的页数：")

    filename = keyword + '-' + cityName + '.csv'
    with open(filename,'a+',newline='',encoding='utf-8') as f:
        f_csv = csv.DictWriter(f,['职位名','学历要求','工作年限','公司名','公司地址','薪资','岗位描述'])
        f_csv.writeheader()

    for i in range(1,int(pageNum)*60+1,60):
        for url in get_page(i,cityName,keyword):
            item = get_parse(url)
            for data in item:
                save_csv(filename,data)
