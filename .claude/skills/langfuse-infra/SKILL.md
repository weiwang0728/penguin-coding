---
name: langfuse-infra
description: 本机自托管 Langfuse(v4,docker compose)部署、项目 .env 接线、连接验证与故障排查 runbook。当用户要求配置/重启/排查 Langfuse 观测,或重新租用实例后恢复观测栈时使用。
---

# Langfuse 自托管接入 Runbook

代码侧接入已内置于项目:`src/observability.py`(fail-open,默认关闭,OTel 版 SDK),完整说明见 `docs/langfuse-integration.md`。本 runbook 只管**服务端与配置**。服务栈与密钥都在持久化目录 `~/work/langfuse`(随云盘保存),项目 `.env` 的 Langfuse 段同样随云盘。

当前快照(2026-11-23 部署):Langfuse **v4.83.0**,6 服务栈,已完成端到端验证。

## 1. 重新租用实例后恢复

确认 `docker info` 可访问 daemon,然后:

```bash
cd ~/work/langfuse && docker compose up -d
```

注意:**不要**用 GitHub main 分支的 upstream compose——它已改用 `docker.langfuse.com` 私有 registry 并含不需要的 ai-gateway 服务。云盘里的 `docker-compose.yml` 是改写过的 docker.io 版本。

镜像不归档(恢复时重拉,见第 2 步)。Python 侧:venv 恢复后补装 SDK(不在 `python311-packages.tar.gz` 里):

```bash
source "$HOME/.venvs/swebench/bin/activate"
python -m pip install 'langfuse==5.2.0'
```

项目 `.env` 已含 Langfuse 段(追加在模型配置之后),无需改动;密钥与 `~/work/langfuse/.env` 的 `LANGFUSE_INIT_PROJECT_*` 一致。

## 2. 镜像拉取(无 root 的 mirror 方案)

Docker Hub 直连在本机不稳(EOF/unauthorized),而**无 root 权限改 `/etc/docker/daemon.json` 或重启 dockerd**。改用「mirror 拉取 + 打回原名」,daocloud 同时覆盖 docker.io 和 cgr.dev:

```bash
pull_tag() { docker pull "docker.m.daocloud.io/$1" && docker tag "docker.m.daocloud.io/$1" "$2"; }
pull_tag langfuse/langfuse-worker:4 docker.io/langfuse/langfuse-worker:4
pull_tag langfuse/langfuse:4       docker.io/langfuse/langfuse:4
pull_tag clickhouse/clickhouse-server:25.12 docker.io/clickhouse/clickhouse-server:25.12
pull_tag library/redis:7           docker.io/redis:7
pull_tag library/postgres:17       docker.io/postgres:17
pull_tag cgr.dev/chainguard/minio:latest cgr.dev/chainguard/minio:latest
```

首次部署后无需 `--pull always`;本地镜像已齐时 `docker compose up -d` 直接用。

## 3. 启动与 init 引导(三个关键坑)

6 服务:langfuse-web(0.0.0.0:3000)、langfuse-worker(127.0.0.1:3030)、clickhouse、postgres、redis、minio。首次就绪约 1–2 分钟(迁移 + ClickHouse 建表)。

首次启动时 web 容器读取 `.env` 的 `LANGFUSE_INIT_*` 自动建 org(`penguin-org`)、project(`penguin-coding`)、API keys 和管理员(`admin@penguin.local`)。**三个实测坑**:

1. **v4.83 要求显式 `LANGFUSE_INIT_ORG_ID`**——只给 `LANGFUSE_INIT_ORG_NAME` 时 init 整体跳过(web 日志有 warn),keys 不会创建。`.env` 已配 `LANGFUSE_INIT_ORG_ID=penguin-org`、`LANGFUSE_INIT_PROJECT_ID=penguin-coding`。
2. **`DATABASE_URL` 必须显式写入 `.env`**,且密码用生成的 `POSTGRES_PASSWORD`。compose 的默认值是 `postgres:postgres`,与随机密码不符 → web 报 Prisma `P1000` 循环重启。
3. **`docker compose restart` 不重读 env**。改完 `.env` 必须 `docker compose up -d` 重建容器;init 引导是幂等的,空库重建容器即生效。

## 4. 项目接线(.env)

项目根目录 `.env` 的 Langfuse 段:

```dotenv
PENGUIN_OBSERVABILITY_ENABLED=true
LANGFUSE_BASE_URL=http://localhost:3000
LANGFUSE_PUBLIC_KEY=pk-lf-local-...
LANGFUSE_SECRET_KEY=sk-lf-local-...
LANGFUSE_SAMPLE_RATE=1.0
LANGFUSE_TRACING_ENVIRONMENT=development
LANGFUSE_RELEASE=<git short sha>
PENGUIN_OBSERVABILITY_CONTENT=redacted
PENGUIN_OBSERVABILITY_MAX_CHARS=1000000
```

- `LANGFUSE_BASE_URL` 指向自托管地址,不是模型 API 地址;模型仍用 `API_KEY`/`BASE_URL`/`MODEL_ID`
- key 在 `~/work/langfuse/.env`(`LANGFUSE_INIT_PROJECT_PUBLIC_KEY` / `..._SECRET_KEY`),该文件 `chmod 600`
- 默认 `redacted` 全量记录输入输出(密钥仍脱敏,截断阈值 `PENGUIN_OBSERVABILITY_MAX_CHARS=1000000`);只要元数据改 `metadata_only`,改后**重启业务进程**(客户端按进程懒初始化)

## 5. 验证(2026-11-23 全部通过)

```bash
# 1) 连接检查:认证 + 合成 trace(不调模型)
python scripts/check_langfuse.py
# 通过输出:Authentication succeeded; synthetic trace flushed: <trace-id>

# 2) 离线单测(不依赖服务端)
API_KEY=test MODEL_ID=test-model PENGUIN_OBSERVABILITY_ENABLED=false \
  python -m pytest -q test/test_observability.py test/test_observability_core.py \
    test/test_observability_concurrency.py test/test_observability_entries.py
# 2026-11-23:45 passed

# 3) 端到端:跑真实任务(SWE-bench 单题冒烟见 swebench-eval skill),
#    trace 经 OTel 异步入库(数秒延迟)后在 http://localhost:3000 查询
```

**v4 是 events_only 模式**:legacy 查询 API(`GET /api/public/traces`、`GET /api/public/trace/<id>`)已移除,返回提示升级 SDK 的 JSON;`POST /api/public/scores` 仍可用(`scripts/import_langfuse_scores.py` 回填分数不受影响)。项目 SDK(langfuse 5.2.0)走 OTel 上报,正常。落库核验走 ClickHouse:

```bash
CHPASS=$(grep '^CLICKHOUSE_PASSWORD=' ~/work/langfuse/.env | cut -d= -f2)
curl -s "http://localhost:8123/?user=clickhouse&password=$CHPASS" \
  --data-binary "SELECT trace_id, span_id, parent_span_id, name, type, environment
                 FROM default.events_core WHERE trace_id='<trace-id>' FORMAT PrettyCompact"
```

首次验证的合成 trace:`0e15fc59fbc3f24dca9a2a38c4587a20`(root `penguin.connection_check` + 子 `tool.connection_check`,父子关系正确)。

## 6. 故障排查

| 现象 | 处理 |
| --- | --- |
| 拉镜像 EOF/unauthorized | 第 2 步 mirror 方案(daocloud,覆盖 docker.io + cgr.dev);无 root 别碰 daemon.json |
| web 报 Prisma `P1000` 重启 | `.env` 缺 `DATABASE_URL` 或密码不匹配,补齐后 `up -d` 重建 |
| init 没建 org/keys | 缺 `LANGFUSE_INIT_ORG_ID`;或数据卷已存在(init 幂等,改 ID 后 `up -d` 会补建缺失对象) |
| 改了 `.env` 不生效 | `restart` 不重读 env,用 `docker compose up -d` |
| `check_langfuse.py` 认证失败 | 核对两个 key 与 `LANGFUSE_BASE_URL`;改完重启业务进程 |
| 查 trace 返回"endpoint not available" | v4 events_only 正常现象,用 UI 或第 5 步 ClickHouse 查询 |
| 有 trace 无内容 | 检查 `PENGUIN_OBSERVABILITY_CONTENT` 是否为 `metadata_only`/未知值,改后重启业务进程 |
| 归还实例 | 栈目录与两个 `.env` 已在 `~/work`,无需导出;镜像不必归档;如需保留 trace 数据,备份卷 `langfuse_postgres_data`/`langfuse_clickhouse_data` |

Web UI:`http://localhost:3000`(端口对外暴露),管理员 `admin@penguin.local`,密码在 `~/work/langfuse/.env` 的 `LANGFUSE_INIT_USER_PASSWORD`。
