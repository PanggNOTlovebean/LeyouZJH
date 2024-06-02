from enum import Enum
VERSION = '1.41'

class PositionConstant1():
    RESOLUTION = (1080, 1920) 
    
    PLAYERS_POS = [
        [858, 733, 1209, 898],
        [369, 409, 550, 551],
        [423, 657, 609, 793],
        [1366, 407, 1552, 547],
        [1316, 660, 1493, 789],
    ]

    BET_POS = [
        [996, 905, 1069, 957],
        [428, 553, 483, 593],
        [490, 804, 542, 842],
        [1438, 558, 1490, 592],
        [1382, 804, 1435, 839],
    ]

    CARD_POS = [
        [871, 749, 910, 795],
        [983, 747, 1020, 795],
        [1092, 749, 1132, 798],
    ]
    # VPN图标位置
    VPN_ICON = [1700, 15, 1762, 61]
    
    # 看牌后 牌型提示位置
    CARD_PROMOTE_POS = [922, 835, 1144, 913]
    
    # bug位置需要重新点击
    BUG_POS = [965, 756]

    # 进入体验房 
    GO_TIYAN_HOUSE = [1014, 542]

    # 用户头像位置 用于比牌
    PLAYER_AVATOR_POS = [[294, 484], [352, 726], [1625, 483], [1568, 731]]

    # 钱包余额
    MONEY_BUTTON = [719, 866, 797, 903]
    # 开始游戏坐标
    START_CLICK_POS = [964, 940]
    # 看牌坐标
    LOOK_CLICK_POS = [1032, 810]
    
    # 检查是否是pk场景
    PK_POSITION = [151, 712]
    
    # 跟进按钮
    FOLLOW_BUTTON = [1505, 989, 1708, 1076]
    
    # 比牌按钮
    COMPARE_BUTTON = [1306, 998, 1500, 1077]
    # 加注按钮
    ADD_BUTTON = [1110, 993, 1306, 1077]
    # 弃牌按钮
    ABANDON_BUTTON = [54, 989, 256, 1079]

    # 跟注坐标
    FOLLOW_CLICK_POS = [1609, 1037]
    # 比牌坐标
    COMPARE_CLICK_POS = [1402, 1035]
    # 加注坐标
    ADD_CLICK_POS = [1201, 1039]
    # 弃牌坐标
    ABANDON_CLICK_POS = [148, 1031]

    # 加注筹码坐标
    ADD_7_CLICK_POS = [1206, 1002]
    # 灯光位置 用于查看当前玩家
    LIGHT_POS = [[962, 397], [948, 389], [950, 394], [974, 388], [969, 390]]

    @classmethod
    def get_status_enum_by_code(cls, code):
        for status in cls:
            if status.code == code:
                return status
        raise ValueError("Invalid code")

class CardsCombEnum(Enum):
    EORROR = (-2, "检测失败")
    TESHU = (-1, "特殊")
    GAOPAI = (0, "高牌")
    DUIZI = (1, "对子")
    SHUNZI = (2, "顺子")
    JINHUA = (3, "金花")
    TONGHUASHUN = (4, "同花顺")
    BAOZI = (5, "豹子")
    
    def __init__(self, code, value):
        self._code = code
        self._value = value

    @property
    def code(self):
        return self._code

    @property
    def value(self):
        return self._value

    @classmethod
    def get_status_enum_by_code(cls, code):
        for status in cls:
            if status.code == code:
                return status
        raise ValueError("Invalid code")

class PlayerStatusEnum(Enum):
    NONE = (0, "-")
    FOLLOWING = (1, "跟注")
    LOOKED = (2, "已看牌")
    LOOSE = (3, "比牌失败")
    ABANDON = (4, "弃牌")

    def __init__(self, code, value):
        self._code = code
        self._value = value

    @property
    def code(self):
        return self._code

    @property
    def value(self):
        return self._value

    @classmethod
    def get_status_enum_by_code(cls, code):
        for status in cls:
            if status.code == code:
                return status
        raise ValueError("Invalid code")

class GameStatusEnum(Enum):
    STOP = (0, "游戏尚未开始")
    WATING = (1, "等待我的回合")
    MYTURN = (2, "我的回合")
    PK = (3, "PK状态")

    def __init__(self, code, value):
        self._code = code
        self._value = value

    @property
    def code(self):
        return self._code

    @property
    def value(self):
        return self._value

    @classmethod
    def get_status_enum_by_code(cls, code):
        for status in cls:
            if status.code == code:
                return status
        raise ValueError("Invalid code")

class MyCardsEnum(Enum):
    BAOZI = (6, "豹子")
    TONGHUASHN = (5, "同花顺")
    AHUA = (4, "A花")
    KHUA = (3, "K花")
    QHUA = (2, "Q花")
    JHUA = (1, "J花")
    BAD = (0, "垃圾")

    def __init__(self, code, value):
        self._code = code
        self._value = value

    @property
    def code(self):
        return self._code

    @property
    def value(self):
        return self._value

    @classmethod
    def get_status_enum_by_code(cls, code):
        for status in cls:
            if status.code == code:
                return status
        raise ValueError("Invalid code")
