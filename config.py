import configparser
import os
# logger = init_logger("config")
drives = [f"{chr(65+i)}:\\" for i in range(26) if os.path.exists(f"{chr(65+i)}:\\")]

class Config:
    def __init__(self, config_file='conf.ini'):
        self.config = configparser.ConfigParser()
        try:
            self.config.read(config_file, encoding='utf-8')
        except Exception as e:
            self.config.read(config_file, encoding='utf-8-sig')

    def get_password(self):
        return self.config.get('user', '密码',  fallback = '')

    def get_readcard_delay(self):
        return self.config.get('game', '看牌后延迟时间(秒)',  fallback = 0)
    
    def get_max_earn(self):
        return int(self.config.get('game', '最大盈利',  fallback = 150))
    
    def get_email_address(self):
        emails = [email.strip() for email in self.config.get('user', '邮箱',  fallback = "").split(',')]
        print(emails)
        return emails
    
    def get_username(self):
        return self.config.get('user', '账号',  fallback = "pangg")
    
    def get_nikename(self):
        return self.config.get('user', '昵称',  fallback = "pangg")
    
    def get_degrade_time(self):
        return int(self.config.get('game', '降级时间(分钟)',  fallback = 60))
    
    def get_degrade_maxearn(self):
        return int(self.config.get('game', '降级盈利',  fallback = 150))
    
    def get_installation_path(self):
        path = self.config.get('path', '雷电根路径',  fallback = "")
        if len(path) == 0:
            print('正在搜索雷电模拟器路径')
            path = find_ld_path()
            self.config.set('path', '雷电根路径', path)
            with open('conf.ini', 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)
        return path
    
    def get_mobile_path(self):
        return self.config.get('path', '模拟器截图路径',  fallback = "/sdcard/pictures/Screenshots")

    def get_pc_path(self):
        path = self.config.get('path', '截图保存路径',  fallback = "")
        if len(path) == 0:
            print('正在搜索雷电存储路径')
            path = find_screenshot_path()
            self.config.set('path', '截图保存路径', path)
            with open('conf.ini', 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)
        return path
    
    def get_conserve_mode(self):
        mode = self.config.get('game', '稳健模式',  fallback = "关")
        return mode == '开'
# 实例化，这样在导入此模块时就可以直接使用了
config = Config()

def find_folder(root_path, folder_name, max_depth):
    for root, dirs, files in os.walk(root_path):
        # 计算当前目录深度
        depth = root[len(root_path):].count(os.sep)
        if depth < max_depth:
            # 限制遍历深度
            dirs[:] = [d for d in dirs if depth + 1 < max_depth]
        elif depth == max_depth:
            # 到达最大深度，清空dirs列表，防止进一步深入
            dirs[:] = []
        if os.path.basename(root) == folder_name:
            return root
    return None

def find_ld_path():
    # 获取所有磁盘
    # 搜索"LDPlayer9"文件夹
    folder_name = "LDPlayer9"
    max_depth = 4

    for drive in drives:
        path = find_folder(drive, folder_name, max_depth)
        if path != None and len(path) != 0:
            return path
    raise Exception("未查找到雷电模拟器，请手动添加")

def find_screenshot_path():
    # 获取当前用户的Documents文件夹路径
    documents_path = os.path.expanduser('~/Documents')
    
    # 定义要搜索的子路径
    subpath = "leidian9\\Pictures"
    
    # 执行搜索
    found_paths = []
    target_subpath_normalized = os.path.normpath(subpath).lower()
    for root, dirs, files in os.walk(documents_path):
        current_path_normalized = os.path.normpath(root).lower()
        if current_path_normalized.endswith(target_subpath_normalized):
            return str(root) + '\Screenshots'

    raise Exception("未查找到截图路径，请手动添加")
   
if __name__ == "__main__":
    pic_path = find_screenshot_path()
    
    ld_path = find_ld_path()
    print(pic_path)
    print(ld_path)