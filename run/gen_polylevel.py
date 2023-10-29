'''生成多种级别的行情数据，若出现数据缺失，需要进行警报输出'''
import pandas as pd
import re
from tools.method import bars2ls

# 加载主力连续数据
contract_name = 'fu'
data_path = '../data'
market_data = pd.read_csv(data_path)
# 获取原始数据级别及起始时间
ori_level = '1m'  # 通过获得的数据自动检测
ori_start = '2020-01-01 00:00:00'
ori_end = '2023-12-31 11:59:59'
# 获取生成数据级别及起始时间
goal_level = '5m'
goal_start = ''
goal_end = ''

# 引用veighna的方案处理级别的转换

data_df = pd.read_csv(data_path)
# data_df.set_index('datetime', inplace=True)

pattern = r'\d+'
goal_level_int = int(re.search(pattern, goal_level)[0])

bars_ls = data_df.values.tolist()
# 转为指定时间粒度
bar_new = bars2ls(bars_ls, interval=goal_level_int, start=goal_start, end=goal_end)
# 转为DataFrame
data_new = pd.DataFrame(bar_new, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
data_new.set_index('datetime', inplace=True)
data_new_path = f"../market_data/{contract_name}&{goal_start}&{goal_end}&{goal_level}.csv"
data_new.to_csv(data_new_path)




