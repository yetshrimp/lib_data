# -*- coding: utf-8 -*-

import requests
import datetime
import time
import sys
import random
import socket
import json
import pandas as pd
import os

requests.packages.urllib3.disable_warnings()


class SeatScanner(object):

    def __init__(self, username='', password=''):
        self.login_url = 'https://seat.lib.whu.edu.cn:8443/rest/auth'  # 图书馆移动端登陆API
        self.usr_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/user'  # 用户信息API
        self.filters_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/free/filters'  # 分馆和区域信息API
        self.stats_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/room/stats2/'  # 单一分馆区域信息API（拼接buildingId）
        self.layout_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/room/layoutByDate/'  # 单一区域座位信息API（拼接roomId+date）
        self.search_url = 'https://seat.lib.whu.edu.cn:8443/rest/v2/searchSeats/'  # 空位检索API（拼接date+startTime+endTime）

        # 已预先爬取的roomId
        self.xt = ('6', '7', '8', '9', '10', '11', '12', '16', '4', '5', '14', '15')
        self.xt_lite = ('9', '11', '8', '10', '6', '7', '16')
        self.gt = ('19', '29', '31', '32', '33', '34', '35', '37', '38')
        self.yt = ('20', '21', '23', '24', '26', '27')
        self.zt = ('39', '40', '51', '52', '56', '59', '60', '61', '62', '65', '66')

        self.allSeats = {}  # 用于储存某区域的所有座位信息
        self.token = ''
        self.username = username
        self.password = password
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'User-Agent': 'doSingle/11 CFNetwork/893.14.2 Darwin/17.3.0',
                        'token': self.token}

        self.seatData = pd.DataFrame(columns=['seatId', 'date', 'hourSparse', 'minuteSparse',
                                              'building', 'room', 'seatName', 'seatStatus',
                                              'window', 'power', 'computer'])
        if os.path.exists('seatData.csv'):
            self.id = len(pd.read_csv('seatData.csv').index)
        else:
            self.id = 0

    # 暂停程序至指定时间，无返回值
    def Wait(self, time_run):
        while True:
            delta = time_run - datetime.datetime.now()
            if delta.total_seconds() <= 0:
                print('\n', end='')
                break
            print('\r等待下一次运行...剩余' + str(int(delta.total_seconds())) + '秒', end='    ')
            time.sleep(0.05)

    # 发起GET请求，用旧token换取新token（旧token通过移动端抓包获得，可以保存后多次使用）并构建Headers，成功则返回token字符串，否则返回False
    def GetToken(self):
        datas = {'username': self.username, 'password': self.password}
        # print('\nTry getting token...Status: ', end='')
        try:
            response = requests.get(self.login_url, params=datas, headers=self.headers, verify=False, timeout=5)
            # print(response.text)
            json = response.json()
            if json['status'] == 'success':
                self.token = json['data']['token']
                self.headers['token'] = self.token
                # print('token：' + json['data']['token'])
                return json['data']['token']
            else:
                # print(json['message'])
                return False
        except:
            # print('Connection lost')
            return False

    # 发起GET请求，获取当前某区域内的位置信息
    def GetSeats(self, roomId, buildingId, date, hour, minuteSparse, log1):
        url = self.layout_url + roomId + '/' + date
        # print('\nTry getting seat information...Status: ', end='')
        try:
            response = requests.get(url, headers=self.headers, verify=False, timeout=5)
            json = response.json()
            print('room' + roomId + ' ' + json['status'])
            if json['status'] == 'success':
                # print(json)
                for seat in json['data']['layout']:
                    if json['data']['layout'][seat]['type'] == 'seat':
                        self.id += 1
                        self.seatData.loc[self.id] = [str(json['data']['layout'][seat]['id']),
                                                      date, hour, minuteSparse, buildingId,
                                                      roomId, str(json['data']['layout'][seat]['name']),
                                                      str(json['data']['layout'][seat]['status']),
                                                      str(json['data']['layout'][seat]['window']),
                                                      str(json['data']['layout'][seat]['power']),
                                                      str(json['data']['layout'][seat]['computer'])]
                log1.logger.info('room' + roomId + ' ' + '座位信息获取成功')
                return True
            else:
                print('room' + roomId + ' ' + '座位信息获取失败')
                log1.logger.error('room' + roomId + ' ' + '座位信息获取失败')
                return False
        except:
            print('room' + roomId + ' ' + 'Connection lost')
            log1.logger.error('room' + roomId + ' ' + 'Connection lost')
        return False

