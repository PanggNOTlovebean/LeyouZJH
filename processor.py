from utils import *
import cv2
import os
from paddleocr import PaddleOCR
from common import *
import re
import pytesseract
import re
import numpy as np
import time
from concurrent.futures import ProcessPoolExecutor
import matplotlib.pyplot as plt
logging.disable(logging.DEBUG)
pytesseract.pytesseract.tesseract_cmd = r".\Tesseract-OCR\tesseract.exe"
logger = init_logger("Image Processor")
# ocr = PaddleOCR(use_gpu = True, use_angle_cls=True, det_model_dir='path_to_your_custom_det_model', rec_model_dir='path_to_your_custom_rec_model')
ocr_model = PaddleOCR(use_angle_cls=True, lang="en")
ocr_model_cn = PaddleOCR(use_angle_cls=True, lang="ch")

def is_number(s):   
    try:
        float(s)  # 尝试将字符串转换为浮点数
        return True
    except ValueError:
        return False
    
def empty_task():
    # 空操作，什么也不做
    return

# 英文识别模型
def ocr(image):
    image = image_padding(image)
    result = ocr_model.ocr(image, cls=True)
    
    if len(result) == 0 or result[0] == None:
        return "#"
    return result[-1][-1][-1][0]

# 中文识别模型
def ocr_cn(image):
    image = image_padding(image)
    result = ocr_model_cn.ocr(image, cls=True)
    if len(result) == 0 or result[0] == None:
        return "#"
    return result[-1][-1][-1][0]

# 中文识别模型，拼接所有识别文字
def ocr_cn_all(image):
    image1 = image_padding(image, False)
    # plt.imshow(image1)
    # plt.show()
    result = ocr_model_cn.ocr(image1, cls=True)
    # print(result)
    if len(result) == 0 or result[0] == None:
        return "#"
    ocr_string = ''
    for a in result[-1]:
        ocr_string += a[-1][0]
    
    return ocr_string
    
    
def get_single_player_money(cropped_image):
    result = ocr(cropped_image)
    
    result = result.replace(',', '')
    try:
        result = float(result)
    except Exception:
        result = -1
        
    return result

def parse_state(image):
    ocr_result = ocr_cn_all(image)
    
    if '已看牌' in ocr_result or '已' in ocr_result or '看' in ocr_result:
        return PlayerStatusEnum.LOOKED
    
    if '失败' in ocr_result:
        return PlayerStatusEnum.LOOSE
    
    if '*' in ocr_result:
        return PlayerStatusEnum.FOLLOWING
    
    if '弃牌' in ocr_result:
        return PlayerStatusEnum.ABANDON
    
    return PlayerStatusEnum.NONE

class ImageProcessor:
    def __init__(self):
        logger.debug("加载ocr模型")
        
        self.test_num = 0
        
        # print('提交空操作以预热进程池')
        self.executor = ProcessPoolExecutor(max_workers=4)
        # 提交空操作以预热进程池
        futures = [self.executor.submit(empty_task) for _ in range(4)]
        for future in futures:
            future.result()
        logger.debug("加载完成")

    def check_game_status(self, image):
        
        image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        x, y = PositionConstant.PK_POSITION
        if image[y, x, 2] < 100:
            return GameStatusEnum.PK
        
        x, y = PositionConstant.ADD_POSITION
        bt_x, bt_y = PositionConstant.START_CLICK_POS
        if 10 < image[y, x, 0] < 30 :
            return GameStatusEnum.MYTURN
        
        x1, y1, x2, y2 = PositionConstant.FOLLOW_BUTTON
        cropped_image = image[y1:y2, x1:x2]
        result = ocr_cn(cropped_image)
        if '跟注' in result and '自动' not in result:
            return GameStatusEnum.MYTURN
        
        if 100 < image[y, x, 0] < 130 and image[bt_y, bt_x, 0] < 30:
            return GameStatusEnum.STOP
        
        return GameStatusEnum.WATING

     
    def get_next_bet(self, image):
        x1, y1, x2, y2 = PositionConstant.COMPARE_BUTTON
        cropped_image = image[y1:y2, x1:x2]
        plt.imshow(cropped_image)
        result = ocr_cn(cropped_image)
        match = re.search(r"\d+", result)
        if match:
            # 获取匹配到的数字
            number = match.group(0)
            return int(number)
        return -1
    
    def get_my_cards(self, image):
        card_num_list = []

        for i in range(len(PositionConstant.CARD_POS)):
            x1, y1, x2, y2 = (
                PositionConstant.CARD_POS[i][0],
                PositionConstant.CARD_POS[i][1],
                PositionConstant.CARD_POS[i][2],
                PositionConstant.CARD_POS[i][3],
            )

            cropped_image = image[y1:y2, x1:x2]
            card_type_num = self.parse_card_num(cropped_image)
            card_num_list.append(card_type_num)
        
        x1, y1, x2, y2 = (
            PositionConstant.CARD_PROMOTE_POS[0],
            PositionConstant.CARD_PROMOTE_POS[1],
            PositionConstant.CARD_PROMOTE_POS[2],
            PositionConstant.CARD_PROMOTE_POS[3],
        )
        
        cropped_image = image[y1:y2, x1:x2]
        card_type = self.parse_card_type(cropped_image)
        # 豹子兜底检查
        if card_type != CardsCombEnum.EORROR and card_num_list[0] == card_num_list[1] and card_num_list[0] == card_num_list[2] and card_num_list[1] == card_num_list[2]:
            if card_num_list[0] != "Q":
                card_type = CardsCombEnum.BAOZI
        return card_num_list, card_type
    
    def parse_card_type(self, image):
        
        ocr_result = self.ocr_cn_card(image)
        print(f'牌型检测结果:{ocr_result}')
        
        for comb in CardsCombEnum:
            if comb.value in ocr_result:
                return comb
            
        if '花顺' in ocr_result:
            return CardsCombEnum.TONGHUASHUN
        
        if '的子' in ocr_result or '韵子' in ocr_result:
            return CardsCombEnum.BAOZI
            
        if '#' == ocr_result:
            return CardsCombEnum.EORROR
        
        return CardsCombEnum.GAOPAI
    
    def check_is_auto(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        x, y = PositionConstant.AUTO_POS
        # print(image[y, x, 0])
        if (image[y, x, 0] > 100):
            x, y = PositionConstant.CANCEL_AUTO_POS
            # print(image[y, x, 1])
            if image[y, x, 1] > 150:
                return True
            return False
        else:
            return True

    
    def parse_card_num(self, image):
        height, width = image.shape[0], image.shape[1]
        
        # image = image[0 : int(height * 0.6), :]
        result = self.ocr_card_number(image)
        # print(result)
        # 五次OCR
        if result == -1:
            result = self.ocr_card_number(cv2.cvtColor(image, cv2.COLOR_RGB2GRAY))
            # print(result)
        if result == -1:
            result = pytesseract.image_to_string(image, lang='eng', config='--psm 10 --oem 3 -c tessedit_char_whitelist=JQKA').strip()
            # print(result)
        if result == '':
            result = pytesseract.image_to_string(image, lang='eng', config='--psm 10 --oem 3 outputbase digits').strip()
            # print(result)
        if result == '':
            result = pytesseract.image_to_string(cv2.cvtColor(image, cv2.COLOR_RGB2GRAY), lang='eng', config='--psm 10 --oem 3 -c tessedit_char_whitelist=JQKA').strip()
            # print(result)
        if result == '':
            result = pytesseract.image_to_string(cv2.cvtColor(image, cv2.COLOR_RGB2GRAY), lang='eng', config='--psm 10 --oem 3 outputbase digits').strip()
            # print(result)
        # plt.imshow(image)
        # plt.show()
        result = str(result)
        # print(result)
        
        if result == '1':
            result = 'J'
            
        if result == '-':
            result = 'Q'
        
        if result != '10' and '1' in result:
            result = result.replace('1', '')
            
        if result == '0':
            result = '10'
            
        for c in ['A', 'K', 'Q', 'J']:
            if c in result:
                result = c
                break
        
        if result == '':
            return 'Q'
        
        return str(result)
    
    def get_players_status(self, image):
        players_status_list = []
        cropped_images = []
        for i in range(1, len(PositionConstant.PLAYERS_POS)):
            x1, y1, x2, y2 = (
                PositionConstant.PLAYERS_POS[i][0],
                PositionConstant.PLAYERS_POS[i][1],
                PositionConstant.PLAYERS_POS[i][2],
                PositionConstant.PLAYERS_POS[i][3],
            )
            cropped_image = image[y1:y2, x1:x2]
            cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_RGB2BGR)
            cropped_image = cv2.bitwise_not(cropped_image)
            cropped_images.append(cropped_image)

        results = list(self.executor.map(parse_state, cropped_images))
        for i in range(4):
            players_status_list.append(results[i])
        return players_status_list
    


    def ocr_card_number(self, image):
        result = ocr(image)
        match = re.search(r"\d+", result)
        number = -1
        if match:
            # 获取匹配到的数字
            number = match.group(0)
            return int(number)
        return number
    
    def ocr_cn_card(self, image):
        image1 = image_padding(image, False)
        result = ocr_model_cn.ocr(image1, cls=True)
        if len(result) == 0 or result[0] == None:
            image2 = image_padding(image, True)
            result = ocr_model_cn.ocr(image2, cls=True)
            if len(result) == 0 or result[0] == None:
                return "#"
        ocr_string = ''
        for a in result[-1]:
            ocr_string += a[-1][0]
        return ocr_string

    def get_tot_bet(self, image):
        x1, y1, x2, y2 = PositionConstant.TOT_BET_LABEL
        cropped_image = image[y1:y2, x1:x2]
        cropped_image = image_padding(cropped_image)
        result = ocr(cropped_image)
        if (result == '#'):
            result = self.parse_card_num(cropped_image)
        if (is_number(result)):
            return int(result)
        # plt.imshow(cropped_image)
        # plt.show()
        return -1
        
    def get_money(self, image):
        x1, y1, x2, y2 = PositionConstant.MONEY_BUTTON
        cropped_image = image[y1:y2, x1:x2]
        
        # cropped_image = image_padding(cropped_image)
        
        # result = pytesseract.image_to_string(cropped_image, lang='eng', config='--psm 10 --oem 3 outputbase digits').strip()
        result = get_single_player_money(cropped_image)
        # if len(result) > 0 and result[0] == '-':
        #     result = result[1:]
        # result = result.replace('-', '.')
        # try:
        #     if result == '' or is_number(result) == False or float(result) > 1000 or float(result) < 10 :
        #     # 兜底检查
        #         result = ocr(cropped_image)
        #     result = float(result)
        # except Exception:
            
        #     return -1
        return result
    
    def follow_check(self, image):
        x1, y1, x2, y2 = PositionConstant.FOLLOW_BUTTON
        cropped_image = image[y1:y2, x1:x2]
        result = ocr_cn(cropped_image)
        if '跟' not in result:
            return False
        if '自动' in result:
            return False
        return True

    def check_vpn(self, image):
        x1, y1, x2, y2 = PositionConstant.VPN_ICON
        cropped_image = image[y1:y2, x1:x2]
        # plt.imshow(hsv_image)
        # plt.show()
        hsv_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
        
        v_max = np.max(hsv_image[:, :, 2])
        if v_max > 200:
            return True
        else:
            return False
    
    
    def get_player_money(self, image):
        player_bet_list = [-1 for _ in range(4)]
        cropped_images = []
        for i in range(1, 5):
            x1, y1, x2, y2 = PositionConstant.BET_POS[i]
            cropped_image = image[y1:y2, x1:x2]
            # plt.imshow(cropped_image)
            # plt.show()
            cropped_images.append(cropped_image)
        results = list(self.executor.map(get_single_player_money, cropped_images))
        for i in range(4):
            player_bet_list[i] = results[i]
        return player_bet_list

    def get_round(self, image):
        x1, y1, x2, y2 = PositionConstant.ROUND
        cropped_image = image[y1:y2, x1:x2]
        result = ocr_cn(cropped_image)
        match = re.search(r'\d+', result)
        if match:
            return match.group(0)
        else:
            return -1
        
def main():
    processor = ImageProcessor()
    # for i in range(10):
    # for i in [1]:
    dir_path = 'test/auto'
    # dir_path = 'test_run/1'
    # dir_path = 'test_run/1702781747'

    # 记录开始时间
    start_time = time.time()
    times = [0 for _ in range(8)]
    gaps_sum = [0 for _ in range(7)]
    for path in os.listdir(dir_path):
        print(path)
        image = cv2.imread(os.path.join(dir_path, path), cv2.IMREAD_UNCHANGED)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        print(processor.check_is_auto(image))
        # print(processor.get_tot_bet(image))
        # print(processor.get_next_bet(image))
        # print(processor.get_round(image))
        # print(processor.get_player_money(image))
        # print(processor.get_money(image))

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(gaps_sum)
    print(f"代码运行时间: {elapsed_time} 秒")
    
if __name__ == "__main__":
    # import cProfile
    # cProfile.run('main()', 'profile_out')
    main()
