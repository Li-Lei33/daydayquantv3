import backtrader as bt
import numpy as np
import pandas as pd
import os
from datetime import datetime
import importlib
import tkinter as tk
import types
import inspect
import tools.method as tm

from config.constant import *
from tools.method import read_json, save_json, dt_str, gen_ppt_t1, list_model_directories


'''运行模型，弹出可视化界面，选择运行的模型，并确定所用到的数据及因子'''
class SimpleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DayDayQuant Backtesting")

        # 获取项目中所有模型的名称，回显默认项，并自动回显相关信息（），如果从回显的模型中选择了其他模型，则需额外修改配置文件中当前模型
        self.project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        model_dirs = list_model_directories(self.project_path)
        # 创建一个tkinter变量
        self.variable = tk.StringVar(self.root)

        # 设置默认模型名--------------------
        # 设置标签
        label1 = tk.Label(text="模型名称：")
        # 为避免此处设置模型名导致参数改变进而触发回调函数，进而在方法尾部设置

        # 创建OptionMenu部件
        self.option_menu = tk.OptionMenu(self.root, self.variable, *model_dirs)

        # 显示OptionMenu部件
        label1.grid(row=0, column=0, pady=10)
        self.option_menu.grid(row=0, column=1, pady=10)

        # 设置模型下数据名----------------------
        # 设置标签
        label2 = tk.Label(text="数据名称：")
        self.variable_2 = tk.StringVar(self.root)
        self.option_menu_2 = tk.OptionMenu(self.root, self.variable_2, *[""])

        label2.grid(row=1, column=0, pady=10)
        self.option_menu_2.grid(row=1, column=1, pady=10)

        # 设置模型下策略名----------------------
        # 设置标签
        label3 = tk.Label(text="策略名称：")
        self.variable_3 = tk.StringVar(self.root)
        self.option_menu_3 = tk.OptionMenu(self.root, self.variable_3, *[""])

        label3.grid(row=2, column=0, pady=10)
        self.option_menu_3.grid(row=2, column=1, pady=10)
        # 回显回测结果对应文件夹名称（默认月日小时分钟）-------------------
        # 设置标签
        label4 = tk.Label(text="结果文件夹：")
        self.option_menu_2.grid(row=1, column=1, pady=10)
        self.entry_text = tk.StringVar()
        self.folder_entry = tk.Entry(self.root, textvariable=self.entry_text)

        label4.grid(row=3, column=0, pady=10)
        self.folder_entry.grid(row=3, column=1, pady=10)
        # 下拉框，选择现有的因子研究报告方案------------------------------
        # 设置标签
        label5 = tk.Label(text="研究方案：")
        self.variable_4 = tk.StringVar(self.root)

        self.option_menu_4 = tk.OptionMenu(self.root, self.variable_4, *[""])
        label5.grid(row=4, column=0, pady=10)
        self.option_menu_4.grid(row=4, column=1, pady=10)

        # 文本框，显示本次回测的参数---------------------------
        self.textbox = tk.Text(self.root, wrap='word', width=40, height=10)
        self.textbox.grid(row=5, column=1, padx=10, pady=10)

        # 界面布局后再配置回调函数
        self.entry_text.trace_add("write", self.onEntryUpdate)
        self.variable.trace('w', self.refresh_interface)
        # 读取当前模型名
        conf = read_json(
            os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "config", "conf.json"))
        default_model_name = Model.MODEL_PRE.value + str(conf["now_model"])
        self.variable.set(default_model_name)

        # 创建容器存放按钮
        self.container = tk.Frame(root, relief="solid")
        self.container.grid(row=6, column=1, padx=3, pady=10)

        self.submit_button = tk.Button(self.container, text="提交", command=self.backtesting)
        self.submit_button.grid(row=0, column=0, padx=5, pady=5)

        self.report_button = tk.Button(self.container, text="报告", command=self.reporting)
        self.report_button.grid(row=0, column=1, padx=5, pady=5)

    def refresh_interface(self, *args):
        # 获取更改后的模型名----------------------
        now_model_name = self.variable.get()
        # 设置模型下数据名---------------------------
        now_model_path = os.path.join(self.project_path, now_model_name)
        data_folder_path = os.path.join(now_model_path, "market_data")
        csv_files = [f for f in os.listdir(data_folder_path) if f.endswith('.csv') and os.path.isfile(os.path.join(data_folder_path, f))]
        if len(csv_files) == 0:
            csv_file_default = ""
        else:
            csv_file_default = csv_files[0]  # 取第一个值为默认值
        menu2 = self.option_menu_2['menu']
        menu2.delete(0, tk.END)

        # 添加新的选项，并更新下拉框默认值
        for file in csv_files:
            menu2.add_command(label=file, command=tk._setit(self.variable_2, file))
        self.variable_2.set(csv_file_default)

        # 设置模型下策略名----------------------
        strategy_files = ["default_strategy.py"]
        menu3 = self.option_menu_3['menu']
        menu3.delete(0, tk.END)

        for strategy_file in strategy_files:
            menu3.add_command(label=strategy_file, command=tk._setit(self.variable_3, strategy_file))
        self.variable_3.set(strategy_files[0])

        # 回显回测结果对应文件夹名称（默认月日小时分钟）-------------------
        backtesting_result_name = datetime.now().strftime("%m-%d_%H-%M")
        self.entry_text.set(backtesting_result_name)

        # 下拉框，选择现有的因子研究报告方案-------------------------------
        # 获取method下gen_ppt_t前缀的方法名
        func_name_ls = []
        for name, obj in inspect.getmembers(tm):
            # 如果属性是函数，获取其名字，若名字满足gen_ppt_t前缀，将其添加至列表
            if isinstance(obj, types.FunctionType) and "gen_ppt_t" in name:
                func_name_ls.append(name)

        # 取第一个为默认值
        default_gen_ppt = func_name_ls[0]

        menu4 = self.option_menu_4["menu"]
        menu4.delete(0, tk.END)
        for func_name in func_name_ls:
            menu4.add_command(label=func_name, command=tk._setit(self.variable_4, func_name))
        self.variable_4.set(default_gen_ppt)

        # 文本框，显示本次回测的参数---------------------------
        # 获取params.json中关于回测引擎的参数
        params_path = os.path.join(now_model_path, "params.json")
        params = read_json(params_path)
        cash = params["cash"]
        shortcash = params["shortcash"]
        commission = params["commission"]
        content_1 = ", ".join(["cash: "+str(cash), "shortcash: "+shortcash, "commission: "+str(commission)])
        # 回显本次回测相关配置信息
        content_2 = "回测结果文件名："+backtesting_result_name

        # 回显提示语，本次回测策略的参数信息请从策略的__init__方法中查看
        content_3 = "关于本次回测具体的策略参数信息，请至策略的__init__方法中查看"

        # 整合本次覆盖写入的文本
        content = '\n'.join([content_1, content_2, content_3])
        self.refresh_text(content)

    def onEntryUpdate(self, *args):
        now_model_name = self.variable.get()
        now_model_path = os.path.join(self.project_path, now_model_name)
        csv_file_default = self.variable_2.get()
        strategy_files_name = self.variable_3.get()
        backtesting_result_name = self.entry_text.get()

        # 文本框，显示本次回测的参数---------------------------
        # 获取params.json中关于回测引擎的参数
        params_path = os.path.join(now_model_path, "params.json")
        params = read_json(params_path)
        cash = params["cash"]
        shortcash = params["shortcash"]
        commission = params["commission"]
        content_1 = ", ".join(["cash: "+str(cash), "shortcash: "+shortcash, "commission: "+str(commission)])
        # 回显本次回测相关配置信息
        content_2 = "回测结果文件名："+backtesting_result_name

        # 回显提示语，本次回测策略的参数信息请从策略的__init__方法中查看
        content_3 = "关于本次回测具体的策略参数信息，请至策略的__init__方法中查看"

        # 整合本次覆盖写入的文本
        content = '\n'.join([content_1, content_2, content_3])
        self.refresh_text(content)

    def backtesting(self):
        # 获取回测相关数据
        # 获得当前模型名称
        model_name = self.variable.get()

        # 获得当前数据名
        data_name = self.variable_2.get()
        # # 获得当前策略名
        # strategy_name = self.variable_3.get()
        # 获得回测结果对应文件夹名称
        result_dir_name = self.entry_text.get()
        # # 获得研究报告方案
        # analysis_name = self.variable_4.get()

        # 获得模型编号，并修改conf.json内容
        model_num = int(model_name.split(Model.MODEL_PRE.value)[1])
        conf_path = os.path.join(self.project_path, "config", "conf.json")
        conf: dict = read_json(conf_path)
        conf["now_model"] = model_num
        save_json(conf, conf_path)

        # 导入模型内唯一策略的文件
        strategy_file = importlib.import_module('.'.join([model_name, 'strategy', 'default_strategy']))
        strategy_class = strategy_file.DefaultStrategy
        # 组合模型路径
        model_path = os.path.join(self.project_path, model_name)
        # 加载数据
        data_path = os.path.join(model_path, "market_data", data_name)  # 将此数据路径回显至可视化界面
        data_ori = pd.read_csv(data_path)
        # 将时间作为索引
        data_ori = data_ori.set_index('datetime', drop=True)
        data_ori.index = pd.to_datetime(data_ori.index)
        # 读取conf.json文件
        # 配置文件路径
        conf_path = os.path.join(self.project_path, "config", "conf.json")
        conf: dict = read_json(conf_path)
        # 获取conf中的参数游标，游标设为0
        conf["now_params_sign"] = 0

        # 创建存储本次回测结果对应的文件夹
        result_dir_path = os.path.join(model_path, 'result', result_dir_name)
        os.mkdir(result_dir_path)

        # 读取conf.json文件，将结果文件夹名保存到数据文件
        conf: dict = read_json(conf_path)
        conf["result_dir_name"] = result_dir_name
        conf["result_dir_path"] = result_dir_path
        save_json(conf, conf_path)

        print(f"{dt_str()}准备进行回测")
        self.backtest(strategy_class, model_path, data_df=data_ori)
        print(f"{dt_str()}本次回测数据已生成，您可点击报告按钮，生成回测报告")

    def reporting(self):
        # 获得研究报告方案
        analysis_name = self.variable_4.get()
        # 配置文件路径
        conf_path = os.path.join(self.project_path, "config", "conf.json")
        # 读取conf.json文件，获得结果文件夹路径
        conf: dict = read_json(conf_path)
        result_dir_path = conf["result_dir_path"]
        # 生成ppt回测报告
        if analysis_name == "gen_ppt_t1":
            print(f"{dt_str()}采用gen_ppt_t1方案生成回测报告")
            gen_ppt_t1(result_dir_path=result_dir_path)  # 将此回测报告方案回显至可视化界面
            print(f"{dt_str()}gen_ppt_t1方案成功生成回测报告")

        else:
            raise ValueError(f"{dt_str()}未知的回测分析报告方案")
        pass

    def refresh_text(self, content: str):
        # 刷新文本框内容
        # 在文本框中更新字符串
        self.textbox.delete("1.0", tk.END)
        self.textbox.insert(tk.END, content)
        pass

    def backtest(self, strategy_class, model_path, data_df):
        # 获取params.json的值，并根据sign调取框架参数，初始化框架
        params_path = os.path.join(model_path, "params.json")
        params = read_json(params_path)
        cash = params["cash"]
        shortcash = params["shortcash"]
        commission = params["commission"]

        # 导入模型策略
        strategy = strategy_class
        # 自定义PandasData类
        # class CusPandasData(bt.feeds.PandasData):
        #     lines = ('c_group', )
        #     params = (('c_group', 'c_group'), )

        # 编写backtrader回测函数
        cerebro = bt.Cerebro(stdstats=True)  # create a "Cerebro" engine instance
        # Create a data feed
        data = bt.feeds.PandasData(dataname=data_df)
        cerebro.adddata(data)  # Add the data feed
        cerebro.broker.set_cash(cash)
        cerebro.broker.set_shortcash(eval(shortcash))
        cerebro.broker.setcommission(commission)
        # cerebro.addobserver(bt.observers.Broker)
        # cerebro.addobserver(bt.observers.BuySell)
        cerebro.addobserver(bt.observers.DrawDown)
        cerebro.addobserver(bt.observers.FundValue)
        # cerebro.addindicator(CacheInd)
        cerebro.addstrategy(strategy)

        cerebro.run()  # run it all
        # 生成图片存储路径
        conf_path = os.path.join(self.project_path, "config", "conf.json")
        # 读取conf.json文件，将结果文件夹名保存到数据文件
        conf: dict = read_json(conf_path)
        result_dir_path = conf["result_dir_path"]
        fig_path = os.path.join(result_dir_path, "result figure.png")
        # 重写Plot的show方法使其不显示，只保存
        from backtrader.plot.plot import Plot

        class NoShowPlot(Plot):
            def show(self):
                self.mpyplot.savefig(fig_path)

        cerebro.plot(plotter=NoShowPlot(), width=64, height=36)


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleApp(root)
    root.mainloop()










