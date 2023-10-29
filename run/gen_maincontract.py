import os
import datetime
import pandas as pd

'''生成主力连续合约，传入初始行情数据，及相关参数，输出主力连续合约'''


# 输入预先选中的合约数据，输入参数为，，
# 输出为主力连续合约，换月期尽可能不要反复横跳


# 新建可视化界面

# 选择参与计算的合约（为简化流程，仅选择合约所属月份）

# 从最早合约开始，同时间所有合约对比交易量，列出交易量最大的两组合约，作为当前主力合约


# 获取参与计算的所有合约的文件名
# 选择所有合约数据，一并参与计算
folder_name = 'FU'
repair_folder_name = folder_name + '_repair'
# # ori_data_path = "../data/ori_data/"
ori_data_path = os.path.join('..', 'data', 'ori_data')

# 修复后数据已经存在
if os.path.exists(os.path.join(ori_data_path, repair_folder_name)):
    print('文件夹已经存在')
else:
    os.mkdir(os.path.join(ori_data_path, repair_folder_name))
    print('文件夹不存在，已新建')
folder_path = os.path.join(ori_data_path, folder_name)
file_name_ls = os.listdir(folder_path)
# 将文件名按从小到大排序（可能不用排序）

# 遍历所有文件，找出交易量高于阈值的数据
threshold_day = 100000  # 日阈值
# for file_name in file_name_ls:
#     print(file_name)
#     # 将文件中的数据整理为dataframe
#     file_data = pd.read_csv(os.path.join(folder_path, file_name))
#     # 将时间作为索引
#     file_data = file_data.set_index('date', drop=True)
#     file_data.index = pd.to_datetime(file_data.index)
#     # 按交易日计算交易量，满足条件的交易日的数据被提取
#     # 提取时间索引和交易量，按天重采样
#     daily_grouped = file_data['volume'].resample('D').sum()
#     # 筛选出阈值以上（包括）的日期
#     selected_day = daily_grouped[daily_grouped >= threshold_day].index
#     # 初始化file_data_repair
#     file_data_repair = pd.DataFrame([])
#     # 提取高于阈值（包括）的数据，并将新数据文件进行保存
#     for day_one in selected_day:
#         file_data_2 = file_data.loc[file_data.index.date == day_one.date()]
#         file_data_repair = pd.concat([file_data_repair, file_data_2], ignore_index=False)
#     if file_data_repair.empty:
#         continue
#     file_data_repair.to_csv(os.path.join(ori_data_path, repair_folder_name, file_name))

# 读取有交易量的合约数据
# 将修复后的合约数据统一组成一张大表，优先时间排序，然后按合约名称由小到大排序
repair_folder_path = os.path.join(ori_data_path, repair_folder_name)
repair_file_name_ls = os.listdir(repair_folder_path)

# 遍历所有修复文件，将其组合至一张大表
# 初始化大表
result_table = pd.DataFrame([])
print('---------2---------')
for repair_file_name in repair_file_name_ls:
    print(repair_file_name)
    repair_file_data = pd.read_csv(os.path.join(repair_folder_path, repair_file_name))
    if repair_file_data.empty:
        continue
    # 将时间作为索引
    repair_file_data = repair_file_data.set_index('date', drop=True)
    repair_file_data.index = pd.to_datetime(repair_file_data.index)
    # 将合约名称以一个新字段形式写入
    repair_file_data = repair_file_data.assign(contract=repair_file_name)
    # 按优先时间排序，然后按合约名称由小到大排序
    result_table = pd.concat([result_table, repair_file_data], ignore_index=False)

# 保证一个时间有最多两个合约（先跑出来数据看看效果）
# 筛选出所有时间数据（去重）
main_contract_table_2 = pd.DataFrame([])  # 至多两组
main_contract_table_1 = pd.DataFrame([])  # 至多一组

datetime_ls = sorted(list(set(result_table.index.to_list())))
# 按时间去索引，如果选出来一或两组，则正常添加到总数据中，若多于两组，则进行筛选
print('-------3---------')
num = 0
ls_len = len(datetime_ls)
for datetime_one in datetime_ls:
    num += 1

    if datetime_one < datetime.datetime(2020, 1, 1, 0, 0, 0):
        continue
    # print(datetime_one)
    selected_data = result_table.loc[datetime_one]
    if isinstance(selected_data, pd.Series):
        selected_data = pd.DataFrame(selected_data).T  # 转置以将行转换为列
        selected_data.index = [datetime_one]  # 重新设置索引
    recent_contract = pd.DataFrame(selected_data.iloc[0, :]).T
    recent_contract.index = [datetime_one]
    main_contract_table_1 = pd.concat([main_contract_table_1, recent_contract], ignore_index=False)
    if len(selected_data) <= 2:
        main_contract_table_2 = pd.concat([main_contract_table_2, selected_data], ignore_index=False)
    else:
        # 选出来的数据超过两组，挑选其中两组交易量最大的
        top_2_data = selected_data.nlargest(2, 'volume')
        main_contract_table_2 = pd.concat([main_contract_table_2, top_2_data], ignore_index=False)

    if num % 1000 == 0:
        print(f'进行中（剩余）：{num}/{ls_len}  （{ls_len-num}）。')


# 检查生成的近期主力连续合约
main_contract_table_1.index.name = 'date'
main_contract_table_1.to_csv('main_contract_table_1.csv')
main_contract_table_2.index.name = 'date'
main_contract_table_2.to_csv('main_contract_table_2.csv')



















