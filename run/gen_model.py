import json
import os
from tools.method import list_model_directories, dt_str, read_json, save_json
from config.constant import Model
import zipfile


'''生成一个新的模型，自动命名'''
# 新建文件夹modelx及下属四个文件夹，以及必要的py文件
project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
conf_path = os.path.join(project_path, 'config', 'conf.json')

# 获取当前所有已创建的model
# 找到编号最大的model，加1为新建model编号
model_name_ls = list_model_directories(project_path)
max_num = 0
for model_name in model_name_ls:
    num = int(model_name.split(Model.MODEL_PRE.value)[1])
    if num > max_num:
        max_num = num
new_model_name = Model.MODEL_PRE.value + str(max_num+1)

# 获取当前配置信息
conf = read_json(conf_path)

# 更新conf中的now_model字段
conf["now_model"] = max_num + 1
save_json(conf, conf_path)

# 创建新模型目录
new_model_path = os.path.join(project_path, new_model_name)
if not os.path.exists(new_model_path):
    # 如果新模型目录不存在
    os.mkdir(new_model_path)
    print(f"{dt_str()}新模型目录已创建，准备复制文件")
else:
    raise ValueError(f"{dt_str()}新模型目录已存在：{new_model_path}")

# 解压模型文件
zip_file_path = os.path.join(project_path, "model.zip")
try:
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(new_model_path)
        print(f"{dt_str()}{zip_file_path}中的文件已经成功解压到'{new_model_path}'")
except zipfile.BadZipFile:
    raise ValueError(f"Error: The file '{zip_file_path}' is not a zip file.")
except FileNotFoundError:
    raise ValueError(f"Error: The file '{zip_file_path}' does not exist.")
# 创建空文件夹result
result_path = os.path.join(new_model_path, 'result')
os.mkdir(result_path)
print(f"{dt_str()}result目录创建成功")
# 模型创建成功
print(f"{dt_str()}新模型{new_model_name}创建成功")


