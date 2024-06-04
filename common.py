from enum import Enum
VERSION = '1.41'

class PositionConstant():
    RESOLUTION = (1080, 1920) 
    
    BET_POS = [
        [741, 885, 832, 914],
        [502, 533, 591, 561],
        [329, 794, 446, 817],
        [1318, 534, 1415, 562],
        [1509, 795, 1599, 818],
    ]
    
    PLAYERS_POS = [
        [-1, -1, -1, -1],
        [497, 391, 611, 423],
        [335, 651, 452, 682],
        [1316, 393, 1424, 420],
        [1507, 651, 1616, 682],
    ]
        
    CARD_POS = [
        [864, 762, 899, 800],
        [981, 762, 1017, 802],
        [1098, 762, 1132, 798],
    ]
    
    PLAYER_AVATOR_POS = [[544, 476], [392, 742], [1360, 485], [1572, 739]]
    
    # VPN图标位置
    VPN_ICON = [1700, 15, 1762, 61]
    
    # 看牌后 牌型提示位置
    CARD_PROMOTE_POS = [922, 852, 1130, 902]
    
    #
    TOT_BET_LABEL = [948, 566, 1007, 605]
    
    MONEY_BUTTON =  [741, 885, 832, 914]
    # 开始游戏坐标
    START_CLICK_POS = [911, 939]
    
    AUTO_POS = [959, 1050]
    CANCEL_AUTO_POS = [864, 1024]
    
    # 进入体验房
    GO_TIYAN_HOUSE = [1014, 542]
    
    # 加注位置
    ADD_POSITION = [1091,1045]
    
    PK_POSITION = [787, 378]
    
    ROUND = [885, 512, 1030, 564]
    
    # 跟进按钮
    FOLLOW_BUTTON = [1607, 965, 1899, 1059]
    
    # 比牌按钮
    COMPARE_BUTTON = [1307, 963, 1596, 1059]
    # 加注按钮
    ADD_BUTTON = [997, 965, 1291, 1062]
    # 弃牌按钮
    ABANDON_BUTTON = [694, 962, 988, 1058]
    
    # 跟注坐标
    FOLLOW_CLICK_POS = [1760, 1013]
    # 比牌坐标
    COMPARE_CLICK_POS = [1448, 1012]
    # 加注坐标
    ADD_CLICK_POS = [1145, 1012]
    # 弃牌坐标
    ABANDON_CLICK_POS = [837, 1012]
    # 看牌坐标
    LOOK_CLICK_POS = [1044, 837]
    # 加注筹码坐标
    ADD_7_CLICK_POS = [1364, 835]
    
    

    
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
    BAOZI = (11, "豹子")
    TONGHUASHN_A = (10, "A同花顺")
    TONGHUASHN_K = (9, "K同花顺")
    TONGHUASHN_Q = (8, "Q同花顺")
    TONGHUASHN = (7, "J以下同花顺")
    AHUA = (6, "A花")
    KHUA = (5, "K花")
    QHUA = (4, "Q花")
    JHUA = (3, "J花")
    HUA10 = (2, "10花")
    HUA9 = (1, "9花")
    SHUNZI = (0, "顺子")
    DUIZI_A = (-1, "对A")
    BAD = (-2, "垃圾")

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



