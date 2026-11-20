---
name: swebench-eval
description: SWE-bench Lite 测评全流程 runbook——Featurize 归还前保存、重新租用恢复、生成预测(串行/并行)、监控、重试与官方评分。当用户要求继续/启动/排查 swebench 测评,或更换模型重跑时使用。
---

# SWE-bench Lite 测评 Runbook

生成与评分分离:`scripts/run_swebench.py` 调 agent 产 patch;官方 harness 在 Docker 里评分。完整文档见 `src/swebench/README.md`。

## 1. Featurize 重新租用

归还按量实例后，持久化目录是 `/home/featurize/work`。项目、未提交代码、项目根目录的 `.env`、历史 checkout、各轮预测、评分报告和 `logs/` 都已在云盘。新实例使用同一账号的云盘，选择可运行 Docker 的 Linux x86_64 环境。当前快照来自 Ubuntu 22.04、conda Python 3.11.8、Docker 26.1.0。[Featurize 实例归还说明](https://docs.featurize.cn/docs/manual/instance-rent)

在同一终端运行以下命令。项目的恢复目录含镜像归档、Python 包、版本清单及只有公开字段的 Lite test JSONL。相邻的评分目录保存同一 revision 的完整 JSON 数组和 Arrow 缓存。

```bash
cd ~/work/penguin-coding
R="$PWD/artifacts/swebench/featurize-restore"
G="$HOME/work/swebench-grading"
DATA="$G/SWE-bench_Lite-test-6ec7bb89b9342f664a54a6e0a6ea6501d3437cc2.json"
(cd "$R" && sha256sum -c SHA256SUMS)
(cd "$G" && sha256sum -c SHA256SUMS)
```

两组校验均通过后，恢复宿主机 Python 环境。以下包包含 CPython 3.11 的原生扩展，使用与快照匹配的基础镜像。每台新实例做一次，后续终端直接激活该环境。

```bash
/environment/miniconda3/bin/python -c 'import sys; assert sys.version_info[:2] == (3, 11)'
/environment/miniconda3/bin/python -m venv "$HOME/.venvs/swebench"
source "$HOME/.venvs/swebench/bin/activate"
tar -xzf "$R/python311-packages.tar.gz" -C "$(python -c 'import sysconfig; print(sysconfig.get_path("purelib"))')"
python -m pytest -q test/test_swebench.py
```

重新评分或使用 `--docker` 生成时，在 Docker 服务就绪后恢复镜像。确认 `docker info` 可访问 daemon，且 Docker 数据盘有足够空间解压镜像。归档中的标签及镜像 ID 见 `images.txt`。

```bash
docker info >/dev/null && docker load -i "$R/images.tar.gz"
(while read -r tag digest; do
  [ "$(docker image inspect --format '{{.Id}}' "$tag")" = "$digest" ] || { echo "镜像校验失败 $tag" >&2; exit 1; }
done < "$R/images.txt")
```

**只重评现有补丁**可直接使用之前的 predictions 和本地完整评分数据。下面重评已有镜像的五题，生成新报告，整个过程无需模型密钥。

```bash
python -m swebench.harness.run_evaluation \
  --dataset_name "$DATA" \
  --predictions_path artifacts/swebench/lite-020-unresolved-docker/predictions.jsonl \
  --cache_level instance --max_workers 2 --run_id "regrade-$(date -u +%Y%m%dT%H%M%SZ)"
```

**重新生成预测**需要项目根目录 `.env` 中有效的 `API_KEY`、兼容 Anthropic Messages 的 `BASE_URL` 及可用的模型接口。下面按 Lite 原顺序重跑基线前 20 题。两个本地仓库入口指向云盘的历史 checkout，覆盖这 20 个 base commit。

```bash
python scripts/run_swebench.py \
  --dataset-file "$R/lite-test.public.jsonl" --repo-root "$R/repos" --limit 20 \
  --model glm-5.3-flash --model-name penguin-glm-5.3-flash \
  --max-iterations 100 --timeout 1800 --parallel 1 \
  --output "artifacts/swebench/lite-020-rerun-$(date -u +%Y%m%dT%H%M%SZ)"
```

使用 Docker 生成时，在上述生成命令中追加 `--docker --dataset "$DATA"`。runner 用 `--dataset-file` 读取公开输入，用 `--dataset` 构造完整 test spec。现有镜像覆盖 14 个 eval 实例、6 个 dev 实例，新增题目可能需要联网构建。跑其他仓库时，添加相应的本地仓库，或移除 `--repo-root` 允许从 GitHub 克隆。

**续跑已有输出目录**时，按原 `run.json` 恢复参数，再加 `--resume`。原来使用 HF 数据集名的 run，可将保存的缓存复制到实例本地可写目录，保持原参数并离线加载。

```bash
export HF_HOME="$(mktemp -d)"
cp -a "$G/hf-cache/datasets" "$HF_HOME/"
export HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1
```

**下次归还前**，确认新 run 的 `run.json`、`predictions.jsonl`、`summary.json` 和评分报告都在 `~/work`。若更换了数据集 revision 或 Python 依赖，保存对应数据和环境。若构建了新镜像，用 `docker image ls` 核对 base/env/eval/dev 标签，将所需标签一起 `docker save` 到新归档，记录镜像 ID 和 SHA-256；完成校验后再归还。保留 `lite-020` 下被 `repos/` 引用的 checkout。

### 手动安装

使用其他基础镜像需要重新安装依赖时，宿主机版本见 `$R/python-versions.txt`。本项目使用 SWE-bench 2.1.8；其 Modal API 与当前快照的 modal 0.73.13 配套。原 conda base 中的 torch 2.2.2 使用 numpy 1.26.4，保留 pyarrow 16.1.0 和 datasets 3.2.0。使用与该镜像兼容的 Python 环境执行：

```bash
python -m pip install -c "$R/python-versions.txt" -r requirements.txt \
  "$R/swebench-2.1.8-py3-none-any.whl" 'httpx[socks]' pytest
```

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
