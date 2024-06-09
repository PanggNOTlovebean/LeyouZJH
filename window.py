from matplotlib import pyplot as plt
import time
import cv2
from config import config
from utils import init_logger, print_split_line
from time import sleep, time
import os
from common import *
from Dnconsole import Dnconsole
logger = init_logger("window")

def change_cmd_title(title):
    """更改命令提示符窗口的标题"""
    os.system(f"title {title}")
    
def askChoice():
    choice = 0
    try:
        choice = int(input('请输入选项, 默认为0: '))
    except:
        print('输入包含无效字符, 默认选择0')
    return choice

class Window:
    
    def __init__(self):
        change_cmd_title(f"版本:{VERSION} - 等待初始化...")
        self.deconsole = Dnconsole()
        self.index = 0
        self.choose_window()
        
        
    def get_test_image(self):
        while True:
            img = self.screenshot()
            img.save(f"img{int(time())}.png")
            sleep(2)
            
   
    def choose_window(self):
        # 需要和目标窗口同一权限，游戏窗口通常是管理员权限 不是管理员就提权
        # if not windll.shell32.IsUserAnAdmin():
        #     windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        
        candidate_handles = self.deconsole.list()
        
            
        while (len(candidate_handles) == 0):
            print('游戏尚未打开.......按任意键重新检查')
            input()
            candidate_handles = self.deconsole.list()
                    
        print_split_line()
        print('可选模拟器:')
        for i, line in enumerate(candidate_handles.splitlines()):
            print(f"{i}: {line}")
        
        if (len(candidate_handles) == 1):
            print('只有一个候选窗口 默认选择窗口0')
            self.index = 0
        else:
            choice = 0
            try:
                self.index = askChoice()
            except:
                print('长时间没有输入 选择默认窗口0')
        change_cmd_title(f"版本:{VERSION} - 监控:模拟器 - {self.index}")
    
    def click(self, POS):
        x, y = POS
        print(f'点击位置: {x}, {y}')
        self.deconsole.touch(self.index, x, y)
        
    def screenshot(self):
        img = self.deconsole.screenshot(self.index)
        return img
        
if __name__ == "__main__":
    window = Window()
    window.screenshot()