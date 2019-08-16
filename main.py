# -*- coding: utf-8 -*-

import pandas as pd
import SeatScanner
import Data_save
import Logger
import datetime
import os

auto = 1  # 标记：自动设置数据或命令行设置数据，1为自动

log1 = Logger.Logger(filename='debug.log', level='warning')


def getMinuteSparse(minute):  # 将分钟转化为间隔编号
    if 0 <= minute and minute < 15:
        return 0
    elif minute >= 15 and minute < 30:
        return 1
    elif minute >= 30 and minute < 45:
        return 2
    elif minute >= 45 and minute <= 59:
        return 3
    else:
        log1.logger.error('获取时间有误')
        return False


def getData(num):  # 从表中读取用户名和密码
    try:
        logData = pd.read_excel('logIn.xlsx', header=0, index_col=None)
        _username = str(logData.loc[num]['username'])
        _password = str(logData.loc[num]['password'])
        log1.logger.info('用户名：' + _username + '    密码: ' + _password)
        return _username, _password
    except:
        log1.logger.error('用户名和密码读取失败')
        return False


def getToken(SS):
    for _ in range(100):
        if SS.GetToken():
            print('获取新token成功')
            log1.logger.info('获取新token成功')
            return True
    print('获取新token失败')
    log1.logger.error('获取新token失败')
    return False


def getDateStr():  # 设置开始时间，默认为即刻开始
    t = datetime.datetime.now()
    if auto:
        return t
    else:
        dateStr = input("请输入开始运行的时间：（格式如 2019-8-5 18:27:00, 且':'为英文字符）")
        if dateStr < str(t):
            print("开始时间有误,设置为即刻开始")
            log1.logger.warning('开始时间有误,设置为即刻开始')
            return t
        else:
            return datetime.datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S")


def getBuildingId():  # 设置要扫描的分馆编号，默认为全部扫描
    if auto:
        buildingId = '1234'
    else:
        buildingId = input('\n请选择要扫描的分馆编号，如\'123\'或\'24\'等 （1.信息科学分馆 2.工学分馆 3.医学分馆 4.总馆）：')
    log1.logger.info('扫描分馆编号：' + buildingId)
    return buildingId


# # 判断当前时间是否为零点
# def endDay(startTime):
#     dt = startTime.strftime("%H:%M:%S")
#     b = []
#     for a in dt.split(':'):
#         b.append(a)
#     c = ''.join(b)
#     if c == '183200':
#         return True
#     else:
#         return False


if __name__ == '__main__':
    startTime = getDateStr()
    rooms = []
    num = 1
    allRoom = 0
    successRoom = 0
    buildingId = getBuildingId()

    logData = pd.read_excel('logIn.xlsx')
    length = len(logData.index)

    while True:
        allRoom = 0
        successRoom = 0

        username, password = getData(++num % length)  # 循环登陆表中用户，防止被封号
        print(username)
        SS = SeatScanner.SeatScanner(username, password)
        getToken(SS)
        SS.Wait(startTime)

        date = startTime.strftime("%Y-%m-%d")
        hour = startTime.hour
        minute = startTime.minute
        minuteSparse = getMinuteSparse(int(minute))

        for building in list(buildingId):
            if building == '1':
                rooms = SS.xt
            elif building == '2':
                rooms = SS.gt
            elif building == '3':
                rooms = SS.yt
            elif building == '4':
                rooms = SS.zt
            else:
                # print('分馆编号输入不合法')
                continue

            for room in rooms:
                allRoom += 1
                if SS.GetSeats(room, building, str(date), hour, minuteSparse, log1):
                    successRoom += 1

        with open('temData.txt', 'a') as f:  # 将每次扫描结果写入临时文件
            f.write('startTime:' + startTime.strftime("%Y-%m-%d %H:%M:%S") + ' allRoom:' + str(allRoom) +
                    ' successRoom:' + str(successRoom) + ' failRoom:' + str(allRoom - successRoom) + '\n')

        print(SS.seatData[:20])

        # 将所爬取的数据存入数据库
        DS = Data_save.DataSaver()
        DS.save(SS.seatData)

        # SS.seatData.to_csv('seatData.csv', mode='a', header=not os.path.exists('seatData.csv'))
        startTime += datetime.timedelta(minutes=15)
