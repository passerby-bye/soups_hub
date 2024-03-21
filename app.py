import subprocess


import os
import subprocess
import time
from io import BytesIO

def install_requirements(requirements_file):
    try:
        # 使用 pip 命令安装 requirements.txt 中的库
        subprocess.check_call(['pip', 'install', '-r', requirements_file])
        print("库安装成功！")
    except subprocess.CalledProcessError as e:
        print("安装失败:", e)

# 指定 requirements.txt 文件路径
requirements_file = 'requirements.txt'

# 安装 requirements.txt 中的库
install_requirements(requirements_file)
os.system(f"python game_app.py")



os.system(f"python game_app.py")

