# -*- coding: utf-8 -*-
import scrapy, os, re, csv, json, datetime
from tickets.items import TicketsItem

class TrainSpider(scrapy.Spider):
    name = 'train'
    allowed_domains = ['12306.cn']
    # 出发时间
    # train_data = datetime.datetime.now().strftime('%Y-%m-%d')
    train_data = '2019-01-24'
    # 出发站
    from_station = '广州'
    # 到达站
    to_station = '湛江西'
    # 抓取接口链接
    start_urls = ['https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9018']

    def parse(self, response):
        # 获取城市编码
        if not os.path.exists('stations.json'):
            text = response.body.decode('utf-8')
            content = re.match('.+?(@.+)', text)
            if content:
                # 获取所有车站信息
                text = content.group(1)
                # 进行清洗后写入json文件
                l = text.split('|')
                a, b = 1, 2
                stations = {}
                search = {}
                while b < len(l):
                    stations[l[a]] = l[b]
                    search[l[b]] = l[a]
                    a += 5
                    b += 5
                stations = json.dumps(stations, ensure_ascii = False)
                with open('stations.json', 'w', encoding='utf-8') as f:
                    f.write(stations)
                search = json.dumps(search, ensure_ascii = False)
                with open('search.json', 'w', encoding='utf-8') as f:
                    f.write(search)
            else:
                (response.body.decode())
        # 抓取数据
        if os.path.exists('stations.json'):
            with open('stations.json', 'rb') as f:
                station = json.load(f)
                query_url = 'https://kyfw.12306.cn/otn/leftTicket/queryA?' \
                            'leftTicketDTO.train_date={}&' \
                            'leftTicketDTO.from_station={}&' \
                            'leftTicketDTO.to_station={}&' \
                            'purpose_codes=ADULT'.format(self.train_data, station[self.from_station], station[self.to_station])
                yield scrapy.Request(query_url, callback = self.query_parse)
        pass

    def query_parse(self, response):
        # 解析查询结果
        text = response.body.decode('utf-8')
        message_fields = ['车次', '始发站', '终点站', '出发站', '到达站', '出发时间', '到达时间', '历时', '特等座', '一等座', '二等座', '软卧', '硬卧', '硬座', '无座', '备注']
        csvName = self.train_data + '.csv'
        writer = csv.writer(open(csvName, 'w'))
        writer.writerow(message_fields)
        infos = json.loads(text)['data']['result']
        with open('search.json', 'rb') as f:
            search = json.load(f)
        for info in infos:
            orgInfo = info.split('|')
            remark = orgInfo[1]
            info = orgInfo[3:]
            # if info[8] == 'N':
            #     continue
            row = [info[0], search[info[1]], search[info[2]], search[info[3]], search[info[4]], info[5], info[6], info[7], info[29], info[28], info[27], info[20], info[25], info[26], info[23], remark]
            writer.writerow(row)
        pass