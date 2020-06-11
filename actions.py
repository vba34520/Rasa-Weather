# -*- coding: utf-8 -*-
# @Author  : XerCis
# @Time    : 2020/6/11 9:21
# @Function: Rasa自定义动作

from datetime import date
from weather import Weather
from rasa_sdk import Action, Tracker
from rasa_sdk.forms import FormAction
from typing import Any, Text, Dict, List
from dateutil.relativedelta import relativedelta
from rasa_sdk.executor import CollectingDispatcher

weather = Weather(verbose=1)


def parseWeekday(x: str) -> int:
    '''解析中文的周几'''
    TODAY = date.today()
    if x in ['今天', '今日', '第一天']:
        return TODAY
    if x in ['明天', '明日', '第二天', '一天后']:
        return TODAY + relativedelta(days=+1)
    if x in ['后天', '后日', '第三天', '二天后', '两天后']:
        return TODAY + relativedelta(days=+2)
    if x in ['大后天', '大后日', '第四天', '三天后']:
        return TODAY + relativedelta(days=+3)
    if x in ['大大后天', '大大后日', '第五天', '四天后']:
        return TODAY + relativedelta(days=+4)
    if x in ['大大大后天', '大大大后日', '第六天', '五天后']:
        return TODAY + relativedelta(days=+5)
    TIME = {
        1: ['1', '一'],
        2: ['2', '二'],
        3: ['3', '三'],
        4: ['4', '四'],
        5: ['5', '五'],
        6: ['6', '六'],
        7: ['7', '七', '日', '天']
    }
    weeks = None
    if x.startswith('上') or x.startswith('前'):
        weeks = -1
    if x.startswith('下') or x.startswith('后') or x.startswith('明'):
        weeks = 0

    count = 0
    for k, v in TIME.items():
        for i in v:
            if i in x:
                count += 1
                weekday = k

    if count != 1:
        return TODAY
    elif weeks == 0 or weeks == -1:
        return TODAY + relativedelta(weekday=weekday - 1, weeks=weeks)
    else:
        if TODAY.isoweekday() >= weekday:
            return TODAY + relativedelta(days=+1, weekday=weekday - 1, weeks=-1)
        else:
            return TODAY + relativedelta(days=+1, weekday=weekday - 1)


class ActionDebug(Action):
    def name(self) -> Text:
        return "action_debug"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        city = tracker.get_slot('city')
        time = tracker.get_slot('time')
        dispatcher.utter_message(text='{} {}'.format(city, time))
        return []


class CityTimeForm(FormAction):
    """自定义表单动作，填充所需插槽"""

    def name(self) -> Text:
        return "city_time_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["city", "time"]

    def slot_mappings(self) -> Dict[Text, Any]:
        """映射所需槽位"""
        return {
            "city": self.from_entity(entity="city"),
            "time": self.from_entity(entity="time")
        }

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any]
               ) -> List[Dict]:
        city = tracker.get_slot('city')
        time = tracker.get_slot('time')
        result = weather.getWeather(city=city)
        today = date.today()
        parse = parseWeekday(x=time)
        delta = relativedelta(parse, today).days
        index = delta + 1 if delta + 1 <= 5 else 1  # 获取五天内，否则获取今天
        dispatcher.utter_message(text='{} {} {}'.format(city, time, result['day{}'.format(index)]))
        return []
