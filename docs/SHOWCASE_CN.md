# EdgeSafe Vision 三分钟可复现展示

这份展示给评审、贡献者和第一次接触项目的人使用。**不需要摄像头、不需要 GPU、不需要 MQTT Broker，也不需要任何生产账号或客户数据。**

EdgeSafe Vision 想证明的不是“AI 能识别人”，而是另一件更接近真实交付的问题：

> **真正有价值的 AI，不是模型输出了一次结果，而是输入到操作人员结果之间的整条链路可以被验证。**

## 1. 安装并验证

```bash
git clone https://github.com/Yazhou-Li/edgesafe-vision.git
cd edgesafe-vision
python -m pip install -e .
python -m unittest discover -s tests -v
```

测试通过，说明当前公开模块、确定性规则和示例与仓库当前版本保持一致。

## 2. 运行端到端合成流水线

```bash
python examples/end_to_end_demo.py
```

这一条命令实际跑过：

```text
合成事件
  → 统一 EdgeEvent
  → 超员规则
  → 报警生命周期
  → 可复现 Trace
```

仓库自带 8 条合成事件，最终应出现：

```text
SUMMARY events=8 alarms_opened=2 alarms_resolved=1
```

这比“检测到了 person”多走了几步：持续时间是否满足、什么时候真正触发、条件恢复后如何结束报警，都由可测试的状态变化来证明。

## 3. 运行只读部署诊断

基础检查：

```bash
edgesafe-doctor
```

使用检查计划并生成证据包：

```bash
edgesafe-doctor \
  --config examples/doctor.example.json \
  --evidence evidence.json
```

EdgeSafe Doctor 做的是有边界的只读观察，例如 Python/平台、磁盘、HTTP/TCP 可达性和必要文件检查。它不会替用户重启服务，也不会擅自修改配置。

证据包默认不采集主机名，并会从 URL 标签中去掉账号密码、Query 和 Fragment。对外分享前仍应人工检查，因为用户自己提供的文件路径、主机名或端口可能带有部署信息。

## 4. 让 Agent 也按同样的方法排障

仓库已经包含一个可移植的 Agent Skill：

```text
.agents/skills/edge-ai-deployment-doctor/
```

它要求 Agent：

1. 先写清楚“预期发生什么、实际发生什么”；
2. 先做最小、非侵入式检查；
3. 按 source → event → rule → alarm → operator feedback 逐段验证；
4. 找到第一个无法被证据支持的环节就停下来；
5. 输出证据与下一步验证，而不是把猜测写成根因。

需要提交或分享 Skill 时，可以一条命令打包：

```bash
python scripts/package_skill.py \
  .agents/skills/edge-ai-deployment-doctor
```

生成：

```text
dist/edge-ai-deployment-doctor.zip
```

打包结果是确定性的，并且拒绝把符号链接意外带进 Skill 压缩包。

## 5. 这个演示证明什么，不证明什么

**它能够证明：**

- 事件归一化是真实代码，不是 PPT；
- 规则持续时间、触发、恢复可以确定性复现；
- 报警有明确生命周期；
- 诊断工具可以生成结构化证据；
- Agent 能复用同一套“证据优先”排障方法；
- 这些行为都有自动测试。

**它不声称：**

- EdgeSafe Vision 是经过认证的生命安全系统；
- 合成数据等于真实客户现场验收；
- HTTP/TCP 可达就等于业务链路完整可用；
- 一个 Demo 可以替代真实设备、网络、权限和法规验证。

## 6. 一分钟讲清楚这个项目

如果路演时间很短，可以这样理解：

> 很多视觉 AI 项目做到“模型识别出了人”就结束了，但真实交付真正容易失败的是后半程：画面旧了、事件对不上、规则持续时间不对、重启后配置丢了、报警根本没到操作人员、出问题又拿不出证据。EdgeSafe Vision 把这些模型之外的最后一公里问题，做成可以复用的规则、适配器、诊断工具、验收方法、自动测试和 Agent Skill。任何人不接生产环境，也能先把完整链路跑通并验证。

继续阅读：[Getting Started](GETTING_STARTED.md)、[Architecture](ARCHITECTURE.md)、[脱敏现场案例](CASE_STUDY.md)。
