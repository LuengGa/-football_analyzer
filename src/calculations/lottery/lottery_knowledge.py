"""
竞彩足球和北京单场官方规则知识库
=====================================

单一真实来源 (Single Source of Truth)
基于中国体彩网官方规则核查 (2025年最新)

核心原则:
1. 竞彩足球和北京单场是完全独立的两种彩种
2. 玩法互不干预，但支持的联赛有重叠也有独有部分
3. 所有规则必须与官方保持一致
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


def _flatten_leagues(league_dict: Dict[str, List[str]]) -> List[str]:
    """将联赛字典展平为列表"""
    result = []
    for leagues in league_dict.values():
        result.extend(leagues)
    return result


@dataclass
class PlayTypeDetail:
    """玩法详情"""
    name: str
    options: List[str]
    description: str
    option_count: int = 0
    is_mixed: bool = False
    special_rules: Dict[str, Any] = field(default_factory=dict)


class LotteryKnowledge:
    """
    竞彩足球和北京单场官方规则知识库

    使用方式:
        knowledge = LotteryKnowledge()
        jingcai = knowledge.get_lottery("JINGCAI")
        rules = knowledge.query_rules("BEIDAN", "让球胜平负")
    """

    SOURCE = "中国体彩网官方规则 (2025年核查)"
    LAST_UPDATED = "2025-05-12"

    JINGCAI_LEAGUES = {
        "欧洲": [
            "英超", "西甲", "意甲", "德甲", "法甲",  # 五大联赛
            "欧冠", "欧罗巴", "欧协联",  # 三大欧战
            "英冠", "英甲", "足总杯", "联赛杯",
            "德乙", "西乙", "意乙",
            "荷甲", "荷乙", "葡超", "瑞超", "挪超",
        ],
        "亚洲": [
            "日职(J1)", "日乙(J2)", "韩职(K1)", "K2联赛",
            "澳超", "沙特联",
        ],
        "其他": [
            "美职联", "解放者杯",
        ],
        "篮球": ["NBA", "CBA", "美职篮"],
        "冰球": ["NHL"],
    }

    BEIDAN_LEAGUES = {
        "重叠赛事": [
            "英超", "西甲", "意甲", "德甲", "法甲",  # 五大联赛
            "英冠", "德乙", "西乙", "意乙",
            "日职(J1)", "日乙(J2)", "韩职(K1)", "K2联赛", "澳超",
            "挪超", "瑞超", "芬超", "丹超",
        ],
        "独有赛事_低级别联赛": [
            "奥乙", "瑞士甲", "波兰甲", "希腊超",
            "冰岛超", "罗甲", "捷甲", "苏冠",
            "爱超", "爱甲", "丹甲", "瑞甲", "挪甲",
            "芬甲", "瑞典甲", "瑞典超", "葡超", "荷乙",
        ],
        "独有赛事_特殊": [
            "澳超独有比赛(中央海岸水手等)",
            "各级国家队比赛",
            "非洲杯", "女足比赛",
        ],
    }

    JINGCAI_CONFIG = {
        "id": "JINGCAI",
        "name": "竞彩足球",
        "full_name": "中国体育彩票竞彩足球游戏",

        "leagues": JINGCAI_LEAGUES,
        "league_flat_list": _flatten_leagues(JINGCAI_LEAGUES),

        "return_rate": 0.69,
        "return_rate_detail": "68%返奖奖金 + 1%调节基金",
        "max_legs": 8,
        "handicap_type": "integer",
        "handicap_type_detail": "整数让球 (1, 2, 3...)",

        "bonus_limits": {
            "2_3_legs": 200000.0,
            "4_5_legs": 500000.0,
            "6_plus_legs": 1000000.0,
        },
        "tax_threshold": 10000.0,
        "tax_rate": 0.80,
        "minimum_bonus": 2.0,

        "sales_region": "全国",
        "sales_region_detail": "全国体彩网点销售",

        "betting_rules": {
            "过关方式": ["M串1 (2×1~8×1)", "自由过关", "M串N容错过关"],
            "复式投注": "支持同一场次选择多个选项",
            "单关赔率": "浮动赔率",
            "过关赔率": "固定赔率",
            "奖金公式": "2元 × 赔率连乘 × 倍数",
            "单注保底": "2元 (不足由调节基金补足)",
            "单注封顶": "2-3关20万, 4-5关50万, 6关及以上100万",
            "个人所得税": "单注≥1万扣20%",
            "混合过关规则": "可将胜平负、让球胜平负、总进球、比分、半全场混合串关，同一场次不可混合",
        },

        "play_types": {
            "胜平负": {
                "name": "胜平负",
                "options": ["胜", "平", "负"],
                "option_count": 3,
                "description": "竞猜全场90分钟（含伤停补时）主队的胜、平、负结果",
                "is_independent_play": True,
                "can_mix": True,
            },
            "让球胜平负": {
                "name": "让球胜平负",
                "options": ["胜", "平", "负"],
                "option_count": 3,
                "description": "竞猜主队加减让球数后的胜平负，让球为整数",
                "is_independent_play": True,
                "can_mix": True,
                "special_rules": {
                    "让球类型": "整数让球",
                    "让球范围": "让1球、让2球、让3球等",
                },
            },
            "比分": {
                "name": "比分",
                "options": [
                    "0:0", "0:1", "0:2", "0:3", "0:4", "0:5+",
                    "1:0", "1:1", "1:2", "1:3", "1:4", "1:5+",
                    "2:0", "2:1", "2:2", "2:3", "2:4", "2:5+",
                    "3:0", "3:1", "3:2", "3:3", "3:4", "3:5+",
                    "4:0", "4:1", "4:2", "4:3", "4:4", "4:5+",
                    "5+:0", "5+:1", "5+:2", "5+:3", "5+:4", "5+:5+",
                ],
                "option_count": 31,
                "description": "竞猜具体比分",
                "is_independent_play": True,
                "can_mix": True,
                "special_rules": {
                    "最大过关": "3串1",
                },
            },
            "总进球": {
                "name": "总进球",
                "options": ["0", "1", "2", "3", "4", "5", "6", "7+"],
                "option_count": 8,
                "description": "竞猜全场主客队总进球数",
                "is_independent_play": True,
                "can_mix": True,
            },
            "半全场": {
                "name": "半全场",
                "options": ["胜胜", "胜平", "胜负", "平胜", "平平", "平负", "负胜", "负平", "负负"],
                "option_count": 9,
                "description": "竞猜半场和全场的结果组合",
                "is_independent_play": True,
                "can_mix": True,
                "special_rules": {
                    "最大过关": "3串1",
                },
            },
            "混合过关": {
                "name": "混合过关",
                "options": ["混合"],
                "option_count": 0,
                "description": "将胜平负、让球胜平负、总进球、比分、半全场混合串关",
                "is_independent_play": False,
                "can_mix": False,
                "special_rules": {
                    "限制": "同一场比赛不可选择多个玩法",
                    "可选玩法": ["胜平负", "让球胜平负", "比分", "总进球", "半全场"],
                    "最大场次": 8,
                },
            },
        },
    }

    BEIDAN_CONFIG = {
        "id": "BEIDAN",
        "name": "北京单场",
        "full_name": "中国体育彩票北京单场游戏",

        "leagues": BEIDAN_LEAGUES,
        "league_flat_list": _flatten_leagues(BEIDAN_LEAGUES),

        "return_rate": 0.65,
        "return_rate_detail": "固定65%返奖率",
        "max_legs": 15,
        "handicap_type": "fraction",
        "handicap_type_detail": "小数让球 (0.5, 0/0.5, 0.5/1...)",

        "bonus_limits": {
        },
        "tax_threshold": 10000.0,
        "tax_rate": 0.80,
        "minimum_bonus": 2.0,

        "sales_region": "京津粤",
        "sales_region_detail": "仅北京、天津、广东联网销售",

        "betting_rules": {
            "过关方式": ["M串1"],
            "复式投注": "支持同一场次选择多个选项",
            "单关赔率": "浮动SP值",
            "过关赔率": "浮动SP值",
            "奖金公式": "2元 × SP值连乘 × 65% × 倍数",
            "单注保底": "2元",
            "个人所得税": "单注≥1万扣20%",
        },

        "play_types": {
            "胜平负": {
                "name": "胜平负",
                "options": ["胜", "平", "负"],
                "option_count": 3,
                "description": "竞猜全场90分钟（含伤停补时）主队胜平负，含让球选项",
                "is_independent_play": True,
                "can_mix": True,
                "special_rules": {
                    "让球类型": "小数让球",
                    "让球范围": ["让0.5球", "让0/0.5球", "让0.5/1球", "让1球", "让1/1.5球", "让1.5球"],
                },
            },
            "上下单双": {
                "name": "上下单双",
                "options": ["上单", "上双", "下单", "下双"],
                "option_count": 4,
                "description": "竞猜总进球数奇偶和上下盘组合",
                "is_independent_play": True,
                "can_mix": True,
                "special_rules": {
                    "上": "主队进球 > 客队进球",
                    "下": "主队进球 ≤ 客队进球",
                    "单": "总进球数为奇数",
                    "双": "总进球数为偶数",
                },
            },
            "比分": {
                "name": "比分",
                "options": [
                    "0:0", "0:1", "0:2", "0:3", "0:4", "0:5+",
                    "1:0", "1:1", "1:2", "1:3", "1:4", "1:5+",
                    "2:0", "2:1", "2:2", "2:3", "2:4", "2:5+",
                    "3:0", "3:1", "3:2", "3:3", "3:4", "3:5+",
                    "4:0", "4:1", "4:2", "4:3", "4:4", "4:5+",
                    "5+:0", "5+:1", "5+:2", "5+:3", "5+:4", "5+:5+",
                ],
                "option_count": 31,
                "description": "竞猜具体比分",
                "is_independent_play": True,
                "can_mix": True,
            },
            "半全场": {
                "name": "半全场",
                "options": ["胜胜", "胜平", "胜负", "平胜", "平平", "平负", "负胜", "负平", "负负"],
                "option_count": 9,
                "description": "竞猜半场和全场的结果组合",
                "is_independent_play": True,
                "can_mix": True,
            },
            "总进球": {
                "name": "总进球",
                "options": ["0", "1", "2", "3", "4", "5", "6", "7+"],
                "option_count": 8,
                "description": "竞猜全场主客队总进球数",
                "is_independent_play": True,
                "can_mix": True,
            },
            "胜负过关": {
                "name": "胜负过关",
                "options": ["胜", "负"],
                "option_count": 2,
                "description": "只有胜负两个选项，无平局",
                "is_independent_play": True,
                "can_mix": True,
                "special_rules": {
                    "无平局": True,
                    "让球": "必须带0.5小数让球消除平局",
                    "特点": "类似于滚球盘，消除平局选项",
                },
            },
        },
    }

    def __init__(self):
        self._lotteries = {
            "JINGCAI": self.JINGCAI_CONFIG,
            "BEIDAN": self.BEIDAN_CONFIG,
        }

    def get_lottery(self, lottery_type: str) -> Dict[str, Any]:
        """获取指定彩种的完整配置"""
        lottery_type = lottery_type.upper()
        if lottery_type not in self._lotteries:
            raise ValueError(f"未知彩种: {lottery_type}，必须是 JINGCAI 或 BEIDAN")
        return self._lotteries[lottery_type]

    def query_rules(self, lottery_type: str, play_type: Optional[str] = None) -> Dict[str, Any]:
        """
        查询规则

        Args:
            lottery_type: JINGCAI 或 BEIDAN
            play_type: 可选，指定玩法名称

        Returns:
            规则字典
        """
        lottery = self.get_lottery(lottery_type)

        if play_type is None:
            return lottery

        play_type = play_type.strip()
        play_types = lottery.get("play_types", {})

        if play_type in play_types:
            return {
                "lottery": lottery["name"],
                "lottery_id": lottery["id"],
                "play_type": play_type,
                **play_types[play_type],
            }

        for pt_name, pt_config in play_types.items():
            if pt_name in play_type or play_type in pt_name:
                return {
                    "lottery": lottery["name"],
                    "lottery_id": lottery["id"],
                    "play_type": pt_name,
                    **pt_config,
                }

        raise ValueError(f"未知玩法: {play_type}，在 {lottery['name']} 中不存在")

    def get_leagues(self, lottery_type: str, overlap_only: bool = False) -> List[str]:
        """
        获取支持的联赛列表

        Args:
            lottery_type: JINGCAI 或 BEIDAN
            overlap_only: 是否只返回与另一种彩种重叠的联赛
        """
        lottery = self.get_lottery(lottery_type)

        if overlap_only:
            other_type = "BEIDAN" if lottery_type == "JINGCAI" else "JINGCAI"
            other = self.get_lottery(other_type)
            return list(set(lottery["league_flat_list"]) & set(other["league_flat_list"]))

        return lottery["league_flat_list"]

    def compare_lotteries(self) -> Dict[str, Any]:
        """对比两种彩种的差异"""
        jingcai = self.get_lottery("JINGCAI")
        beidan = self.get_lottery("BEIDAN")

        jingcai_leagues = set(jingcai["league_flat_list"])
        beidan_leagues = set(beidan["league_flat_list"])

        return {
            "竞彩足球": {
                "name": jingcai["name"],
                "联赛数量": len(jingcai_leagues),
                "返奖率": f"{jingcai['return_rate']*100}%",
                "最大串关": f"{jingcai['max_legs']}关",
                "玩法数量": len(jingcai["play_types"]),
                "独有玩法": ["混合过关"],
                "独有联赛": list(jingcai_leagues - beidan_leagues),
            },
            "北京单场": {
                "name": beidan["name"],
                "联赛数量": len(beidan_leagues),
                "返奖率": f"{beidan['return_rate']*100}%",
                "最大串关": f"{beidan['max_legs']}关",
                "玩法数量": len(beidan["play_types"]),
                "独有玩法": ["上下单双", "胜负过关"],
                "独有联赛": list(beidan_leagues - jingcai_leagues),
            },
            "重叠联赛": list(jingcai_leagues & beidan_leagues),
            "差异说明": {
                "让球": f"竞彩={jingcai['handicap_type_detail']}，北单={beidan['handicap_type_detail']}",
                "玩法": "竞彩独有混合过关，北单独有上下单双和胜负过关",
                "销售": f"竞彩={jingcai['sales_region']}，北单={beidan['sales_region']}",
            },
        }


LOTTERY_KNOWLEDGE = LotteryKnowledge()


def get_lottery_knowledge() -> LotteryKnowledge:
    """获取彩票知识库单例"""
    return LOTTERY_KNOWLEDGE
