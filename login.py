

import uuid
from config import config
import requests
from common import *
import sys   
import ctypes
from email_driver import send_email
import json
import platform
import subprocess
def run_single_instance():
    # 定义互斥体的名称，这个名称需要在系统中是唯一的
    mutex_name = "kaiyuan_zjh_game_mutex"
    
    # 尝试创建一个互斥体
    mutex = ctypes.windll.kernel32.CreateMutexA(None, False, mutex_name)
    
    # 检查互斥体是否已经存在
    last_error = ctypes.windll.kernel32.GetLastError()
    
    # 如果互斥体已经存在（ERROR_ALREADY_EXISTS=183）
    if last_error == 183:
        print("程序已经在运行中,需要请升级多窗口版本。")
        sys.exit()

def get_uuid():
    command = 'wmic cpu get ProcessorId'
    result = subprocess.check_output(command, shell=True, universal_newlines=True)
    serial_number = ''.join(result.strip().split('\n')).replace(' ','')
    # print(serial_number)
    return serial_number[-12:]

def login():
    device =  uuid.UUID(int=uuid.getnode()).hex[-12:] # 获取MAC地址并转换为十六进制格式
    # device =  get_uuid() # 获取MAC地址并转换为十六进制格式
    print(f'设备id: {device}')
    print('读取配置密码...')
    username = config.get_username()
    password = config.get_password()
    url = 'http://47.95.36.122:8082/login'  # 将地址替换为实际的服务器地址
    # 构建GET请求的参数
    params = {
        'username': f'{username}',  # 替换为实际的用户名
        'password': f'{password}',  # 替换为实际的密码
        'version': f'{VERSION}',  # 替换为实际的版本号
        'device': f'{device}'
    }

    # 发送GET请求
    response = requests.get(url, params=params)

    # 检查响应状态码
    if response.status_code == 200:
        data = response.json()  # 解析JSON响应数据
        code = data.get('code')
        message = data.get('message')
        
        if code == 1:
            print(f"登录成功")
            role = data.get('type')
            if role == 1:
                print('单窗口模式')
                run_single_instance()
            return
        else:
            email_body = message + json.dumps(params)
            for email in ["904399787@qq.com", "736045262@qq.com"]:
                send_email(
                receiver_email=email,
                body=str(email_body),
                subject=f"【{config.get_nikename()}】未认证")
            raise Exception(f"登录失败 {message}")
    else:
        print(f"请求失败 {response.status_code}")
        raise Exception(f"登录失败")

if __name__ == "__main__":
    print(get_uuid())
