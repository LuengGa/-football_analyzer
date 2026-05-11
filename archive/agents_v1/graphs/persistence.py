from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os
import time


class MemoryPersistence:
    """
    持久化记忆系统
    
    保存历史决策到文件系统
    """
    
    def __init__(self, memory_dir: str = "memory/history"):
        self.memory_dir = memory_dir
        os.makedirs(self.memory_dir, exist_ok=True)
        
        # 今日文件
        today = datetime.now().strftime("%Y%m%d")
        self.history_file = os.path.join(self.memory_dir, f"history_{today}.json")
        self.decision_index_file = os.path.join(self.memory_dir, "decision_index.json")
        
        # 索引加载
        self._load_index()
    
    def _load_index(self) -> Dict:
        """加载决策索引"""
        if os.path.exists(self.decision_index_file):
            try:
                with open(self.decision_index_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_index(self, index: Dict):
        """保存决策索引"""
        with open(self.decision_index_file, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    
    def save_decision(self, decision_entry: Dict) -> str:
        """保存单个决策到文件"""
        decision_id = decision_entry.get("decision_id", f"DEC_{int(time.time())}")
        entry = decision_entry.copy()
        entry["decision_id"] = decision_id
        entry["saved_at"] = datetime.now().isoformat()
        
        # 保存到今日文件
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except:
                history = []
        else:
            history = []
        
        history.append(entry)
        
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        
        # 更新索引
        index = self._load_index()
        index[decision_id] = {
            "match_id": entry.get("match_id"),
            "date": datetime.now().strftime("%Y%m%d"),
            "file": self.history_file,
            "timestamp": datetime.now().isoformat()
        }
        self._save_index(index)
        
        print(f"   -> 💾 [Persistence] 决策已保存到 {self.history_file}")
        return decision_id
    
    def load_recent_decisions(self, limit: int = 10) -> List[Dict]:
        """加载最近的决策"""
        all_decisions = []
        
        # 加载今日文件
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    all_decisions.extend(json.load(f))
            except:
                pass
        
        return all_decisions[-limit:]
    
    def load_decision_by_match(self, match_id: str) -> Optional[Dict]:
        """根据比赛ID加载决策"""
        index = self._load_index()
        for decision_id, info in index.items():
            if info.get("match_id") == match_id:
                if os.path.exists(info.get("file")):
                    try:
                        with open(info.get("file"), "r", encoding="utf-8") as f:
                            history = json.load(f)
                            for entry in history:
                                if entry.get("match_id") == match_id:
                                    return entry
                    except:
                        pass
        return None
