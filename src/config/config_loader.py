"""
Config Loader - 配置加载器
负责加载环境变量和配置文件
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional


def load_env_file(env_path: Optional[str] = None):
    """
    手动加载 .env 文件到环境变量
    
    Args:
        env_path: .env 文件路径，默认为项目根目录的 .env
    """
    if env_path is None:
        env_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            ".env"
        )
    
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # 跳过注释和空行
                if not line or line.startswith("#"):
                    continue
                
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # 移除引号
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    os.environ[key] = value
                    print(f"[ConfigLoader] 加载环境变量: {key}")
    
    else:
        print(f"[ConfigLoader] 未找到 .env 文件: {env_path}")


def get_config(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    获取配置值
    
    Args:
        key: 配置键名
        default: 默认值
    
    Returns:
        配置值
    """
    return os.getenv(key, default)


def get_all_api_keys() -> Dict[str, Optional[str]]:
    """获取所有API Key"""
    return {
        "FOOTBALL_DATA_API_KEY": get_config("FOOTBALL_DATA_API_KEY"),
        "ODDS_API_KEY": get_config("ODDS_API_KEY"),
        "API_FOOTBALL_KEY": get_config("API_FOOTBALL_KEY"),
        "SPORTMONKS_API_KEY": get_config("SPORTMONKS_API_KEY"),
        "ODDS_API_IO_KEY": get_config("ODDS_API_IO_KEY"),
        "OPENWEATHERMAP_API_KEY": get_config("OPENWEATHERMAP_API_KEY"),
        "WEATHERAPI_KEY": get_config("WEATHERAPI_KEY")
    }


# 在模块加载时自动加载 .env 文件
load_env_file()


if __name__ == "__main__":
    print("测试配置加载器...")
    
    keys = get_all_api_keys()
    
    print("\n已加载的API Key:")
    for key, value in keys.items():
        if value:
            # 隐藏部分密钥内容
            masked = value[:8] + "*" * (len(value) - 8) if len(value) > 8 else "****"
            print(f"  {key}: {masked}")
        else:
            print(f"  {key}: 未配置")
