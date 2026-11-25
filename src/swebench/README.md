# SWE-bench 接入

生成预测与评分分开执行：本项目 runner 调用 Penguin 修改仓库、导出补丁；官方 SWE-bench harness 在 Docker 中评分。`completed` 只代表 Agent 正常结束，不代表解决了题目。

## 安装与配置

在项目根目录使用现有 Python 环境：

```bash
pip install -r requirements.txt
pip install datasets swebench
```

通过环境变量或项目根目录 `.env` 配置 `API_KEY`、可选 `BASE_URL`。接口须兼容本项目使用的 Anthropic Messages API；模型由 runner 的 `--model` 显式指定。不要把密钥写入命令行或数据集。

全项目工作目录统一为 `CODE_AGENT_WORKSPACE_DIR`（进程启动时读取），默认是项目根目录下的 `workspace`。相对配置路径按进程启动目录解析。文件工具、搜索、命令、任务、团队、skill 工作目录和 PRDBench 使用同一根目录；更换目录需要启动新进程。

## 生成预测

```bash
python scripts/run_swebench.py \
  --dataset princeton-nlp/SWE-bench_Lite \
  --split test \
  --limit 5 \
  --model YOUR_MODEL_ID \
  --model-name penguin-baseline \
  --max-iterations 100 \
  --timeout 1800 \
  --output artifacts/swebench/lite-001
```

`--instance-ids ID1 ID2` 可固定题目；`--limit` 按数据集原顺序取前 N 题。每题单独 clone、checkout `base_commit` 并启动新 Python 进程，串行执行。只将 `instance_id`、`repo`、`base_commit`、`problem_statement` 写入 worker 输入，不传递参考补丁、测试补丁或评分字段。

可选参数：

- `--dataset-file /absolute/path/instances.jsonl`：本地 JSONL，至少包含上面四个字段，无需 datasets 包。
- `--repo-root /absolute/path/mirrors`：从本地 `mirrors/owner/repo` 克隆，适合离线与重复实验。
- `--setup-command '...'`：每题仓库内运行的可信依赖安装命令；`--setup-timeout 900` 限制克隆及安装各阶段时间;单题 agent 上限 `--timeout` 建议 7200。安装命令不要修改受版本控制的源码，否则这些修改也会进入补丁。
- `--resume`：配合完全相同的参数恢复已有运行。已完成记录（包括失败记录）跳过；中断的题目目录归档到 `interrupted/`，重新执行。重试已结束但失败的题目请用新的输出目录和 `--instance-ids`。
- `--parallel N`：同时运行 N 题（默认 1，串行）。各题使用独立目录与 worker 进程，`predictions.jsonl` 与 `summary.json` 仍按数据集原始顺序写出。并发受模型接口限流与本机资源约束，建议 2–4。

worker 暴露 `exit_loop` 工具并在 system prompt 中声明;模型完成修复后主动调用它作为正常出口。进程超时会终止进程组，包括命令工具启动的子进程，并尽可能保留已有补丁。非 completed 状态使 runner 返回非零退出码，但仍输出预测，继续运行其他题目。

## 运行环境边界

这是**本地进程 runner，不是容器沙箱**。模型命令继承宿主机权限、环境和网络；路径检查不是安全隔离。应在专用评测机器或外部隔离环境执行。标准答案和评分文件不要放在 Agent 可访问的环境中。

runner 不自动构建 SWE-bench 实例镜像，也不自动安装每个历史仓库所需的特定 Python/依赖版本。使用 `--setup-command` 或预先准备的执行环境提供依赖；不同题目需要不同环境时分批运行。未经环境准备的运行只能验证生成链路，不能视作环境一致的正式基线。官方评分阶段仍使用官方 Docker harness。

## 产物

```text
<output>/
  run.json                  参数及所选实例的公开字段
  predictions.jsonl         官方格式，包含所有已处理题目（失败可为空补丁）
  summary.json              每题状态、耗时、补丁大小、可用的 token 统计
  <instance_id>/
    repo/                   独立 checkout，保留现场
    input.json              仅公开输入字段
    clone.log / setup.log   仓库准备输出（setup.log 按需生成）
    worker.log              Agent 进程标准输出及错误
    events.jsonl            模型文本、工具调用及结果（长结果截断）
    messages.json           正常返回后的会话
    worker_result.json      正常返回或捕获异常后的 Agent 状态与 usage
    result.json             父进程写入的最终状态，超时同样有记录
    patch.diff              相对 base_commit 的补丁
    prediction.json         单题预测
```

补丁收集使用临时 Git index，不修改真实暂存区；包括已提交、已暂存、未暂存、新增和删除文件。新增文件遵循 `.gitignore`，另排除 Agent 内部目录、缓存、虚拟环境、`.pyc` 和 `.log`。其他未忽略的临时文件仍可能进入补丁，需检查 `patch.diff`。不要用这些保留目录名存放修复源码。

Token 统计沿用现有 Agent loop 计数口径；超时强制终止时可能没有最终 usage，不作精确账单统计。工具日志和会话可能包含仓库内容及命令输出，分享前按实际内容检查。

## 官方评分

安装并启动 Docker 后，在项目根目录执行：

```bash
python -m swebench.harness.run_evaluation \
  --dataset_name princeton-nlp/SWE-bench_Lite \
  --predictions_path artifacts/swebench/lite-001/predictions.jsonl \
  --max_workers 2 \
  --run_id penguin-lite-001
```

小样本评分可追加与生成阶段一致的 `--instance_ids ID1 ID2`。使用官方报告的 resolved 判定，按预先选定的题目总数计算解决率，另外记录空补丁、超时和基础设施失败。修改补丁重新评分时更换 `run_id`，避免缓存旧结果。

## Docker 生成模式（`--docker`）

默认生成模式在宿主机本地环境运行 worker，测试验证受限于本机依赖。`--docker` 让 worker 直接运行在该题的官方 `sweb.eval` 镜像内：

```bash
python scripts/run_swebench.py \
  --dataset princeton-nlp/SWE-bench_Lite --split test \
  --model <MODEL_ID> --model-name penguin-<MODEL_ID> \
  --max-iterations 100 --timeout 7200 \
  --docker \
  --output artifacts/swebench/<run-name>
```

- worker 进程用镜像内 base conda Python（3.11）运行；agent 的 `run_command` 默认落在 `testbed` conda 环境（dev 镜像把 `testbed/bin` 前置到 `PATH`），跑测试用的就是与评分一致的解释器和依赖。
- 镜像准备三层复用：已有 `sweb.eval.x86_64.<iid>` 直接使用；缺失时优先用本地历史 checkout 打 `git bundle` 离线构建（容器内不访问 GitHub）；env 镜像缺失时调用官方 harness 构建（仅 conda 网络）。`sweb.dev.x86_64.<iid>` 在实例镜像上追加 agent 依赖（pip 清华源）。
- patch 在容器内导出（`/out/export_patch.sh`，与宿主机 `export_patch` 逻辑一致），超时时容器仍存活，先 `docker exec` 导出再清理；容器以宿主机 uid 运行，产物属主与本地模式一致。
- 宿主机需安装 Docker 且磁盘预留充足（每题镜像 3GB+，env 镜像按仓库版本共享）。`--setup-command` 在该模式下不可用（env 镜像已带依赖）。

参考：[官方评测指南](https://www.swebench.com/SWE-bench/guides/evaluation/)。

## 离线验证

```bash
python -m pytest test/test_swebench.py -q
```

测试使用临时 Git 仓库和模拟 worker，不调用模型：验证补丁可应用、新增/删除/已提交变更、真实 index 不被污染、公开字段过滤、超时保留补丁、恢复运行及工具工作目录一致性。

## 测评报告

verified-030 首轮完整测评(2026-11-24,glm-5.3-flash,19/30 resolved)的结果、行为分析与经验教训见 [docs/verified-030-eval-report.md](../docs/verified-030-eval-report.md)。
