# -*- coding: utf-8 -*-
# @Author  : XerCis
# @Time    : 2020/6/10 14:15
# @Function: 查询天气预报

import os
import json
from typing import List, Text
from suds.client import Client
from collections import defaultdict
from suds.xsd.doctor import ImportDoctor, Import


class Weather:
    def __init__(self, verbose: int = 0):
        '''初始化获取支持的地区、城市

        :param verbose: Integer. 0, or 1. Verbosity mode. 0 = silent, 1 = start and end.
        '''
        if verbose == 1:
            import time
            start = time.time()
            print('Building supported regions and cities ...')

        self.load()  # 读取

        if verbose == 1:
            end = time.time()
            print('Built succesfully. Cost {:.3f} seconds.'.format(end - start))

    def creat_client(self):
        '''创建suds.client对象'''
        imp = Import('http://www.w3.org/2001/XMLSchema', location='http://www.w3.org/2001/XMLSchema.xsd')
        imp.filter.add('http://WebXml.com.cn/')
        doctor = ImportDoctor(imp)
        self.client = Client('http://ws.webxml.com.cn/WebServices/WeatherWS.asmx?wsdl', doctor=doctor)

    def load(self, filepath='weather.json'):
        '''读取'''
        self.creat_client()

        # 加载JSON缓存
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                self.__dict__.update(json.load(f))
        else:
            self.REGION = {}  # 国家地区和省份
            native = self.client.service.getRegionProvince()  # 国内
            foreign = self.client.service.getRegionCountry()  # 国外
            for x in native[0]:
                region, _id = x.split(',')
                self.REGION[region] = _id
            for x in foreign[0]:
                region, _id = x.split(',')
                self.REGION[region] = _id

            self.CITY = {}  # 城市
            self.REGION_CITY = defaultdict(list)  # 地区支持的城市
            regions = list(self.REGION.keys())
            for region in regions:
                cities = self.client.service.getSupportCityString(theRegionCode=region)
                for x in cities[0]:
                    city, _id = x.split(',')
                    if city == '无城市':
                        del self.REGION[region]
                    else:
                        self.CITY[city] = _id
                        self.REGION_CITY[region].append(city)
            self.persist()  # 持久化

    def persist(self, filepath='weather.json'):
        '''持久化'''
        with open(filepath, 'w', encoding='utf-8') as f:
            data = self.__dict__.copy()
            del data['client']
            json.dump(data, f, ensure_ascii=False, indent=2)

    def getCity(self) -> List[Text]:
        '''获取所有支持的城市'''
        return list(self.CITY.keys())

    def getRegion(self) -> List[Text]:
        '''获取所有支持的地区'''
        return list(self.REGION.keys())

    def getRegionCity(self, region: str) -> List[Text]:
        '''获取地区支持的城市

        >>> Weather().getRegionCity(region='巴西')
        ['里约热内卢', '圣保罗']
        '''
        return self.REGION_CITY[region]

    def getWeather(self, city: str) -> List[Text]:
        '''获取城市天气'''
        result = {
            'city': city,
            'status': 0  # 失败
        }
        if city in self.CITY:
            weather = self.client.service.getWeather(theCityCode=city)
            weather = weather[0]
            result = {
                'city': weather[0],  # 城市
                'reporttime': weather[3],  # 时间
                'live': weather[4],  # 实况
                'brief': weather[5],  # 紫外线和空气质量
                'index': weather[6],  # 各种指数
                'today': ' '.join(weather[7:10]),  # 今天天气
                'tomorrow': ' '.join(weather[12:15]),  # 明天天气
                'day1': ' '.join(weather[7:10]),  # 今天天气
                'day2': ' '.join(weather[12:15]),  # 明天天气
                'day3': ' '.join(weather[17:20]),  # 后天天气
                'day4': ' '.join(weather[22:25]),  # 大后天天气
                'day5': ' '.join(weather[27:30]),  # 大后天天气
            }
        return result


if __name__ == '__main__':
    weather = Weather(verbose=1)
    region = weather.getRegion()  # 支持的所有地区
    cities = weather.getCity()  # 支持的所有城市
    support = weather.getRegionCity(region='巴西')  # 支持的巴西的城市
    result = weather.getWeather(city='广州')  # 查询广州的天气
    print('支持的地区数', len(region))
    print('支持的城市数', len(cities))
    print('支持的巴西城市', support)
    print('广州的天气', result)
