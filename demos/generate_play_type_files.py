#!/usr/bin/env python3
"""
批量生成玩法文件
"""

import json
from pathlib import Path


def generate_jingcai_play_types():
    """生成竞彩玩法文件"""
    play_types = [
        {
            "id": "win_draw_loss",
            "name": "胜平负",
            "description": "竞猜全场90分钟（含伤停补时）主队的胜、平、负结果",
            "options": ["胜", "平", "负"],
            "max_legs": None,
            "is_independent": True,
            "can_mix": True,
            "content": "竞彩足球胜平负玩法：竞猜全场90分钟（含伤停补时）主队的胜、平、负结果。可选选项：胜, 平, 负。"
        },
        {
            "id": "handicap_win_draw_loss",
            "name": "让球胜平负",
            "description": "竞猜主队加减让球数后的胜平负，让球为整数",
            "options": ["胜", "平", "负"],
            "max_legs": None,
            "is_independent": True,
            "can_mix": True,
            "special_rules": {
                "让球类型": "整数让球",
                "让球范围": ["让1球", "让2球", "让3球等"]
            },
            "content": "竞彩足球让球胜平负玩法：竞猜主队加减让球数后的胜平负，让球为整数。可选选项：胜, 平, 负。让球类型：整数让球。让球范围：让1球、让2球、让3球等。"
        },
        {
            "id": "score",
            "name": "比分",
            "description": "竞猜具体比分",
            "options": ["0:0", "0:1", "0:2", "0:3", "0:4", "0:5+", "1:0", "1:1", "1:2", "1:3", "1:4", "1:5+", "2:0", "2:1", "2:2", "2:3", "2:4", "2:5+", "3:0", "3:1", "3:2", "3:3", "3:4", "3:5+", "4:0", "4:1", "4:2", "4:3", "4:4", "4:5+", "5+:0", "5+:1", "5+:2", "5+:3", "5+:4", "5+:5+"],
            "max_legs": 3,
            "is_independent": True,
            "can_mix": True,
            "content": "竞彩足球比分玩法：竞猜具体比分。可选选项：0:0, 0:1, 0:2, 0:3, 0:4, 0:5+, 1:0, 1:1, 1:2, 1:3, 1:4, 1:5+, 2:0, 2:1, 2:2, 2:3, 2:4, 2:5+, 3:0, 3:1, 3:2, 3:3, 3:4, 3:5+, 4:0, 4:1, 4:2, 4:3, 4:4, 4:5+, 5+:0, 5+:1, 5+:2, 5+:3, 5+:4, 5+:5+。最大过关：3串1。"
        },
        {
            "id": "total_goals",
            "name": "总进球",
            "description": "竞猜全场主客队总进球数",
            "options": ["0", "1", "2", "3", "4", "5", "6", "7+"],
            "max_legs": None,
            "is_independent": True,
            "can_mix": True,
            "content": "竞彩足球总进球玩法：竞猜全场主客队总进球数。可选选项：0, 1, 2, 3, 4, 5, 6, 7+。"
        },
        {
            "id": "half_full",
            "name": "半全场",
            "description": "竞猜半场和全场的结果组合",
            "options": ["胜胜", "胜平", "胜负", "平胜", "平平", "平负", "负胜", "负平", "负负"],
            "max_legs": 3,
            "is_independent": True,
            "can_mix": True,
            "content": "竞彩足球半全场玩法：竞猜半场和全场的结果组合。可选选项：胜胜, 胜平, 胜负, 平胜, 平平, 平负, 负胜, 负平, 负负。最大过关：3串1。"
        },
        {
            "id": "mixed_parlay",
            "name": "混合过关",
            "description": "将胜平负、让球胜平负、总进球、比分、半全场混合串关",
            "options": [],
            "max_legs": 8,
            "is_independent": False,
            "can_mix": False,
            "special_rules": {
                "限制": "同一场比赛不可选择多个玩法",
                "可选玩法": ["胜平负", "让球胜平负", "比分", "总进球", "半全场"]
            },
            "content": "竞彩足球混合过关玩法：将胜平负、让球胜平负、总进球、比分、半全场混合串关。限制：同一场比赛不可选择多个玩法。可选玩法：胜平负, 让球胜平负, 比分, 总进球, 半全场。最大场次：8。"
        }
    ]
    
    base_path = Path("data/knowledge/jingcai/play_types")
    
    for i, play_type in enumerate(play_types, 1):
        filename = f"{i:02d}_{play_type['id']}.json"
        filepath = base_path / filename
        
        play_type_data = {
            "version": "1.0",
            "lottery_type": "JINGCAI",
            "play_type": play_type["name"],
            **play_type,
            "importance": 0.9,
            "knowledge_chunk": {
                "id": f"jingcai_{play_type['id']}",
                "content": play_type["content"],
                "category": "jingcai",
                "play_type": play_type["name"],
                "importance": 0.9
            }
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(play_type_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 生成: {filename}")
    
    print(f"\n🎉 竞彩玩法文件生成完成！共 {len(play_types)} 个")


def generate_beidan_play_types():
    """生成北单玩法文件"""
    play_types = [
        {
            "id": "win_draw_loss",
            "name": "胜平负",
            "description": "竞猜全场90分钟（含伤停补时）主队胜平负，含让球选项",
            "options": ["胜", "平", "负"],
            "max_legs": None,
            "is_independent": True,
            "can_mix": True,
            "special_rules": {
                "让球类型": "小数让球",
                "让球范围": ["让0.5球", "让0/0.5球", "让0.5/1球", "让1球", "让1/1.5球", "让1.5球"]
            },
            "content": "北京单场胜平负玩法：竞猜全场90分钟（含伤停补时）主队胜平负，含让球选项。可选选项：胜, 平, 负。让球类型：小数让球。让球范围：让0.5球, 让0/0.5球, 让0.5/1球, 让1球, 让1/1.5球, 让1.5球。"
        },
        {
            "id": "over_under_odd_even",
            "name": "上下单双",
            "description": "竞猜总进球数奇偶和上下盘组合",
            "options": ["上单", "上双", "下单", "下双"],
            "max_legs": None,
            "is_independent": True,
            "can_mix": True,
            "special_rules": {
                "上": "主队进球 > 客队进球",
                "下": "主队进球 ≤ 客队进球",
                "单": "总进球数为奇数",
                "双": "总进球数为偶数"
            },
            "content": "北京单场上下单双玩法：竞猜总进球数奇偶和上下盘组合。可选选项：上单, 上双, 下单, 下双。上：主队进球 > 客队进球；下：主队进球 ≤ 客队进球；单：总进球数为奇数；双：总进球数为偶数。"
        },
        {
            "id": "score",
            "name": "比分",
            "description": "竞猜具体比分",
            "options": ["0:0", "0:1", "0:2", "0:3", "0:4", "0:5+", "1:0", "1:1", "1:2", "1:3", "1:4", "1:5+", "2:0", "2:1", "2:2", "2:3", "2:4", "2:5+", "3:0", "3:1", "3:2", "3:3", "3:4", "3:5+", "4:0", "4:1", "4:2", "4:3", "4:4", "4:5+", "5+:0", "5+:1", "5+:2", "5+:3", "5+:4", "5+:5+"],
            "max_legs": None,
            "is_independent": True,
            "can_mix": True,
            "content": "北京单场比分玩法：竞猜具体比分。可选选项：0:0, 0:1, 0:2, 0:3, 0:4, 0:5+, 1:0, 1:1, 1:2, 1:3, 1:4, 1:5+, 2:0, 2:1, 2:2, 2:3, 2:4, 2:5+, 3:0, 3:1, 3:2, 3:3, 3:4, 3:5+, 4:0, 4:1, 4:2, 4:3, 4:4, 4:5+, 5+:0, 5+:1, 5+:2, 5+:3, 5+:4, 5+:5+。"
        },
        {
            "id": "half_full",
            "name": "半全场",
            "description": "竞猜半场和全场的结果组合",
            "options": ["胜胜", "胜平", "胜负", "平胜", "平平", "平负", "负胜", "负平", "负负"],
            "max_legs": None,
            "is_independent": True,
            "can_mix": True,
            "content": "北京单场半全场玩法：竞猜半场和全场的结果组合。可选选项：胜胜, 胜平, 胜负, 平胜, 平平, 平负, 负胜, 负平, 负负。"
        },
        {
            "id": "total_goals",
            "name": "总进球",
            "description": "竞猜全场主客队总进球数",
            "options": ["0", "1", "2", "3", "4", "5", "6", "7+"],
            "max_legs": None,
            "is_independent": True,
            "can_mix": True,
            "content": "北京单场总进球玩法：竞猜全场主客队总进球数。可选选项：0, 1, 2, 3, 4, 5, 6, 7+。"
        },
        {
            "id": "win_loss",
            "name": "胜负过关",
            "description": "只有胜负两个选项，无平局",
            "options": ["胜", "负"],
            "max_legs": None,
            "is_independent": True,
            "can_mix": True,
            "special_rules": {
                "注意": "必须带0.5小数让球消除平局",
                "特点": "类似滚球盘，消除平局选项"
            },
            "content": "北京单场胜负过关玩法：只有胜负两个选项，无平局。注意：必须带0.5小数让球消除平局。特点：类似滚球盘，消除平局选项。可选选项：胜, 负。"
        }
    ]
    
    base_path = Path("data/knowledge/beidan/play_types")
    
    for i, play_type in enumerate(play_types, 1):
        filename = f"{i:02d}_{play_type['id']}.json"
        filepath = base_path / filename
        
        play_type_data = {
            "version": "1.0",
            "lottery_type": "BEIDAN",
            "play_type": play_type["name"],
            **play_type,
            "importance": 0.9,
            "knowledge_chunk": {
                "id": f"beidan_{play_type['id']}",
                "content": play_type["content"],
                "category": "beidan",
                "play_type": play_type["name"],
                "importance": 0.9
            }
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(play_type_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 生成: {filename}")
    
    print(f"\n🎉 北单玩法文件生成完成！共 {len(play_types)} 个")


def main():
    print("=" * 60)
    print("开始批量生成玩法文件")
    print("=" * 60)
    
    print("\n" + "=" * 60)
    print("竞彩玩法")
    print("=" * 60)
    generate_jingcai_play_types()
    
    print("\n" + "=" * 60)
    print("北单玩法")
    print("=" * 60)
    generate_beidan_play_types()
    
    print("\n" + "=" * 60)
    print("🎉 所有玩法文件生成完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
