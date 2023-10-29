from tools.object import BarData, TickData
from tools.constant import Interval, Exchange
from tools.k_tools import BarGenerator
from config.constant import Model
import backtrader as bt
import datetime as dt
import importlib

import os
import csv

from tools.method import read_json, save_json


# 二次封装的bt.Strategy
class DDStrategy(bt.Strategy):
    def __init__(self):
        # -------- 代码块内请勿修改！  代码块由此开始->
        self.record_ls = []

        # 保存本次回测的参数
        self.record_ls.append(['0', 0, 0])
        # 获取当前模型下的ArrayManager
        # 项目路径
        self.project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        conf_path = os.path.join(self.project_path, "config", "conf.json")
        conf: dict = read_json(conf_path)
        now_model = conf["now_model"]
        model_name = Model.MODEL_PRE.value + str(now_model)
        ArrayManager = importlib.import_module('.'.join([model_name, "factor", "factor_am"])).ArrayManager

        self.am_1m = ArrayManager(30)
        self.am_5m = ArrayManager(30)
        self.am_15m = ArrayManager(30)

        self.bg_1m = BarGenerator(self.on_bar, 1, self.on_1m_bar)
        self.bg_5m = BarGenerator(self.on_bar, 5, self.on_5m_bar)
        self.bg_15m = BarGenerator(self.on_bar, 15, self.on_15m_bar)
        # 初始化账户信息
        self.size = 0
        self.price = 0
        self.value = 0
        self.qty = 0

        # <-代码块至此结束 -----------------------

    def next(self):
        """
        主要用于将backtrader传递过来的最小周期数据进行收录，并转为ArrayManager类型的数据进行管理和调用
        将交易逻辑代码写入on_1m_bar执行效果等价于写入此函数
        """
        # -------- 代码块内请勿修改！  代码块由此开始->
        # 将本次接收的行情数据传入数组管理器和K线生成器
        # 然后写回调函数on_1m_bar on_5m_bar on_15m_bar
        # 将接收到的行情数据转为bar_data对象

        # 实例策略展示两只标的的策略，self.datas[0]和self.datas[1]
        # 两只标的，三种K线周期，共六个数组管理器
        symbol: str = '0000'
        exchange: Exchange = Exchange.DD
        datetime: dt.datetime = bt.num2date(self.data.datetime[0])

        interval: Interval = Interval.MINUTE
        volume: float = self.data.volume[0]
        turnover: float = 0
        open_interest: float = 0
        open_price: float = self.data.open[0]
        high_price: float = self.data.high[0]
        low_price: float = self.data.low[0]
        close_price: float = self.data.close[0]

        bar_data: BarData = BarData(symbol, exchange, datetime, interval, volume, turnover, open_interest, open_price, high_price, low_price, close_price)
        # 将bar_data装入k线生成器
        self.bg_1m.update_bar(bar_data)
        self.bg_5m.update_bar(bar_data)
        self.bg_15m.update_bar(bar_data)

        # <-代码块至此结束 -----------------------

    def on_bar(self, bar_data: BarData):
        """空的回调函数，占位，对于一分钟及以上周期的历史数据，该函数不会被触发"""
        pass

    def on_1m_bar(self, bar_data: BarData):
        """1m(或最小周期)K线数据生成回调函数"""
        # -------- 代码块内请勿修改！  代码块由此开始->
        # 将bar_data装入数组管理器
        self.am_1m.update_bar(bar_data)
        # 数据缓存不充分，结束
        if not self.am_1m.inited:
            return
        # 获取当前账户信息，仅在一分钟K线回调函数中获取
        self.size = self.position.size
        self.price = self.position.price
        self.value = self.broker.get_value()
        self.qty = self.value / self.am_1m.close[-1]
        # <-代码块至此结束 -----------------------

    def on_5m_bar(self, bar_data: BarData):
        """5mK线数据生成回调函数"""
        # -------- 代码块内请勿修改！  代码块由此开始->
        # 将bar_data装入数组管理器
        self.am_5m.update_bar(bar_data)
        # 数据缓存不充分，结束
        if not self.am_5m.inited:
            return
        # <-代码块至此结束 -----------------------

    def on_15m_bar(self, bar_data: BarData):
        """15mK线数据生成回调函数"""
        # -------- 代码块内请勿修改！  代码块由此开始->
        # 将bar_data装入数组管理器
        self.am_15m.update_bar(bar_data)
        # 数据缓存不充分，结束
        if not self.am_15m.inited:
            return
        # <-代码块至此结束 -----------------------

        pass

    def stop(self):
        """策略执行结束回调函数"""
        # -------- 代码块内请勿修改！  代码块由此开始->
        # 将本次回测的观测数据保存为csv文件，包含策略参数、现金、净值、收盘价、交易行为
        # 读取conf.json
        conf = read_json(os.path.join(self.project_path, 'config', 'conf.json'))
        result_dir_path = conf["result_dir_path"]
        # 设置record csv文件名
        # 用本次回测的参数进行命名
        csv_name = dt.datetime.strftime(dt.datetime.now(), "%m-%d %H_%M")
        # csv文件路径
        record_csv_path = os.path.join(result_dir_path, f"{csv_name}.csv")
        # record_ls写入csv
        with open(record_csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(self.record_ls)
        pass
        # <-代码块至此结束 -----------------------

    def notify_order(self, order):
        """订单状态改变回调函数"""
        # -------- 代码块内请勿修改！  代码块由此开始->
        # 记录买卖金额及数量，正为买，负为卖
        if order.status == 4:  # 4为Completed
            price = order.executed.pprice
            size = order.executed.psize
            self.record_ls.append(['2', price, size])
        # <-代码块至此结束 -----------------------
        pass

    def notify_trade(self, trade):
        """交易状态改变回调函数"""
        # -------- 代码块内请勿修改！  代码块由此开始->
        # 记录每笔交易
        self.record_ls.append(['3', 'Open' if trade.isopen else 'Close', trade.pnlcomm])
        # <-代码块至此结束 -----------------------
        pass

    def notify_cashvalue(self, cash, value):
        """单个行情节点处理完毕后，推送现金及净值数据"""
        # -------- 代码块内请勿修改！  代码块由此开始->
        # 接收现金、净值并记录
        self.record_ls.append(['1', cash, value, self.data.close[0],
                               bt.num2date(self.data.datetime[0]).strftime("%Y-%m-%d %H:%M")])
        # <-代码块至此结束 -----------------------
        pass
    