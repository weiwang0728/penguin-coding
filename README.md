# penguin-coding

## Langfuse 可观测性

支持可选的 Agent/模型/工具链路追踪、Token 用量、PRDBench 与 SWE-bench 评分关联。默认关闭。
安装 `requirements-observability.txt` 后按 [Langfuse 接入说明](docs/langfuse-integration.md) 配置；
可用 `python scripts/check_langfuse.py` 验证连接（不调用模型）。

## SWE-bench

支持独立 workspace、逐题 Agent 运行、补丁导出、JSONL 预测和运行日志。
使用方式与环境要求见 [SWE-bench 接入说明](src/swebench/README.md)。
