#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import cv2
from time import sleep
from config import config
import numpy as np
# from retrying import retry
class Dnconsole:
    """
    【雷电控制台类】
    version: 9.0
    import该文件会自动实例化为 Dc
    """

    def __init__(self, installation_path : str = config.get_installation_path()):
        if installation_path is None or installation_path == "":
            print(f"请输入正确模拟器安装路径")
        """
        【构造方法】
        """
        # 模拟器安装路径
        self.ins_path = installation_path
        if os.path.exists(self.ins_path) is False:
            print(f"{self.ins_path}模拟器安装路径不存在！")
        
        # Dnconsole程序路径
        self.console_path = self.ins_path + r"\ldconsole.exe "
        if os.path.exists(self.console_path) is False:
            print(f"{self.console_path}程序路径不存在")
        
        # adb程序路径
        self.adb_path = self.ins_path + r"\adb.exe "
        if os.path.exists(self.adb_path) is False:
            print(f"{self.adb_path}程序路径不存在")

        # ld截屏程序路径
        self.ld_path = self.ins_path + r"\ld.exe "
        if os.path.exists(self.adb_path) is False:
            print(f"{self.ld_path}程序路径不存在！")
        
        # 模拟器截图保存路径
        self.mobile_path = config.get_mobile_path()
        
        self.pc_path = config.get_pc_path()
        
        # 构造完成
        print(f"模拟器配置加载完成.({self.ins_path})")

    def CMD(self, cmd: str):
        """
        【执行控制台命令语句】
        :param cmd: 命令
        :return: 控制台调试内容
        """
        CMD = self.console_path + cmd  # 控制台命令
        process = os.popen(CMD)
        result = process.read()
        process.close()
        return result

    def ADB(self, cmd: str):
        """
        【执行ADB命令语句】
        :param cmd: 命令
        :return: 控制台调试内容
        """
        CMD = self.adb_path + cmd  # adb命令
        process = os.popen(CMD)
        result = process.read()
        process.close()
        return result
    
    # @retry(wait_fixed=5000, stop_max_delay=10000)  # 设置重试策略
    def LD(self, cmd: str):
        CMD = self.ld_path + cmd  # adb命令
        process = os.popen(CMD)
        result = process.read()
        # process.close()
        return result
    
    def quit(self, index: int = 0):
        """
        【关闭模拟器】
        :param index: 模拟器序号
        """
        cmd = "quit --index %d" % (index)
        self.CMD(cmd)

    def quitall(self):
        """
        【关闭所有模拟器】
        """
        cmd = "quitall"
        self.CMD(cmd)

    def launch(self, index: int = 0):
        """
        【启动模拟器】
        :param index: 模拟器序号
        :return: True=已启动 / False=不存在
        """
        cmd = "launch --index %d" % (index)
        if self.CMD(cmd) == "":
            return True
        else:
            return False

    def reboot(self, index: int = 0):
        """
        【重启模拟器】
        :param index: 模拟器序号
        :return: 控制台调试内容
        """
        cmd = "reboot --index %d" % (index)
        return self.CMD(cmd)

    def list(self):
        """
        【获取模拟器列表（仅标题）】
        :return: 控制台调试内容
        """
        cmd = "list"
        return self.CMD(cmd)

    def runninglist(self):
        """
        【获取正在运行的模拟器列表（仅标题）】
        :return: 控制台调试内容
        """
        cmd = "runninglist"
        return self.CMD(cmd)

    def isrunning(self, index: int = 0):
        """
        【检测模拟器是否启动】
        :param index: 模拟器序号
        :return: True=已启动 / False=未启动
        """
        cmd = "isrunning --index %d" % (index)
        if self.CMD(cmd) == "running":
            return True
        else:
            return False

    def list2(self):
        """
        【取模拟器列表】
        :return: 列表（索引、标题、顶层句柄、绑定句柄、是否进入android、进程PID、VBox进程PID）
        """
        cmd = "list2"
        return self.CMD(cmd)

    def add(self, name: str):
        """
        【添加模拟器】
        :param name: 新模拟器标题
        :return: 控制台调试内容
        """
        cmd = "add %s" % (name)
        return self.CMD(cmd)

    def screenshot(self, index: int):
        """
        【截屏并保存到本地】
        :param index: 模拟器序号
        """
        # 记录函数开始时间
        cmd = f"-s {index} screencap -p {self.mobile_path + f'/{index}.png'}"
        self.LD(cmd)
        screenshot_path = self.pc_path + f'\\{index}.png'
        image = cv2.imdecode(np.fromfile(screenshot_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        # image = cv2.imread(screenshot_path, cv2.IMREAD_UNCHANGED)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image
    
    def touch(self, index: int, x: int, y: int, delay: int = 0):
        if delay == 0:
            self.LD(f"-s {index} input tap {x} {y}")
        else:
            self.LD(f"-s {index} input touch {x} {y} {delay}")
    
if __name__ == "__main__":

    console = Dnconsole(r"D:\leidian\LDPlayer9")
    print(console.list2())
    console.screenshot(1)
    console.touch(1, 350, 186)
    sleep(1)
    console.screenshot(1)
    # pass
