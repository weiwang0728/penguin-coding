---
name: swebench-eval
description: SWE-bench 测评全流程 runbook(当前验证集合 swebench-verify-30)——Featurize 归还前保存、重新租用恢复、生成预测(默认 Docker 模式,宿主机模式仅降级用)、监控、重试与官方评分。当用户要求继续/启动/排查 swebench 测评,或更换模型重跑时使用。
---

# SWE-bench 测评 Runbook(验证集合:verified-030)

生成与评分分离:`scripts/run_swebench.py` 调 agent 产 patch;官方 harness 在 Docker 里评分。完整文档见 `src/swebench/README.md`。

**当前验证集合 `verified-030`**:从 SWE-bench_Verified(500 题)分层抽样 30 题——各 repo 平方根配额(每 repo ≥1,合计 30)× 4 档 Verified 难度轮转,seed=20261123。抽样清单与公开字段:
- `artifacts/swebench/verified-030.public.jsonl`(30 行,instance_id/repo/base_commit/problem_statement)
- `artifacts/swebench/verified-030.manifest.json`(抽样方法与分布)、`verified-030.SHA256SUMS`
- 评分用完整数据:`$HOME/work/swebench-grading/verified-dl/verified-test.parquet`(含 test_patch/gold,不进 git)
- 覆盖 12 个 repo(astropy 2、django 7、matplotlib 3、seaborn 1、flask 1、requests 1、xarray 2、pylint 1、pytest 2、sklearn 3、sphinx 3、sympy 4);本地 `repos/` 只覆盖 astropy+django,其余 repo 由 runner 从 GitHub 克隆(需网络)

## 1. Featurize 重新租用

归还按量实例后，持久化目录是 `/home/featurize/work`。项目、未提交代码、项目根目录的 `.env`、历史 checkout、各轮预测、评分报告和 `logs/` 都已在云盘。新实例使用同一账号的云盘，选择可运行 Docker 的 Linux x86_64 环境。当前快照来自 Ubuntu 22.04、conda Python 3.11.8、Docker 26.1.0。[Featurize 实例归还说明](https://docs.featurize.cn/docs/manual/instance-rent)

在同一终端运行以下命令。项目的恢复目录含镜像归档、Python 包、版本清单及只有公开字段的 Lite test JSONL。相邻的评分目录保存 Lite 完整 JSON 数组和 Arrow 缓存,以及 Verified 完整 parquet(`verified-dl/`)。

```bash
cd ~/work/penguin-coding
R="$PWD/artifacts/swebench/featurize-restore"
G="$HOME/work/swebench-grading"
DATA="$G/SWE-bench_Lite-test-6ec7bb89b9342f664a54a6e0a6ea6501d3437cc2.json"
(cd "$R" && sha256sum -c SHA256SUMS)
(cd "$G" && sha256sum -c SHA256SUMS)
(cd "$PWD/artifacts/swebench" && sha256sum -c verified-030.SHA256SUMS)
sha256sum "$G/verified-dl/verified-test.parquet"
# 期望值:a45b1fe4e2f0c8390b2b2938ac83e92ed5979000856808f3679c07812e9e6dcd
```

两组校验均通过后，恢复宿主机 Python 环境。以下包包含 CPython 3.11 的原生扩展，使用与快照匹配的基础镜像。每台新实例做一次，后续终端直接激活该环境。

```bash
/environment/miniconda3/bin/python -c 'import sys; assert sys.version_info[:2] == (3, 11)'
/environment/miniconda3/bin/python -m venv "$HOME/.venvs/swebench"
source "$HOME/.venvs/swebench/bin/activate"
tar -xzf "$R/python311-packages.tar.gz" -C "$(python -c 'import sysconfig; print(sysconfig.get_path("purelib"))')"
python -m pytest -q test/test_swebench.py
```

重新评分或使用 `--docker` 生成时，在 Docker 服务就绪后恢复镜像。确认 `docker info` 可访问 daemon，且 Docker 数据盘有足够空间解压镜像。两个归档:旧 `images.tar.gz`(Lite 基线 era,标签见 `images.txt`)与 **`images-env-verified030-v2.tar.gz`(verified-030 全套 base+env 镜像 + 4 个已修复的 eval 镜像 astropy-8872/sphinx-7985/8459/11510,标签与 ID 见 `images-verified030-v2.txt`,校验和见 `images-env-verified030-v2.sha256`)**。先载旧归档再载新归档:

```bash
docker info >/dev/null && docker load -i "$R/images.tar.gz" && docker load -i "$R/images-env-verified030-v2.tar.gz"
(while read -r tag digest; do
  [ "$(docker image inspect --format '{{.Id}}' "$tag")" = "$digest" ] || { echo "镜像校验失败 $tag" >&2; exit 1; }
done < "$R/images-verified030-v2.txt")
```

**载入后必须核对 tag 数量**:`tar -xzOf <archive> manifest.json`（或 `index.json`）的 RepoTags 须覆盖全部预期标签——11-26 发现旧归档(30.7GB,sha256 校验"通过")实际只含 `sweb.base` 一个镜像(保存当天即损坏,校验和为假阴性),sha256 不能证明归档完整。缺失时用 swebench 2.1.8 `build_env_images` 联网重建(16 个约 1.5 小时,网络抖动会致个别失败需重试)。

恢复后的 env 镜像(`sweb.env.x86_64.*`)可直接供 Docker 模式生成与官方评分复用。**例外**:重建 eval 镜像会遇到 era 依赖漂移(2026-11-26 详录见 `docs/verified-030-eval-report.md` §4.6 与 memory `swebench-era-drift-pins`)——astropy-8872 的 env 镜像已注入 `PIP_CONSTRAINT=/opt/constraints.txt`+`SETUPTOOLS_USE_DISTUTILS=stdlib`,sphinx eval 镜像已补 `docutils==0.16`+`roman==3.3` 与 tox `-rA`;其余 2019–2021 era repo 重建时按 §4.6 清单钉版。sphinx-7985 的 F2P 需访问 google.com,本网络不可达,属硬限制。

**只重评现有补丁**可直接使用之前的 predictions 和本地完整评分数据。下面重评已有镜像的五题，生成新报告，整个过程无需模型密钥。

```bash
python -m swebench.harness.run_evaluation \
  --dataset_name "$DATA" \
  --predictions_path artifacts/swebench/lite-020-unresolved-docker/predictions.jsonl \
  --cache_level instance --max_workers 2 --run_id "regrade-$(date -u +%Y%m%dT%H%M%SZ)"
```

**重新生成预测**需要项目根目录 `.env` 中有效的 `API_KEY`、兼容 Anthropic Messages 的 `BASE_URL` 及可用的模型接口。默认跑 **verified-030** 全部 30 题。**默认使用 Docker 模式生成**（`--docker --dataset <完整数据集>`）：agent 在每题正确的 testbed 容器里工作，能看到真实测试结果；宿主机共享 Python 3.11 跑不了老 repo 的测试（缺 pkg_resources、astropy_helpers 子模块、老依赖），会产生盲改 patch。verified-030 的大多数 repo 没有现成镜像，Docker 模式需联网构建 env 镜像；`repos/` 本地 checkout 只覆盖 astropy+django，其余 repo 需网络从 GitHub 克隆（不带 `--repo-root` 即可）。

```bash
python scripts/run_swebench.py \
  --dataset-file artifacts/swebench/verified-030.public.jsonl \
  --dataset "$G/SWE-bench_Verified-verified030.json" \
  --model glm-5.3-flash --model-name penguin-glm-5.3-flash \
  --max-iterations 100 --timeout 7200 --parallel 3 \
  --output "artifacts/swebench/verified-030-$(date -u +%Y%m%dT%H%M%SZ)" \
  --docker
```

Lite 基线前 20 题仍可用本地 checkout 重跑（离线,timeout 建议 7200）：

```bash
python scripts/run_swebench.py \
  --dataset-file "$R/lite-test.public.jsonl" --repo-root "$R/repos" --limit 20 \
  --model glm-5.3-flash --model-name penguin-glm-5.3-flash \
  --max-iterations 100 --timeout 7200 --parallel 1 \
  --output "artifacts/swebench/lite-020-rerun-$(date -u +%Y%m%dT%H%M%SZ)"
```

Docker 模式说明：runner 用 `--dataset-file` 读取公开输入，用 `--dataset` 构造完整 test spec。**env 镜像跨 run 复用**（`sweb.env.x86_64.<hash>` 按 environment.yml 哈希命名）——先 `docker image ls | grep sweb.env` 查已有哪些，已构建的题秒级就绪；未构建的需联网构建，重环境（matplotlib/sklearn）单镜像可达 1–2.5 小时。容器内 `git clone github.com` 大仓库会间歇性 TLS 中断（GnuTLS -110），失败重试通常可过；宿主机 `repos/` 本地 checkout 不能注入容器，Docker 模式一律走 GitHub 克隆。

**宿主机模式（不带 `--docker`）已不推荐**，仅作降级手段：agent 用宿主机共享 Python 3.11 跑测试，老 repo 无法执行测试 → 盲改 patch（2026-11-24 verified-030 首轮 60% 解决率中 sphinx 0/3、pylint 0/1 部分归因于此）。宿主机模式的 permission 沙箱（工作区边界、rm 类 CONFIRM→deny、`$()` 拦截）是宿主机唯一防线，不要放开。

**续跑已有输出目录**时，按原 `run.json` 恢复参数，再加 `--resume`。原来使用 HF 数据集名的 run，可将保存的缓存复制到实例本地可写目录，保持原参数并离线加载。

```bash
export HF_HOME="$(mktemp -d)"
cp -a "$G/hf-cache/datasets" "$HF_HOME/"
export HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1
```

**下次归还前**，确认新 run 的 `run.json`、`predictions.jsonl`、`summary.json` 和评分报告都在 `~/work`。verified-030 的三个文件（public.jsonl / manifest.json / SHA256SUMS）与 `$G/verified-dl/verified-test.parquet` 是评分的必备数据，缺失则重新下载并更新 `verified-030.SHA256SUMS` 与 parquet 哈希。若更换了数据集 revision 或 Python 依赖，保存对应数据和环境。若构建了新镜像，用 `docker image ls` 核对 base/env/eval/dev 标签，将所需标签一起 `docker save` 到新归档，记录镜像 ID 和 SHA-256；**归档校验必须核对 manifest RepoTags 数量（`tar -xzOf <archive> index.json`），只信 sha256 会漏检截断档（11-26 事故）**。完成校验后再归还。**Langfuse trace 数据在 Docker named volume 里,不随 `~/work` 持久化——归还前必须备份 `langfuse_clickhouse_data`/`langfuse_postgres_data` 卷到 `~/work/langfuse/backup/`,否则 token 级分析数据全丢（11-26 实际发生）**。保留 `lite-020` 下被 `repos/` 引用的 checkout；verified-030 各 repo 的 checkout（`verified-030-glm-*/<instance>/repo`）如磁盘允许也一并保留，可省下次克隆。

### 手动安装

使用其他基础镜像需要重新安装依赖时，宿主机版本见 `$R/python-versions.txt`。本项目使用 SWE-bench 2.1.8；其 Modal API 与当前快照的 modal 0.73.13 配套。原 conda base 中的 torch 2.2.2 使用 numpy 1.26.4，保留 pyarrow 16.1.0 和 datasets 3.2.0。使用与该镜像兼容的 Python 环境执行：

```bash
python -m pip install -c "$R/python-versions.txt" -r requirements.txt \
  "$R/swebench-2.1.8-py3-none-any.whl" 'httpx[socks]' pytest
```

## 2. 启动/续跑测评

**启动前先跑预检**（数据完整性、归档 RepoTags 核验、era 钉版、网络、孤儿进程;约 5–8 分钟,`--quick` 跳过深检但正式跑之前务必跑完整的）：

```bash
bash scripts/preflight_benchmark.sh        # FAIL 必须先解决;WARN 逐条确认(如 7985 依赖 google.com 不可达属已知硬限制)
```

默认 Docker 模式（agent 在 testbed 容器内工作，测试结果真实）：

```bash
python scripts/run_swebench.py \
  --dataset-file artifacts/swebench/verified-030.public.jsonl \
  --dataset "$HOME/work/swebench-grading/SWE-bench_Verified-verified030.json" \
  --model <MODEL_ID> --model-name penguin-<MODEL_ID> \
  --max-iterations 100 --timeout 7200 \
  --parallel 3 \
  --output artifacts/swebench/<run-name> \
  --docker
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
- `error` 且 0 patch、报 "Instance image build failed ... Neither 'setup.py' nor 'pyproject.toml' found":是 **pyproject-only repo**(sphinx≥7.2 等,无 setup.py、flit_core 后端)撞上 legacy 安装路径——2026-11-25 已在 `scripts/run_swebench.py` 按 setup.py 存在性分流修复;若复现说明用了旧代码,拉新代码后换新输出目录重跑
- worker_error 且 0 patch:先查 `worker.log` 是否缺依赖(环境问题),修环境后该题必须重跑
- Docker 模式下容器内 git clone 间歇 TLS 失败(容器/worker 异常退出):直接原参数重试该题,通常第二次即过;连续失败再查网络
- timeout 带非空 patch:补丁可能有效,直接送评分判定,不必盲目重跑

## 5. 官方评分(Docker)

verified-030 评分用本地保存的完整数据（离线，不依赖 HF）。`run_evaluation` 的 `--dataset_name` 接受本地文件；Verified 完整数据是 parquet，先转成 JSON 数组（与 Lite 的 `SWE-bench_Lite-test-*.json` 同格式）再传：

```bash
python - <<'PY'
import json, os, pandas as pd
g = os.path.expanduser("~/work/swebench-grading")
ids = [json.loads(l)["instance_id"] for l in open("artifacts/swebench/verified-030.public.jsonl")]
df = pd.read_parquet(os.path.join(g, "verified-dl/verified-test.parquet"))
sel = df[df["instance_id"].isin(ids)]
with open(os.path.join(g, "SWE-bench_Verified-verified030.json"), "w") as f:
    json.dump(json.loads(sel.to_json(orient="records")), f)
print(len(sel), "instances written")
PY
python -m swebench.harness.run_evaluation \
  --dataset_name "$HOME/work/swebench-grading/SWE-bench_Verified-verified030.json" \
  --predictions_path artifacts/swebench/<run>/predictions.jsonl \
  --max_workers 2 --run_id "verified030-<run-id>"
```

Lite 评分仍用原命令（`--dataset_name princeton-nlp/SWE-bench_Lite` 或本地 Lite JSON）。小样本加 `--instance_ids ID1 ID2`;重评分换 run_id 避免缓存;resolved 以官方判定为准,verified-030 按固定 30 题算解决率。

## 6. 现有产物

**verified-030(当前验证集合,glm-5.3-flash,官方评分已完成)**
- **最终结果:20/30 resolved(66.7%),error 0**——首轮 19/30(63.3%);11-25 对 11 个 unresolved 题做 Docker 模式重生成并评分,pylint-4970 翻盘(详见 `docs/verified-030-eval-report.md` §4.5)
- 首轮合并 predictions 见 `verified-030-glm-merged-predictions.jsonl`,评分报告 `logs/run_evaluation/verified030-glm-*` 与 `reports/penguin-glm-5.3-flash.verified030-*.json`(harness 聚合报告统一归档在 `reports/`)
- `verified-030-glm-20261123T083900Z`:30 题首轮生成(宿主机模式,parallel 3,timeout 7200;因 API 5h 限额中断过)
- `verified-030-glm-retry2-20261124T065932Z`:5 个 api_error 题重跑(全部 completed)
- **docker11 重生成(2026-11-25)**:
  - `verified-030-unresolved11.public.jsonl`:11 个 unresolved 题清单
  - `verified-030-glm-docker11-20261125T081103Z`:Docker 模式重生成 10 题 completed + 1 error(sphinx-11510 构建失败,已修复后重跑)
  - `verified-030-glm-docker11-sph11510-20261125T101202Z`:sphinx-11510 修复后单题重跑(completed)
  - `verified-030-glm-docker11-merged-predictions.jsonl`:11 题合并 predictions(全部非空 patch)
  - 评分:`logs/run_evaluation/docker11-20261125T112035Z` + `reports/penguin-glm-5.3-flash.verified030-docker11-20261125T112035Z.json`;结果 **1/11 resolved**,20/30 总分
  - 教训:django-11885 F2P 过但 P2P 回归 2;astropy-8872 是 pyparsing warning-as-error 环境问题(重评可豁免);sphinx 3 题测试基建仍跑不通
- `verified-030.public.jsonl` / `manifest.json` / `SHA256SUMS`:抽样清单与公开字段
- **env 镜像已存档(v2,2026-11-26)**:featurize-restore 目录下 `images-env-verified030-v2.tar.gz`(base+20 env[sklearn `3a59860bcd...` 缺待补]+4 个修复版 eval 镜像)+ `images-verified030-v2.txt` + `.sha256`。**旧 `images-env-verified030.tar.gz` 已损坏**(只含 base,勿再用);16 个 env 镜像系重建,4 个旧 env 镜像已补 git HTTP/1.1;astropy-8872 env 含 PIP_CONSTRAINT 钉版;sphinx eval 镜像含 roman/docutils/-rA 修复。 era 漂移处置详见 `docs/verified-030-eval-report.md` §4.6
- Lite 各题产物(历史基线):
  - `lite-020`:前 20 题基线(12 completed)
  - `lite-020-retry3`:11583 completed
  - `lite-020-retry7`:7 题重试(3600s + parallel 3)
  - `lite-021-040-20261123T061514Z`:21–40 题扩展
- 各 run 的 `run.json` 是重建题目清单的数据源
