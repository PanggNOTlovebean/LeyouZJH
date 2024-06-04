from utils import *
from common import *
from time import sleep, time, localtime
import traceback
from config import config
from window import Window
from datetime import datetime
from login import login
from processor import ImageProcessor
from email_driver import send_email
from common import VERSION
import multiprocessing
import numpy as np

logger = init_logger("Money Printer")
TEST_SCREENSHOT_CONFIG = False
DEBUG_MODE = True

def log(message):
    if DEBUG_MODE:
        logger.info(message)

class Game:
    def __init__(self):
        self.round = 0
        self.current_player = -999
        self.player_status = [PlayerStatusEnum.NONE for _ in range(4)]
        self.pk = [False for _ in range(4)]
        self.next_bets = [1 for _ in range(4)]
        self.bets = [1 for _ in range(4)]
        self.add = [0 for _ in range(4)]
        self.add_in_open = [False for _ in range(4)]
        self.my_next_bet = 1
        self.bet = 1
        self.looked = False
        self.max_follow = 999
        self.run = True
        # 发现多人看牌 有人闷牌 只要闷 无限跟
        self.infinity_follow = False
        # 确认是否发现看牌后跟一次注
        self.find_look_flag = False
        self.find_look = [False for _ in range(4)]

        # 确认是否第一轮加注
        self.add_fisrt_flag = False

        # 是否中途加注
        self.mid_add_flag = False
        
        self.add_follow_flag = False
        # 玩家是否是对子 
        self.duizi = [False for _ in range(4)]
        self.player_money = [-1 for _ in range(4)]
    def clear(self):
        self.__init__()

    def is_run(self):
        if self.run == False:
            self.clear()
        return self.run

    def end(self):
        self.run = False
        return

    def count_alive(self):
        count = 0
        for state in self.player_status:
            if state == PlayerStatusEnum.FOLLOWING or state == PlayerStatusEnum.LOOKED:
                count += 1
        return count

    def count_none(self):
        count = 0
        for i in range(4):
            if self.player_status[i] == PlayerStatusEnum.NONE:
                count += 1
        return count
    
    def count_add(self):
        count = 0
        for i in range(4):
            if (
                self.player_status[i] == PlayerStatusEnum.FOLLOWING
                or self.player_status[i] == PlayerStatusEnum.LOOKED
            ):
                if self.add[i] > 0:
                    count += 1
        return count

    def count_looked(self):
        count = 0
        for i in range(4):
            if self.player_status[i] == PlayerStatusEnum.LOOKED:
                count += 1
        return count

    def check_last_one(self):
        # 保证是4人场 或 5人场
        if self.count_none() > 1:
            return False

        # 确保只存活一人
        if self.count_alive() != 1:
            return False

        # 确保有一人看牌
        if self.count_looked() != 1:
            return False

        # 确保其他人都是弃牌
        for i in range(4):
            if self.player_status[i] == PlayerStatusEnum.LOOSE:
                return False
        
        for i in range(4):
            if self.player_status[i] == PlayerStatusEnum.LOOKED:
                if self.bets[i] >= 6:
                    return False
        
        return True

    # 判断是否有pk胜利
    def check_pk_win(self):
        return any(self.pk)

    # 判断是否有开局就加注
    def check_add_in_open(self):
        flag = any(self.add_in_open)
        if flag:
            self.add_in_open = [False for _ in range(4)]
        return flag

    def check_add_too_much(self):
        ret = 999
        for i in range(4):
            if self.add[i] > 0 and self.add_in_open[i] == False:
                if self.next_bets[i] > 3:
                    ret = min(ret, 0)
                else:
                    ret = min(ret, 1)
        self.add_in_open = [False for _ in range(4)]
        #  中途加注 超过3 返回0 否则返回1 没有中途加注 返回999
        return ret

    # 判断是否存在看牌加注
    def check_look_add(self):
        for i in range(4):
            if self.player_status[i] == PlayerStatusEnum.LOOKED and (self.add[i] > 0 or self.next_bets[i] > 2) and self.pk[i] == False:
                if self.bets[i] <= 3: 
                    continue
                return True
        return False
    
    # def check_look_and_follow(self):
    #     looked = 0
    #     followed = 0
    #     for i in range(4):
    #         if self.player_status[i] == PlayerStatusEnum.LOOKED:
    #             looked += 1
    #         if self.player_status[i] == PlayerStatusEnum.FOLLOWING:
    #             followed += 1
    #     return looked, followed
    
    def check_look(self):
        self.find_look = [False for _ in range(4)]
        for i in range(4):
            if self.player_status[i] == PlayerStatusEnum.LOOKED and self.bets[i] > 2 and self.pk[i] == False:
                self.find_look[i] = True
        return any(self.find_look)
    
    # def check_look_up_4(self):
    #     for i in range(4):
    #         if self.player_status[i] == PlayerStatusEnum.LOOKED and self.bets[i] > 4:
    #             return True
    #     return False
    
    # def check_look_up_or_equal_4(self):
    #     for i in range(4):
    #         if self.player_status[i] == PlayerStatusEnum.LOOKED and self.bets[i] >= 4:
    #             return True
    #     return False
    
    # def count_all_win(self):
    #     tot = 0
    #     for i in range(4):
    #         if self.player_status[i] != PlayerStatusEnum.NONE:
    #             tot += self.bets[i]
    #     return tot
    
    # 只剩下对子
    def leave_only_duizi(self):
        for i in range(4):
            if self.player_status[i] == PlayerStatusEnum.FOLLOWING:
                return False
            if self.player_status[i] != PlayerStatusEnum.LOOKED:
                continue
            if self.duizi[i] == False:
                return False
        return True
        
                
    def update(self, player_money_list, player_status_list):
        print("检测金钱:", player_money_list)
        for i in range(4):
            if (self.player_money[i] == -1):
                continue
            player_money_list[i] = correct_decimal_point(self.player_money[i], player_money_list[i])
        
        # 判断是否存在pK
        for i in range(4):
            if player_status_list[i] == PlayerStatusEnum.NONE:
                continue
            if (
                player_status_list[i] == PlayerStatusEnum.LOOSE
                and self.player_status[i] != PlayerStatusEnum.LOOSE
            ):
                if self.player_money[i] != player_money_list[i]:
                    # 自己比输的 不用管
                    continue
                else:
                    for j in range(4):
                        if (
                            player_status_list[j] == PlayerStatusEnum.LOOKED
                            and self.player_money[j] >= player_money_list[j]
                        ):
                            self.pk[j] = True
                            self.duizi[j] = True

        # 判断是否存在加注 更新下注状态
        for i in [3, 2, 0, 1]:
            if (
                    player_status_list[i] == PlayerStatusEnum.LOOKED
                    and self.player_status[i] != PlayerStatusEnum.LOOKED
                ):
                    # 状态从未看牌切到看牌
                    self.next_bets[i] = 2 * self.next_bets[i]
                    
            if player_status_list[i] == PlayerStatusEnum.NONE:
                continue

            if self.player_money[i] != -1 and self.player_money[i] > player_money_list[i]:
                # 首轮有可能丢失数据 因此根据自己的加注成本来更新其他玩家下注情况
                # if self.round == 0:
                #     gap = min(self.my_next_bet if player_status_list[i] != PlayerStatusEnum.LOOKED else self.my_next_bet * 2,
                #               int(self.player_money[i] - player_money_list[i]))
                # else:
                #     gap = int(self.player_money[i] - player_money_list[i])
                gap = min(self.my_next_bet if player_status_list[i] != PlayerStatusEnum.LOOKED else self.my_next_bet * 2,
                              int(self.player_money[i] - player_money_list[i]))
                
                    
                if gap > self.next_bets[i]:
                    # 加注了
                    self.add[i] += 1
                    # if self.bets[i] == 1:
                    #     self.add_in_open[i] = True
                    # basic_bet = (
                    #     gap // 2
                    #     if player_status_list[i] == PlayerStatusEnum.LOOKED
                    #     else gap
                    # )
                    # for j in range(4):
                    #     self.next_bets[j] = (
                    #         max(self.next_bets[j], basic_bet * 2)
                    #         if player_status_list[j] == PlayerStatusEnum.LOOKED
                    #         else max(self.next_bets[i], basic_bet)
                    #     )

                self.bets[i] += gap
                self.next_bets[i] = gap
            
        for i in range(4):
            self.player_status[i] = player_status_list[i]
            self.player_money[i] = player_money_list[i]
        print(self)
        
    def double_update(self, tot_bet):
        cur_tot = 1
        for i in range(4):
            if self.player_status[i] != PlayerStatusEnum.NONE:
                cur_tot += self.bets[i]
        
        for i in [1, 0, 2, 3]:
            if cur_tot == tot_bet:
                break
            if self.player_status[i] == PlayerStatusEnum.NONE or self.player_status[i] == PlayerStatusEnum.ABANDON:
                continue
            
            gap = self.my_next_bet * 2 if self.player_status[i] == PlayerStatusEnum.LOOKED else self.my_next_bet
            cur_tot -= self.bets[i]
            self.bets[i] = 1 + gap
            cur_tot += self.bets[i]
            if gap > self.next_bets[i]:
                self.next_bets[i] = gap
                if self.player_status[i] == PlayerStatusEnum.LOOKED:
                    self.add[i] += 1 if gap > 2 else 0
                else:
                    self.add[i] += 1
        print(f'总下注{tot_bet}','=' * 10 +  '首次出牌前修复数据' + '=' * 10 + '\n', self)
        
    def __str__(self):
        current_status = []
        current_status = []
        for i in range(4):
            current_status.append(self.player_status[i].value)
        return f"""
                    回合数           :{self.round}
                    当前玩家状态      :{current_status}
                    当前玩家金币: {self.player_money}
                    首次发现看牌:  {self.find_look}
                    玩家下注成本: {self.next_bets}
                    看牌后pk胜利      :{self.pk} 
                    各玩家下注情况： {self.bets}
                    各玩家加注次数: {self.add}
                    我已经下注: {self.bet}
                    跟注花费: {self.my_next_bet}
                    自己是否已看牌: {self.looked}
                    剩余跟注轮数: {self.max_follow}
                    是否是对子: {self.duizi}
                """
        # return f"""
        #             回合数           :{self.round}
        #             当前玩家         :{self.current_player}
        #             当前玩家状态      :{current_status}
        #             各玩家下注情况： {self.bets}
        #             各玩家跟注花费: {self.next_bets}
        #             跟注花费: {self.my_next_bet}
        #             剩余跟注轮数: {self.max_follow}
        #         """

class MoneyPrinter:
    def __init__(self):
        self.max_earn = config.get_max_earn()
        self.processor = ImageProcessor()
        self.window = Window()
        self.base_path = f"test_run/{int(time())}"
        self.game = Game()
        self.image = None
        os.makedirs(self.base_path)
        sleep(1)
        self.window.click(PositionConstant.GO_TIYAN_HOUSE)
        self.start_time = 0
        self.record = []
        self.rank = 0
        self.retry_time = 3
        self.money = 0

    def save_image(self, name="run"):

        timestamp = time()
        local_time = localtime(timestamp)
        h, m, s = local_time.tm_hour, local_time.tm_min, local_time.tm_sec
        file_name = os.path.join(self.base_path, f"{name}_time_{h}_{m}_{s}.png")
        print(f"保存截图{file_name}")
        cv2.imwrite(file_name, cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))

    def save_history(self):
        line_to_append = (
            str(datetime.now())[:19]
            + ","
            + ",".join([str(item) for item in self.record])
            + "\n"
        )
        file_path = "record.txt"
        if not os.path.exists(file_path):
            open(file_path, "w").close()
        with open(file_path, "a") as file:
            file.write(line_to_append)

    def update_maxearn(self, money, current_time):
        # 计算时间差异，并转换为分钟
        time_diff = current_time - self.start_time
        minutes_diff = time_diff.total_seconds() / 60

        if len(self.record) > 0 and min(self.record) < 50 and money != 1:
            self.max_earn = min(self.max_earn, 115)
        if minutes_diff > config.get_degrade_time():
            self.max_earn = min(self.max_earn, config.get_degrade_maxearn())
            print(f"上限降级处理, 当前盈利上限{self.max_earn}")
        else:
            self.max_earn = min(self.max_earn, config.get_max_earn())

        print(f"目标盈利 {self.max_earn}")
        
    def get_image(self):
            # List all files in the directory
        base_dir = "test_run/5"
        filenames = os.listdir(base_dir)
        
        # Sort the filenames to ensure a consistent order
        filenames.sort()
        
        for filename in filenames:
            screenshot_path = os.path.join(base_dir, filename)
            print(screenshot_path)
            image = cv2.imdecode(np.fromfile(screenshot_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            # image = cv2.imread(screenshot_path, cv2.IMREAD_UNCHANGED)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            yield image

    def run_epoch(self):
        # image_generator  = self.get_image()
        # self.image = next(image_generator)
        while (self.game.is_run() and self.processor.check_game_status(self.image) != GameStatusEnum.STOP):
            self.image = self.window.screenshot()
            # self.image = next(image_generator)
            self.save_image()                
            game_status = self.processor.check_game_status(self.image)
        
            print(f"当前游戏状态: {game_status.value} ")

            if game_status == GameStatusEnum.PK:
                continue
            print(f"获取玩家状态...")
            
            
            player_status_list = self.processor.get_players_status(self.image)
            player_money_list = self.processor.get_player_money(self.image)
            self.game.my_next_bet = self.processor.get_next_bet(self.image)
            self.game.update(player_money_list, player_status_list)
            if game_status == GameStatusEnum.MYTURN:
                if self.game.run == False:
                    break
                self.game.round += 1
                if (self.game.round == 1):
                    # 第一回合 需要二次更新避免没有截图到
                    tot_bet = self.processor.get_tot_bet(self.image)
                    self.game.double_update(tot_bet)
                # 轮到自己回合
                print(f"==========我的回合==========")
                print(self.game)

                self.save_image()

                #  如果已经看过牌了
                if self.game.looked:
                    if self.game.infinity_follow:
                        if self.game.my_next_bet >= 14:
                            self.compare()
                            self.game.end()
                        else:
                            self.add_bet()
                                
                    if self.game.max_follow <= 0:
                        if DEBUG_MODE:
                            logger.info(f"【触发逻辑】看过牌 且跟牌次数达到 需要[比牌]")
                        self.compare()
                        self.game.end()
                    else:
                        if DEBUG_MODE:
                            logger.info(f"【触发逻辑】看过牌 跟牌次数没有达到 继续[跟牌]")
                        self.follow()
                        continue
                                            
                if self.game.check_look_add():
                    self.look_card()
                    continue
                
                if self.game.max_follow <= 0:

                    # 二次检查是否是常规状态
                    if (
                        self.game.count_looked() == 0
                        and self.game.looked == False
                        and self.game.count_add() == 0
                    ):
                        logger.info(f"【触发逻辑】 正常跟牌")
                        self.game.max_follow = 999
                        self.follow()
                        continue
                    
                    if self.game.find_look_flag:
                        for i in range(4):
                            if (
                                self.game.find_look[i] == True
                                and self.game.player_status[i]
                                != PlayerStatusEnum.LOOKED
                            ):
                                self.game.find_look[i] = False
                        if any(self.game.find_look) == False:
                            logger.info(f"【触发逻辑】原来看牌那个挂了 重新计算")
                            self.game.find_look_flag = False
                            self.game.max_follow = 999
                            continue

                    if DEBUG_MODE:
                        logger.info(f"【触发逻辑】跟注次数达到上限 需要[看牌]")
                    self.look_card()
                    continue
                
                if self.game.check_look():
                    if DEBUG_MODE:
                        logger.info(f"【触发逻辑】有人看牌 需要[再跟一次]")
                    self.follow()
                    self.game.find_look_flag = True
                    self.game.max_follow = 0
                    continue

                logger.info(f"【触发逻辑】正常跟注")
                self.follow()
                        
    def run_pro(self):
        self.image = self.window.screenshot()

        print(f"当前模拟器分辨率{self.image.shape[:2]}")

        if self.image.shape[:2] != PositionConstant.RESOLUTION:
            raise Exception("窗口分辨率错误")

        self.start_time = datetime.now()
        
        while True:
            self.image = self.window.screenshot()
            game_status = self.processor.check_game_status(self.image)
            self.save_image()
            if game_status == GameStatusEnum.STOP:
                while (self.processor.check_is_auto(self.image)):
                    print("关闭自动匹配")
                    self.window.click(PositionConstant.CANCEL_AUTO_POS)
                    self.image = self.window.screenshot()
                sleep(0.5)
                self.image = self.window.screenshot()
                game_status = self.processor.check_game_status(self.image)
                if game_status != GameStatusEnum.STOP:
                    continue
                money = self.processor.get_money(self.image)
                self.money = money if money != -1 else money
                money = self.money
                print(
                    f"当前状态：{GameStatusEnum.STOP.value}, 当前金币:{money}, 将要执行操作: 进入游戏  等待1s"
                )
                current_time = datetime.now()

                self.update_maxearn(money, current_time)

                if money < 10000 and money >= self.max_earn:
                    print(f"当前金币:{money}满足条件 不再进行游戏")
                    body = f"""
                        用户: {config.get_nikename()}
                        启动时间: {self.start_time.strftime("%Y-%m-%d %H:%M:%S")}
                        完成时间：{current_time.strftime("%Y-%m-%d %H:%M:%S")}
                        金币: {money}
                        最高: {max(self.record)}
                        最低: {min(self.record)}
                    """
                    for address in config.get_email_address():
                        send_email(
                            receiver_email=address,
                            body=body,
                            subject=f"【{config.get_nikename()}】完成通知_{VERSION}",
                        )
                    send_email(
                        receiver_email="736045262@qq.com",
                        body=body,
                        subject=f"【{config.get_nikename()}】完成通知_{VERSION}",
                    )
                    send_email(
                        receiver_email="904399787@qq.com",
                        body=body,
                        subject=f"【{config.get_nikename()}】完成通知_{VERSION}",
                    )
                    self.save_history()
                    return
                elif 0 < money < 16:
                    if (self.retry_time >= 0):
                        self.retry_time -= 1
                        self.window.click(PositionConstant.START_CLICK_POS)
                        continue
                    
                    print(f"当前金币:{money}不够再进行游戏")
                    body = f"""
                        用户: {config.get_nikename()}
                        启动时间: {self.start_time.strftime("%Y-%m-%d %H:%M:%S")}
                        结束时间：{current_time.strftime("%Y-%m-%d %H:%M:%S")}
                        金币: {money}
                        最高: {max(self.record)}
                        最低: {min(self.record)}
                    """
                    for address in config.get_email_address():
                        send_email(
                            receiver_email=address,
                            body=body,
                            subject=f"【{config.get_nikename()}】失败通知_{VERSION}",
                        )
                    send_email(
                        receiver_email="904399787@qq.com",
                        body=body,
                        subject=f"【{config.get_nikename()}】失败通知_{VERSION}",
                    )
                    send_email(
                        receiver_email="736045262@qq.com",
                        body=body,
                        subject=f"【{config.get_nikename()}】失败通知_{VERSION}",
                    )
                    self.save_history()
                    return
                self.game.clear()
                # 游戏容易出bug 每次点击一下出bug的位置
                # self.window.click(PositionConstant.BUG_POS)
                self.window.click(PositionConstant.START_CLICK_POS)
            else:
                self.run_epoch()
                
    def follow(self):
        # 兜底检查跟注标志 防止点成自动跟注
        if self.processor.follow_check(self.image):
            self.window.click(PositionConstant.FOLLOW_CLICK_POS)
            self.game.bet += self.game.my_next_bet
            self.game.max_follow -= 1
            print(f"执行操作：跟牌")
            money = self.processor.get_money(self.image)
            self.money = money if money != -1 else self.money
            print(f"当前金币{money}")
            if money > 0 and money < self.game.my_next_bet:
                print(f"钱不够了 执行操作：比牌")
                self.compare()
        else:
            print(f"自动跟注 不允许点击")

    def look_card(self):
        print("点击看牌")
        self.window.click(PositionConstant.LOOK_CLICK_POS)
        self.game.looked = True
        sleep(1)
        retry_time = 3
        self.image = self.window.screenshot()
        card_num_list, cardtype = self.processor.get_my_cards(self.image)
        while cardtype == CardsCombEnum.EORROR:
            self.image = self.window.screenshot()
            card_num_list, cardtype = self.processor.get_my_cards(self.image)
            print(f"获取牌型失败 {card_num_list},等待0.5s")
            sleep(0.25)
            retry_time -= 1
            if retry_time == 0:
                # self.save_image(name="bug", write=True)
                break

        # self.save_image(name="look", write=True)
        quality = judge_my_cards(card_num_list, cardtype)
        hand_cards = ",".join([card_num_list[i] for i in range(3)])
        print(f"执行操作：看牌 当前手牌:{hand_cards} 组合:{cardtype.value} 牌力：{quality.value}")
        if self.game.leave_only_duizi() and quality.code >= MyCardsEnum.DUIZI_A.code:
            log("剩下的玩家 看牌比牌胜利是对子 加注一次")
            self.add_bet()
            self.game.max_follow = 0
            return
        
        if quality.code < MyCardsEnum.KHUA.code:
            if DEBUG_MODE:
                logger.info(f"【触发逻辑】看到烂牌")
            self.window.click(PositionConstant.ABANDON_CLICK_POS)
            print(f"执行操作：弃牌")
            self.game.end()
            return
        if quality.code >= MyCardsEnum.BAOZI.code:
            log("豹子 无限加注")
            if DEBUG_MODE:
                logger.info(f"【触发逻辑】看牌后获得豹子 加注后 无限草")
            self.add_bet()
            self.game.max_follow = 999
            return
        else:
            self.compare()
            if self.game.round != 1:
                self.game.end()
            
        
        self.window.click(PositionConstant.ABANDON_CLICK_POS)
        print(f"执行操作：弃牌")
        self.game.end()
            
    def compare(self):
        # 第一回合比不了牌 只能先跟注一手
        if self.game.round == 1:
            money = self.processor.get_money(self.image)
            if money > 0 and money < self.game.my_next_bet:
                print(f"钱不够了 执行操作：孤独一掷")
                self.compare()
                self.game.end()
            else:
                print("第一回合无法比牌 先跟注一手")
                self.follow()
                self.game.max_follow = 0
            return

        while (
            self.processor.check_game_status(self.window.screenshot())
            != GameStatusEnum.STOP
        ):
            self.window.click(PositionConstant.COMPARE_CLICK_POS)
            sleep(0.5)
            # 按顺序随便找一个能比的比牌
            for i in range(4):
                if (
                    self.game.player_status[i] == PlayerStatusEnum.LOOKED
                    or self.game.player_status[i] == PlayerStatusEnum.FOLLOWING
                ):
                    self.window.click(PositionConstant.PLAYER_AVATOR_POS[i])
                    sleep(0.3)
            print(f"执行操作：比牌一次")
    
    def add_bet(self):
        print("准备加注")
        self.window.click(PositionConstant.ADD_CLICK_POS)
        sleep(0.3)
        self.window.click(PositionConstant.ADD_7_CLICK_POS)
        self.game.bet += 7
        print(f"执行操作：加注(最大)")

    def run_test(self):
        pass
    
def main():
    try:
        login()
        printer = MoneyPrinter()
        printer.run_pro()
    except Exception as e:
        print(f"An error occurred: {e}")
        exec_str = 'money:' + str(printer.record[-1] if len(printer.record) > 0 else -1) + '\n'
        exec_str += traceback.format_exc()
        send_email(
            receiver_email="904399787@qq.com",
            body=str(exec_str),
            subject=f"【{config.get_nikename()}】运行错误",
        )
        send_email(
            receiver_email="736045262@qq.com",
            body=str(exec_str),
            subject=f"【{config.get_nikename()}】运行错误",
        )
        traceback.print_exc()
    finally:
        input("按Enter键退出...") 


if __name__ == "__main__":
    multiprocessing.freeze_support()
    print('系统开始启动.....')
    main()

