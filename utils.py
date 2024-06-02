import os
import json
import logging
import cv2
from common import *


def init_logger(name):
        logger = logging.getLogger(name)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logging.basicConfig(filename=name + '.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        logger.addHandler(console_handler)
        return logger

# logger = init_logger("utils")

# 如果图片尺寸小于224x224 进行padding
def image_padding(image, scale = True):
    if scale :
        original_height, original_width = image.shape[:2]
        new_width = original_width * 2
        new_height = int(original_height * 1.5)  
        image = cv2.resize(image, (new_width, new_height))
        
    height, width = image.shape[0], image.shape[1]

    # 设置目标尺寸
    target_size = (224, 224)
    
    height_padding = 0
    width_padding = 0
    # 计算需要添加的填充量
    if height < target_size[0] or width < target_size[1]:
        height_padding = max(0, target_size[0] - height)
        width_padding = max(0, target_size[1] - width)

    # 计算垂直和水平填充的数量
    top_padding = height_padding // 2
    bottom_padding = height_padding - top_padding
    left_padding = width_padding // 2
    right_padding = width_padding - left_padding

    # 创建白色填充
    white = (255, 255, 255)
    image = cv2.copyMakeBorder(image, top_padding, bottom_padding, left_padding, right_padding, cv2.BORDER_CONSTANT, value=white)

    # 调整图像大小为目标尺寸
    image = cv2.resize(image, target_size)
    return image


def judge_my_cards(card_num_list, card_type):
    if card_type == CardsCombEnum.BAOZI:
        return MyCardsEnum.BAOZI
    if card_type == CardsCombEnum.TONGHUASHUN:
        return MyCardsEnum.TONGHUASHN
    if card_type == CardsCombEnum.JINHUA:
        if 'A' in card_num_list:
            return MyCardsEnum.AHUA
        if 'K' in card_num_list:
            return MyCardsEnum.KHUA
        if 'Q' in card_num_list:
            return MyCardsEnum.QHUA
        if 'J' in card_num_list:
            return MyCardsEnum.JHUA
    return MyCardsEnum.BAD

def read_conf(file_path):
    if not os.path.exists(file_path):
        raise Exception('未找到配置文件')
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

def print_split_line():
    print("===========================================")
    
    
def correct_decimal_point(last_result, current_result):
    
    """
    根据上次OCR结果校正当前OCR结果中的小数点。
    
    Args:
    last_result (str): 上次OCR结果，带小数点的数字。
    current_result (str): 当前OCR结果，可能疏漏小数点的数字。
    
    Returns:
    str: 校正后带小数点的当前OCR结果。
    """
    min_interval = 99999
    if(current_result > 10000):
        current_result /= 100
    ret = current_result
    
    if (abs(current_result - last_result) > 100):
        while(current_result > 0):
            current_result = current_result / 10.0
            interval = abs(current_result - last_result)
            if (interval < min_interval):
                min_interval = interval
                ret = current_result
    if ret < 10:
        return current_result
    return ret
if __name__ == "__main__":
    last_result = 110.8
    current_result = 112.8
    corrected_result = correct_decimal_point(last_result, current_result)
    print("校正后结果:", corrected_result)