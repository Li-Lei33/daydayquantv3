import numpy as np
import pandas as pd

import tools.method as tm
import inspect

from config.constant import Model
from tools.method import read_json, save_json, dt_str, gen_ppt_f1, list_model_directories

import os
import importlib
import types

import tkinter as tk


"""本程序用于将因子带入指定模型的金融数据中，并展示因子画像，用于做因子分析"""


class SimpleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DayDayQuant Factor Analysis")

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

        # 下拉框，选择现有的因子研究报告方案------------------------------
        # 设置标签
        label3 = tk.Label(text="研究方案：")
        self.variable_3 = tk.StringVar(self.root)

        self.option_menu_3 = tk.OptionMenu(self.root, self.variable_3, *[""])
        label3.grid(row=2, column=0, pady=10)
        self.option_menu_3.grid(row=2, column=1, pady=10)

        # 文本框，显示所有备选因子---------------------------
        label4 = tk.Label(text="备选因子：")
        label4.grid(row=3, column=0, pady=10)

        self.textbox = tk.Text(self.root, wrap='word', width=40, height=10)
        self.textbox.grid(row=3, column=1, padx=10, pady=10)

        # 界面布局后再配置回调函数
        self.variable.trace('w', self.refresh_interface)
        # 读取当前模型名
        conf = read_json(
            os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "config", "conf.json"))

        default_model_name = Model.MODEL_PRE.value + str(conf["now_model"])
        self.variable.set(default_model_name)

        self.submit_button = tk.Button(root, text="提交", command=self.analysis_factor)
        self.submit_button.grid(row=4, column=1, pady=20)

    def refresh_interface(self, *args):
        # 获取更改后的模型名----------------------
        now_model_name = self.variable.get()
        # 设置模型下数据名---------------------------
        default_model_path = os.path.join(self.project_path, now_model_name)
        data_folder_path = os.path.join(default_model_path, "market_data")
        csv_files = [f for f in os.listdir(data_folder_path) if f.endswith('.csv') and os.path.isfile(os.path.join(data_folder_path, f))]
        csv_file_default = csv_files[0]  # 取第一个值为默认值
        menu2 = self.option_menu_2['menu']
        menu2.delete(0, tk.END)

        # 添加新的选项，并更新下拉框默认值
        for file in csv_files:
            menu2.add_command(label=file, command=tk._setit(self.variable_2, file))
        self.variable_2.set(csv_file_default)

        # 文本框，显示所有备选因子------------------------
        # 获取所有因子
        factor_am = importlib.import_module('.'.join([now_model_name, "factor", "factor_am"]))
        factor_class = factor_am.ArrayManager
        # 获取类中非父类方法名
        methods = []
        # 获取类的所有属性和方法
        for name, func in factor_class.__dict__.items():
            # 过滤出方法，并排除继承自父类的方法
            if isinstance(func, types.FunctionType) and name != "get_public_factor" and name != "__init__":
                methods.append(name)
        for name in factor_class(size=1).get_public_factor():
            methods.append(name)
        text = ', '.join(map(str, methods))

        # 下拉框，选择现有的因子研究报告方案-------------------------------
        # 获取method下gen_ppt_f前缀的方法名
        func_name_ls = []
        for name, obj in inspect.getmembers(tm):
            # 如果属性是函数，获取其名字，若名字满足gen_ppt_t前缀，将其添加至列表
            if isinstance(obj, types.FunctionType) and "gen_ppt_f" in name:
                func_name_ls.append(name)

        default_gen_ppt = func_name_ls[0]

        menu3 = self.option_menu_3["menu"]
        menu3.delete(0, tk.END)
        for func_name in func_name_ls:
            menu3.add_command(label=func_name, command=tk._setit(self.variable_3, func_name))
        self.variable_3.set(default_gen_ppt)

        # 在文本框中更新字符串
        self.textbox.delete("1.0", tk.END)
        self.textbox.insert(tk.END, text)

    def analysis_factor(self):
        """从界面获取相应参数，并开展因子分析"""
        # 获取模型路径
        model_name = self.variable.get()

        # 获取需要分析的因子
        factor_name_ls = self.textbox.get('1.0', tk.END)[:-1].split(', ')
        # 获取所用到的数据
        data_file_name = self.variable_2.get()
        data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), model_name, 'market_data', data_file_name)
        # 获取因子研究报告方案
        gen_ppt = self.variable_3.get()
        analysis(model_name, factor_name_ls, data_path, gen_ppt)


def analysis(model_name: str, factor_name_ls: list, data_path: str, gen_ppt: str):
    print(f"{dt_str()}开始生成因子分析报告")
    # 导入模型因子类
    factor_am = importlib.import_module('.'.join([model_name, "factor", "factor_am"]))
    factor_class = factor_am.ArrayManager
    # 模型路径
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), model_name)
    # 数据路径
    data_ori = pd.read_csv(data_path)
    am = factor_class(len(data_ori))
    am.open_array = data_ori['open'].to_numpy()
    am.high_array = data_ori['high'].to_numpy()
    am.low_array = data_ori['low'].to_numpy()
    am.close_array = data_ori['close'].to_numpy()
    am.volume_array = data_ori['volume'].to_numpy()

    # 遍历数据，新增因子列
    for f in factor_name_ls:
        method_to_call = getattr(am, f)
        result = method_to_call(n=14, array=True)
        # 如果result类型不为ndarray则报错
        if not isinstance(result, np.ndarray):
            raise ValueError(f"因子{f}返回值不满足一维ndarray要求")
        # 因子值添加到数据新列
        data_ori[f] = result
    print(f"{dt_str()}因子值计算完毕")

    # 因子已整合，开始基于因子值给出分析报告
    if gen_ppt == "gen_ppt_f1":
        gen_ppt_f1(data_ori, os.path.join(model_path, "result"))
        pass
    else:
        raise ValueError(f"{dt_str()}未知的因子分析报告方案")


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleApp(root)
    root.mainloop()
