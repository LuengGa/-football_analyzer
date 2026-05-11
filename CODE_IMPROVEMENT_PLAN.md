
# AFA 项目持续改进计划

## 已完成的修复和改进 (2026-05-11)

### 1. 已修复的关键问题

#### 1.1 修复 HTML 编码字符问题
- **问题**: `-&gt;` 被错误地编码在 Python 文件中，而不是使用正确的 `->`
- **修复文件**:
  - [augmented_data.py](file:///workspace/src/afa_v9/ai_augmented/augmented_data.py)
  - [augmented_memory.py](file:///workspace/src/afa_v9/ai_augmented/augmented_memory.py)
  - [core_upgrades.py](file:///workspace/src/afa_v9/ai_augmented/core_upgrades.py)
- **辅助工具**: 创建了 [fix_html_encoding.py](file:///workspace/fix_html_encoding.py) 用于批量修复

#### 1.2 修复数据合约导入问题
- **问题**: 测试文件无法导入 `NormalizedMatch` 等类，因为旧的模块路径不存在
- **修复**: 在 [data_contract.py](file:///workspace/src/core/data_contract.py) 中直接实现了这些数据类
- **结果**: `tests/unit/core/test_data_contract.py` 现在所有 3 个测试都通过

#### 1.3 格式化测试文件
- **操作**: 运行了 `black` 和 `isort` 来格式化所有测试文件
- **修复文件数量**: 40+ 个测试文件被重新格式化
- **结果**: 消除了大量 lint 警告

---

## 待完成的改进工作

### 优先级 1：高优先级

#### 2.1 类型注解问题
- **问题**: Mypy 报告了 844 个类型错误
- **建议改进方向**:
  - 逐步为核心模块添加完整的类型注解
  - 修复 `Optional[T]` 类型处理
  - 为第三方库添加 `type: ignore` 或安装对应的 stubs
  - 优先修复以下核心模块：
    - [src/afa_v9/backtest.py](file:///workspace/src/afa_v9/backtest.py)
    - [src/afa_v9/agents/](file:///workspace/src/afa_v9/agents/)
    - [src/core/mcp/adapter.py](file:///workspace/src/core/mcp/adapter.py)

#### 2.2 测试相关问题
- **缺少测试数据文件**: `INTEGRATED_COMPLETE_DATA.json` 缺失导致测试失败
  - 建议：创建最小化的测试数据或使用 mock 数据
  - 或在测试中添加 skip 条件
- **测试覆盖率**: 增加核心计算模块的测试覆盖
  - 优先：赔率计算、凯利公式、Elo 评分等

#### 2.3 模块间依赖清理
- **问题**: 一些模块引用了不存在的类或方法
  - 例如 `mcp/adapter.py` 中引用的 `DataSourceManager` 和 `KellyCriterion`
  - 需要检查并更新这些引用

### 优先级 2：中优先级

#### 2.4 代码质量改进
- **Flake8 警告**: 测试文件还有多个警告需要修复
  - 未使用的导入和变量
  - 过长的函数（C901 复杂度警告）
  - 建议：拆分 `test_pro_complete.py` 等复杂测试文件

#### 2.5 文档改进
- 补充缺失的 docstring
- 完善 API 文档
- 更新 README 中的项目结构说明

#### 2.6 架构清理
- 清理 `archive/` 目录中不再需要的旧文件
- 确保所有模块都在正确的位置

### 优先级 3：低优先级

#### 2.7 CI/CD 改进
- 设置 GitHub Actions 自动运行测试和 lint
- 添加 pre-commit hooks 强制执行代码格式
- 设置 mypy 作为 CI 的一部分

#### 2.8 性能优化
- 缓存经常使用的计算结果
- 优化大规模数据处理
- 添加性能监控

---

## 分阶段实施计划

### 阶段 1：稳定代码库（本周）
- ✅ 修复关键语法错误
- ✅ 修复导入路径问题
- ✅ 格式化代码
- 使核心测试能正常运行（跳过需要外部文件的测试）

### 阶段 2：类型安全（1-2 周）
- 为核心模块添加类型注解
- 配置 mypy 作为检查的一部分
- 逐步解决现有类型错误

### 阶段 3：测试完善（2-3 周）
- 创建缺失的测试数据或使用 mock
- 增加测试覆盖率
- 建立完整的集成测试

### 阶段 4：架构优化（持续）
- 清理模块依赖
- 完善代码文档
- 建立贡献指南

---

## 验证清单

在合并任何更改前，请验证以下内容：
- [ ] 架构检查通过 (`python scripts/check_architecture.py`)
- [ ] 代码格式化 (`black src tests scripts && isort src tests scripts`)
- [ ] Lint 检查通过 (`flake8 src tests scripts`)
- [ ] 类型检查通过 (`mypy src`)
- [ ] 相关测试通过
- [ ] 文档已更新

---

## 有用的命令

```bash
# 运行架构检查
python scripts/check_architecture.py

# 格式化代码
python -m black src tests scripts
python -m isort src tests scripts

# 代码质量检查
python -m flake8 src tests scripts --count --select=E9,F63,F7,F82 --show-source --statistics
python -m flake8 src tests scripts --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# 类型检查
python -m mypy src

# 运行测试
python -m pytest tests/ -xvs
python -m pytest tests/unit/core/ -x  # 仅核心单元测试
python -m pytest tests/ -k "not integration"  # 不运行集成测试
```
