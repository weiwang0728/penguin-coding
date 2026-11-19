---
name: swebench-eval
description: SWE-bench Lite 测评全流程 runbook——环境初始化、生成预测(串行/并行)、监控、重试与官方评分。当用户要求继续/启动/排查 swebench 测评,或更换模型重跑时使用。
---

# SWE-bench Lite 测评 Runbook

生成与评分分离:`scripts/run_swebench.py` 调 agent 产 patch;官方 harness 在 Docker 里评分。完整文档见 `src/swebench/README.md`。

## 1. 环境初始化(每台新机器必做)

conda base(`python` = `/environment/miniconda3/bin/python`)安装:

```bash
pip install -r requirements.txt          # anthropic/python-dotenv/prompt_toolkit/rich/PyYAML
pip install "datasets==3.2.0" "pyarrow==16.1.0" "numpy==1.26.4" pytest
pip install "httpx[socks]"
```

版本陷阱:
- **不要升级 numpy ≥ 2**(会破坏 torch 2.2.2);新版 pyarrow 强制 numpy≥2,故固定 pyarrow 16.1.0 + datasets 3.2.0
- pypi 走清华镜像,Claude 沙箱内被域名过滤拦截 → pip 安装需在沙箱外执行
- `.env` 需含 `API_KEY`、`BASE_URL`(Anthropic Messages 兼容接口),不要写进命令行

## 2. 启动/续跑测评

```bash
python scripts/run_swebench.py \
  --dataset princeton-nlp/SWE-bench_Lite --split test \
  --model <MODEL_ID> --model-name penguin-<MODEL_ID> \
  --max-iterations 100 --timeout 3600 \
  --parallel 3 \
  --output artifacts/swebench/<run-name>
```

- **HF 直连会被限流**。数据集拿不到时:从已有 run 的 `run.json` 导出题目公开字段(instance_id/repo/base_commit/problem_statement)为 JSONL,改用 `--dataset-file` + `--instance-ids`
- `--parallel N`:并发跑 N 题(2–4 合适,过高易撞接口限流);`predictions.jsonl`/`summary.json` 仍按原顺序写出
- `--timeout` 单题 agent 墙钟上限(**建议 7200**:exit_loop 是正常出口,墙钟只是兜底;1800/3600 实测会截断难题收尾);timeout ≠ 空补丁,finally 里仍会导出已有 patch
- `--resume`:仅恢复"未完成"题(同参数同目录);**重试已结束但失败的题必须换新输出目录 + `--instance-ids`**

### 重启前检查孤儿进程

TaskStop / 会话结束可能只杀 shell 不杀 python 子进程:

```bash
for p in /proc/[0-9]*/cmdline; do c=$(tr '\0' ' ' < "$p" 2>/dev/null); case "$c" in *run_swebench*|*swebench.worker*) echo "$p";; esac; done
```

有残留先 `kill <runner_pid> <worker_pid...>`,确认清空后再启动,避免双 runner 写同一目录。

## 3. 进度监控

worker 已暴露 `exit_loop` 工具(复用 `src/prdbench/tools.py` 的 ExitLoopTool,system prompt 已声明),模型修完会主动调它收尾——这是正常出口,不是异常;墙钟超时只作兜底。

- 每题状态:`<output>/<instance_id>/result.json` 的 `status`(running/completed/timeout/worker_error…)
- 汇总:`<output>/summary.json`(每完成一题落盘一次)+ `predictions.jsonl`
- 运行中题看 `events.jsonl` 行数增长;`wc -l` 连续两轮 +0 再看 `worker.log`:
  - `Response truncated at max_tokens=16384, escalating to 65536` = 模型在生成 64K 级超长响应,等 10–25 分钟会自行恢复,**不要杀**
  - 长请求挂 9–13 分钟后自行恢复也是常态(glm-5.3-flash 常见),先观察再干预
- 单题事件爆发(+100/3min)通常在收尾;体量参考:完成题 events ≈ 980–1100

## 4. 失败重试策略

- 一轮跑完后统计 `summary.json` 非 completed 的题,导出到新 JSONL,换新输出目录重试
- worker_error 且 0 patch:先查 `worker.log` 是否缺依赖(环境问题),修环境后该题必须重跑
- timeout 带非空 patch:补丁可能有效,直接送评分判定,不必盲目重跑

## 5. 官方评分(Docker)

```bash
python -m swebench.harness.run_evaluation \
  --dataset_name princeton-nlp/SWE-bench_Lite \
  --predictions_path artifacts/swebench/<run>/predictions.jsonl \
  --max_workers 2 --run_id <run-id>
```

小样本加 `--instance_ids ID1 ID2`;重评分换 run_id 避免缓存;resolved 以官方判定为准,按预先选定题目总数算解决率。

## 6. 现有产物

- `artifacts/swebench/lite-020`:前 20 题基线(12 completed)
- `lite-020-retry3`:11583 completed
- `lite-020-retry7`:7 题重试(3600s + parallel 3)
- 各 run 的 `run.json` 是重建题目清单的数据源
