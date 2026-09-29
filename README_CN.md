# EdgeSafe Vision

[![CI](https://github.com/Yazhou-Li/edgesafe-vision/actions/workflows/ci.yml/badge.svg)](https://github.com/Yazhou-Li/edgesafe-vision/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/Yazhou-Li/edgesafe-vision)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](pyproject.toml)

> 面向真实多摄像头部署的开源边缘 AI 安全监测、告警、诊断与验收工具集。

EdgeSafe Vision 由 **Yazhou Li** 维护。它把真实边缘 AI 交付中的工程经验，整理成开发者、FDE、解决方案工程师、集成商和实施团队可以直接复用的代码、诊断工具、测试和文档。

项目关注的不是“再训练一个模型”，而是完整交付链路：

**摄像头 → AI 推理 → 事件 → 业务规则 → 报警 → 操作反馈 → 验收**

## 为什么要做这个项目

很多视觉 AI Demo 到“检测到 person”就结束了，但真实现场还要继续解决：

- 摄像头画面是不是真的新鲜；
- 视频与 AI 框是否还同步；
- 超员是否应该持续 N 秒才报警；
- 条件恢复后报警如何关闭；
- Windows / Linux 重启后配置是否还能保持；
- 语音和告警是否真的到达操作人员；
- 出问题后如何快速拿到可验证证据，而不是靠猜。

EdgeSafe Vision 把这些“模型之外”的最后一公里问题，做成可以复用和测试的工程资产。

## 当前已开源

- 人员超员规则引擎：阈值、持续时间、冷却
- 重点区域入侵规则：归一化 Polygon、停留时间、Track 状态
- 视频 / AI 元数据新鲜度监控：识别旧画面、旧框、时序偏差
- 报警生命周期：打开、确认、恢复
- 统一事件模型：把 Frigate / MQTT / Webhook / 自定义检测结果转换为统一规则输入
- Frigate tracked-object 事件与摄像头状态 MQTT 适配器
- EdgeSafe Doctor：跨平台、只读、无第三方依赖的诊断 CLI，支持检查计划与结构化证据包
- Windows / Ubuntu 诊断脚本
- 脱敏规则示例和 Demo
- 回归测试与 GitHub Actions CI
- 架构文档、验收清单和真实交付经验脱敏案例

## 适合谁

如果你在做下面这些事情，这个项目会更有价值：

- 边缘 AI / 视频分析；
- 智慧零售、仓储、工业或安全监测；
- 多摄像头事件与报警系统；
- Frigate / MQTT / Webhook 事件链；
- Windows / Linux 边缘设备现场交付；
- AI 项目的可验证验收与故障诊断。

## 快速开始

需要 Python 3.10+。

```bash
git clone https://github.com/Yazhou-Li/edgesafe-vision.git
cd edgesafe-vision
python -m pip install -e .
python -m unittest discover -s tests -v
python examples/demo.py
python examples/adapter_demo.py
edgesafe-doctor --http http://127.0.0.1:5000
edgesafe-doctor --config examples/doctor.example.json --evidence evidence.json
```

更完整的上手路径见：[Getting Started](docs/GETTING_STARTED.md)；适配器契约和示例见：[Integrations](docs/INTEGRATIONS.md)。

所有示例都使用公开、合成或脱敏数据，不依赖客户生产环境。

## 最小规则示例

```python
from edgesafe.rules import OccupancyRule, OccupancyRuleEngine

rule = OccupancyRule(
    rule_id="entrance-overcrowding",
    camera_id="cam-01",
    threshold=4,
    duration_seconds=10,
    cooldown_seconds=60,
)

engine = OccupancyRuleEngine()

print(engine.evaluate(rule, person_count=5, timestamp=0))
print(engine.evaluate(rule, person_count=5, timestamp=10))
```

时间戳由调用方传入，所以持续时间、冷却和恢复逻辑可以稳定复现和测试。

## 项目原则

**证据优先。** 进程启动成功，不等于操作人员真的收到了报警。

**交付优先于 Demo。** 视频、规则、报警、语音、认证和重启保持必须能一起工作。

**默认保护隐私。** 生产数据、客户信息和生产凭据不进入公开仓库。

**小步可验证。** 修复尽量保持范围小、可测试、可回归。

## 项目阶段

EdgeSafe Vision 当前仍处于早期开源阶段。已有模块可以运行并有测试，但它不是经过认证的生命安全系统，也不是开箱即用的完整商业产品。

用于真实环境时，仍需要由实施方完成现场安全、权限、网络、法规和验收验证。

## 安全

请不要在 Issue、日志、示例配置或 Pull Request 中提交账号密码、令牌、私钥、客户信息、真实私网信息、生产截图或其他敏感数据。

安全问题和负责任披露方式请参见 [SECURITY.md](SECURITY.md)。

## 参与项目

欢迎参与改进：

- Bug：使用结构化 Bug Report；
- 可复用的新需求：提交 Feature Request；
- 代码或文档：先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)；
- 部署与集成支持：参见 [SUPPORT.md](SUPPORT.md)。

项目尤其欢迎：Frigate / MQTT / Webhook 适配、跨平台诊断、可复现测试、现场验收方法以及隐私友好的 Demo。

## 路线图

见 [ROADMAP.md](ROADMAP.md)。

## License

Apache License 2.0。第三方组件继续遵循其原始许可证，参见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 维护者

**Yazhou Li**  
GitHub: [github.com/Yazhou-Li](https://github.com/Yazhou-Li)
