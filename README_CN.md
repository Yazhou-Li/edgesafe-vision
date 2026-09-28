# EdgeSafe Vision

> 面向真实部署的边缘 AI 安全监测与预警参考平台。

EdgeSafe Vision 是由 **Yazhou Li** 维护的开源项目，来源于真实边缘 AI 工程实践，但公开仓库不包含客户数据、生产凭据、私钥或真实运行配置。

项目关注的不是“训练一个新模型”，而是完整交付链路：

**摄像头 → AI 推理 → 事件 → 业务规则 → 报警 → 操作反馈 → 验收**

## 当前已开源

- 人员超员规则引擎：阈值、持续时间、冷却
- 重点区域入侵规则：归一化 Polygon、停留时间、Track 状态
- 视频 / AI 元数据新鲜度监控：识别旧画面、旧框、时序偏差
- 报警生命周期：打开、确认、恢复
- 统一事件模型：把 Frigate / MQTT / Webhook / 自定义检测结果转换为同一规则输入
- EdgeSafe Doctor：跨平台只读诊断 CLI
- Windows / Ubuntu 诊断脚本
- 脱敏规则示例和 Demo
- 回归测试与 GitHub Actions CI
- 架构文档、验收清单和真实交付经验脱敏案例

## 为什么这个项目有价值

很多视觉 AI Demo 到“检测到 person”就结束了，但真实现场还需要解决：

- 摄像头是否长期稳定；
- 视频画面和 AI 框是否同步；
- 超员是否要持续 N 秒才报警；
- 人离开后报警如何恢复；
- 重点区域如何配置；
- 本地语音是否真的被现场听见；
- Windows / Ubuntu 重启后配置是否仍然有效；
- 出问题后如何快速拿到可验证证据。

EdgeSafe Vision 把这些“模型之外”的工程问题做成可复用的规则、诊断和验收资产。

## 快速开始

需要 Python 3.10+。

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python examples/demo.py
edgesafe-doctor --http http://127.0.0.1:5000
```

## 开源原则

这个仓库面向真正的开源社区，不是简历展示仓库。

公开内容优先满足三个标准：

1. 能实际运行或复现；
2. 对边缘 AI 开发、实施或运维有直接价值；
3. 不泄露客户、生产环境或安全敏感信息。

## 安全

请不要在 Issue、日志、示例配置或 Pull Request 中提交账号密码、令牌、个人信息、私有部署信息或其他敏感数据。

安全问题和负责任披露方式请参见 [SECURITY.md](SECURITY.md)。

## 支持

社区问题、Bug 和功能建议可以通过 GitHub 提交；仓库开启 Issues 后会统一维护。

组织级私有部署、系统集成或支持需求，参见 [Enterprise Support](docs/ENTERPRISE_SUPPORT.md)。

## 维护者

**Yazhou Li**  
GitHub: [github.com/Yazhou-Li](https://github.com/Yazhou-Li)
