import backtrader as bt
from tools.object import BarData
from tools.core import DDStrategy
import datetime as dt

from tools.method import dt_str


class DefaultStrategy(DDStrategy):
    param = (
        ("p1", 5),
        ("p2", 10)
    )

    def __init__(self):
        super().__init__()  # 继承父类方法的内容，勿删
        # 存储已经回测过的月份，用来显示进度
        self.completed_month = []

        print(f"{dt_str()}策略__init__方法执行完成")

    def next(self):
        """
        主要用于将backtrader传递过来的最小周期数据进行收录，并转为ArrayManager类型的数据进行管理和调用
        将交易逻辑代码写入on_1m_bar执行效果等价于写入此函数
        """
        super().next()  # 继承父类方法的内容，勿删

        pass

    def on_bar(self, bar_data: BarData):
        """空的回调函数，占位，对于一分钟及以上周期的历史数据，该函数不会被触发"""
        super().on_bar(bar_data=bar_data)  # 继承父类方法的内容，勿删

        pass

    def on_1m_bar(self, bar_data: BarData):
        """1m(或最小周期)K线数据生成回调函数"""
        super().on_1m_bar(bar_data=bar_data)  # 继承父类方法的内容，勿删
        year_month = dt.datetime.strftime(bt.num2date(self.data.datetime[0]), "%Y-%m")
        now_dt = bar_data.datetime.strftime('%Y-%m-%d %H:%M')
        if year_month not in self.completed_month:
            self.completed_month.append(year_month)
            print(f"回测进行至{self.completed_month[-1]}")
        else:
            pass
        if self.size == 0:
            # 确定当前趋势
            adx = self.am_1m.adx(14, False)
            roc = self.am_1m.roc(14, False)
            trend_up = True if adx > 20 and roc > 0 else False
            trend_down = True if adx > 20 and roc < 0 else False

            # 确定当前波动幅度
            atr = self.am_1m.atr(14, False)
            wave_cond = True if atr/self.am_1m.close[-1] > 0.005 else False

            # 5日均线向上触及20日均线（趋势为空且波动幅度足够），做空
            sma_5_arr = self.am_1m.sma(5, True)
            sma_20_arr = self.am_1m.sma(20, True)
            up_5_20 = True if sma_5_arr[-1] >= sma_20_arr[-1] and sma_5_arr[-2] < sma_20_arr[-2] else False
            if up_5_20 and trend_down and wave_cond:
                self.sell(size=int(self.qty*0.8))
                print(f"{now_dt} 触发空单开仓条件")
            # 5日均线向下触及20日均线（趋势为多且波动幅度足够），做多
            down_5_20 = True if sma_5_arr[-1] <= sma_20_arr[-1] and sma_5_arr[-2] > sma_20_arr[-2] else False
            if down_5_20 and trend_up and wave_cond:
                self.buy(size=int(self.qty*0.8))
                print(f"{now_dt} 触发多单开仓条件")
        elif self.size > 0:
            # 盈利达到5%平仓
            stop_profit = True if (self.am_1m.close[-1] - self.price) / self.price >= 0.05 else False
            # 或亏损达到2%平仓。
            stop_loss = True if (self.am_1m.close[-1] - self.price) / self.price <= -0.02 else False
            if stop_profit:
                self.close(size=self.size)
                print(f"{now_dt} 触发多单止盈平仓条件")
            elif stop_loss:
                self.close(size=self.size)
                print(f"{now_dt} 触发多单止损平仓条件")
        elif self.size < 0:
            # 盈利达到5%平仓
            stop_profit = True if (self.price - self.am_1m.close[-1]) / self.price >= 0.05 else False
            # 或亏损达到2%平仓。
            stop_loss = True if (self.price - self.am_1m.close[-1]) / self.price <= -0.02 else False
            if stop_profit:
                self.close(size=-self.size)
                print(f"{now_dt} 触发空单止盈平仓条件")
            elif stop_loss:
                self.close(size=-self.size)
                print(f"{now_dt} 触发空单止损平仓条件")
        else:
            pass
        pass

    def on_5m_bar(self, bar_data: BarData):
        """5mK线数据生成回调函数"""
        super().on_5m_bar(bar_data=bar_data)  # 继承父类方法的内容，勿删

        pass

    def on_15m_bar(self, bar_data: BarData):
        """15mK线数据生成回调函数"""
        super().on_15m_bar(bar_data=bar_data)  # 继承父类方法的内容，勿删

        pass

    def stop(self):
        """策略执行结束回调函数"""
        super().stop()  # 继承父类方法的内容，勿删

        pass

    def notify_order(self, order):
        """订单状态改变回调函数"""
        super().notify_order(order=order)  # 继承父类方法的内容，勿删

        pass

    def notify_trade(self, trade):
        """交易状态改变回调函数"""
        super().notify_trade(trade=trade)  # 继承父类方法的内容，勿删

        pass

    def notify_cashvalue(self, cash, value):
        """单个行情节点处理完毕后，推送现金及净值数据"""
        super().notify_cashvalue(cash=cash, value=value)  # 继承父类方法的内容，勿删

        pass

