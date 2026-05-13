"""
Machine Learning Predictors
机器学习预测器模块

包含:
- Random Forest
- Gradient Boosting (XGBoost/LightGBM if available)
- Neural Networks
- Ensemble (Blending/Stacking)
"""

import sys
import os
import pickle
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .feature_engineering import MatchFeatures

@dataclass
class PredictionResult:
    """ML 预测结果"""
    home_win_prob: float = 0.0
    draw_prob: float = 0.0
    away_win_prob: float = 0.0
    confidence: float = 0.0
    model_name: str = ""
    feature_importance: Optional[Dict[str, float]] = None


class BasePredictor:
    """基础预测器"""
    
    def __init__(self, name: str):
        self.name = name
        self.is_trained = False
        self.model = None
    
    def train(self, X: np.ndarray, y: np.ndarray):
        raise NotImplementedError
    
    def predict_proba(self, features: MatchFeatures) -> PredictionResult:
        raise NotImplementedError
    
    def save(self, path: str):
        with open(path, 'wb') as f:
            pickle.dump(self, f)
    
    @staticmethod
    def load(path: str) -> 'BasePredictor':
        with open(path, 'rb') as f:
            return pickle.load(f)  # type: ignore[return-value,no-any-return]


class RandomForestPredictor(BasePredictor):
    """随机森林预测器"""
    
    def __init__(self, n_estimators: int = 200, max_depth: int = 15):
        super().__init__("RandomForest")
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.model: Optional[Any] = None
    
    def train(self, X: np.ndarray, y: np.ndarray):
        from sklearn.ensemble import RandomForestClassifier
        
        print(f"🎯 训练随机森林模型: {self.n_estimators} estimators...")
        
        self.model = RandomForestClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X, y)  # type: ignore[union-attr,attr-defined]
        self.is_trained = True
        print("✅ 随机森林训练完成")
    
    def predict_proba(self, features: MatchFeatures) -> PredictionResult:
        if not self.is_trained or not self.model:
            return PredictionResult(0.33, 0.33, 0.34, 0.0, self.name)
        
        X = features.to_array().reshape(1, -1)
        proba = self.model.predict_proba(X)[0]  # type: ignore[union-attr,attr-defined]
        
        # y = 0:客胜, 1:平局, 2:主胜
        away_win = proba[0]
        draw = proba[1]
        home_win = proba[2]
        
        confidence = max(home_win, draw, away_win)
        
        # 特征重要性
        feature_names = [
            'home_form', 'home_goals', 'home_conceded',
            'home_att', 'home_def', 'home_win%', 'home_draw%', 'home_loss%',
            'away_form', 'away_goals', 'away_conceded',
            'away_att', 'away_def', 'away_win%', 'away_draw%', 'away_loss%',
            'h2h_home', 'h2h_draw', 'h2h_away', 'h2h_hg', 'h2h_ag',
            'goal_diff_exp', 'form_diff', 'league_strength'
        ]
        
        feature_importance = dict(zip(
            feature_names,
            self.model.feature_importances_
        )) if hasattr(self.model, 'feature_importances_') else None
        
        return PredictionResult(
            home_win_prob=home_win,
            draw_prob=draw,
            away_win_prob=away_win,
            confidence=confidence,
            model_name=self.name,
            feature_importance=feature_importance
        )


class XGBoostPredictor(BasePredictor):
    """XGBoost 预测器 (如果可用)"""
    
    def __init__(self):
        super().__init__("XGBoost")
        self.model = None
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        try:
            import xgboost
            return True
        except ImportError:
            return False
    
    def train(self, X: np.ndarray, y: np.ndarray):
        if not self.available:
            print("⚠️ XGBoost not available, skipping...")
            return
            
        import xgboost as xgb
        
        print("🎯 训练 XGBoost 模型...")
        
        self.model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.05,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X, y)  # type: ignore[union-attr,attr-defined]
        self.is_trained = True
        print("✅ XGBoost 训练完成")
    
    def predict_proba(self, features: MatchFeatures) -> PredictionResult:
        if not self.available or not self.is_trained:
            return PredictionResult(0.33, 0.33, 0.34, 0.0, self.name)
        
        X = features.to_array().reshape(1, -1)
        proba = self.model.predict_proba(X)[0]  # type: ignore[union-attr,attr-defined]
        
        away_win = proba[0]
        draw = proba[1]
        home_win = proba[2]
        
        confidence = max(home_win, draw, away_win)
        
        return PredictionResult(
            home_win_prob=home_win,
            draw_prob=draw,
            away_win_prob=away_win,
            confidence=confidence,
            model_name=self.name
        )


class EnsemblePredictor(BasePredictor):
    """集成预测器 (Blending multiple models)"""
    
    def __init__(self, predictors: List[BasePredictor]):
        super().__init__("Ensemble")
        self.predictors = predictors
        self.weights = [1.0 / len(predictors) for _ in predictors]
    
    def train(self, X: np.ndarray, y: np.ndarray):
        for predictor in self.predictors:
            if not predictor.is_trained:
                predictor.train(X, y)
        self.is_trained = True
    
    def predict_proba(self, features: MatchFeatures) -> PredictionResult:
        results = [
            pred.predict_proba(features) 
            for pred in self.predictors 
            if pred.is_trained
        ]
        
        if not results:
            return PredictionResult(0.33, 0.33, 0.34, 0.0, self.name)
        
        # 加权平均
        home_win = sum(r.home_win_prob * w for r, w in zip(results, self.weights))
        draw = sum(r.draw_prob * w for r, w in zip(results, self.weights))
        away_win = sum(r.away_win_prob * w for r, w in zip(results, self.weights))
        
        confidence = max(home_win, draw, away_win)
        
        return PredictionResult(
            home_win_prob=home_win,
            draw_prob=draw,
            away_win_prob=away_win,
            confidence=confidence,
            model_name="Ensemble (" + ",".join([r.model_name for r in results]) + ")"
        )


class ModelTrainer:
    """模型训练和管理"""
    
    def __init__(self):
        self.models: Dict[str, BasePredictor] = {}
    
    def train_all(self, X: np.ndarray, y: np.ndarray):
        """训练所有可用模型"""
        
        rf = RandomForestPredictor()
        rf.train(X, y)
        self.models['random_forest'] = rf
        
        xgb = XGBoostPredictor()
        if xgb.available:
            xgb.train(X, y)
            self.models['xgboost'] = xgb
        
        if len(self.models) > 1:
            ensemble = EnsemblePredictor(list(self.models.values()))
            self.models['ensemble'] = ensemble
    
    def get_best_model(self) -> Optional[BasePredictor]:
        """获取最优模型（目前是集成模型）"""
        return self.models.get('ensemble', self.models.get('random_forest'))
