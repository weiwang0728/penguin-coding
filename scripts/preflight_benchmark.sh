#!/bin/bash
# Benchmark 预检:在启动评测/生成前验证环境与数据的有效性。
# 背景:2026-11-26 事故——镜像归档 sha256"通过"但实际只含 1 个镜像(假阴性),
# 只信校验和会带着残缺环境跑完整个 benchmark。脚本会"失败出声"。
#
# 用法: bash scripts/preflight_benchmark.sh [--quick]
#   --quick   跳过深检(归档全档扫描、pytest),只跑快检
# 退出码: 0=全部通过(允许 WARN), 1=存在 FAIL
set -u

PASS=0; WARN=0; FAIL=0
declare -a FAILS WARNS

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
R="$repo_root/artifacts/swebench/featurize-restore"
G="$HOME/work/swebench-grading"
QUICK=""
[ "${1:-}" = "--quick" ] && QUICK=1

# 预期值来源: swebench-eval skill / docs/verified-030-eval-report.md
EXPECTED_PARQUET_SHA="a45b1fe4e2f0c8390b2b2938ac83e92ed5979000856808f3679c07812e9e6dcd"
ARCHIVE="$R/images-env-verified030-v2.tar.gz"
ARCHIVE_MANIFEST="$R/images-verified030-v2.txt"
MIN_FREE_GB="${MIN_FREE_GB:-60}"
# 需要访问外网测试目标的实例(本网络到 google.com 不可达时必然误判为 unresolved)
declare -A NET_DEPENDENT_TESTS=( ["sphinx-doc__sphinx-7985"]="https://www.google.com" )

say()  { printf '%s\n' "$*"; }
pass() { printf '  [PASS] %s\n' "$*"; PASS=$((PASS+1)); }
warn() { printf '  [WARN] %s\n' "$*"; WARN=$((WARN+1)); WARNS+=("$*"); }
fail() { printf '  [FAIL] %s\n' "$*"; FAIL=$((FAIL+1)); FAILS+=("$*"); }

say "== Benchmark 预检 $(date '+%F %T') (repo: $repo_root)${QUICK:+ [quick mode]} =="

# ---------- 1. 持久化数据校验和 ----------
say "-- 1. 持久化数据完整性"
if [ -f "$R/SHA256SUMS" ]; then
  if out=$(cd "$R" && sha256sum -c SHA256SUMS 2>&1 | grep -v ': OK$'); then
    fail "featurize-restore 校验失败: $(echo "$out" | head -2)"
  else
    pass "featurize-restore/SHA256SUMS 全部通过"
  fi
else
  warn "缺少 $R/SHA256SUMS,跳过"
fi
if [ -f "$G/SHA256SUMS" ]; then
  if out=$(cd "$G" && sha256sum -c SHA256SUMS 2>&1 | grep -v ': OK$'); then
    fail "swebench-grading 校验失败: $(echo "$out" | head -2)"
  else
    pass "grading 目录 SHA256SUMS 全部通过"
  fi
else
  warn "缺少 $G/SHA256SUMS,跳过"
fi
if [ -f artifacts/swebench/verified-030.SHA256SUMS ]; then
  if out=$(sha256sum -c artifacts/swebench/verified-030.SHA256SUMS 2>&1 | grep -v ': OK$'); then
    fail "verified-030 数据校验失败: $(echo "$out" | head -2)"
  else
    pass "verified-030 抽样清单校验通过"
  fi
else
  warn "缺少 verified-030.SHA256SUMS,跳过"
fi
PARQUET="$G/verified-dl/verified-test.parquet"
if [ -f "$PARQUET" ]; then
  actual=$(sha256sum "$PARQUET" | cut -d' ' -f1)
  if [ "$actual" = "$EXPECTED_PARQUET_SHA" ]; then
    pass "verified parquet 哈希匹配"
  else
    fail "verified parquet 哈希不匹配(实际 $actual)"
  fi
else
  fail "缺少评分用完整数据 $PARQUET"
fi

# ---------- 2. 镜像归档有效性(核心教训: sha256 不证明归档完整) ----------
say "-- 2. 镜像归档 RepoTags 核验(防截断/假阴性)"
if [ -f "$ARCHIVE" ]; then
  recorded=$(cut -d' ' -f1 "$R/images-env-verified030-v2.sha256" 2>/dev/null)
  expected_tags=0
  [ -f "$ARCHIVE_MANIFEST" ] && expected_tags=$(wc -l < "$ARCHIVE_MANIFEST")
  if [ "$QUICK" = 1 ]; then
    warn "quick 模式跳过全档扫描(约 5 分钟);启动正式跑之前务必跑一次完整预检"
  else
    tags_json=$(tar -xzOf "$ARCHIVE" manifest.json 2>/dev/null | python3 -c "
import json,sys
try:
    d = json.load(sys.stdin)
except Exception as e:
    print('PARSE_ERROR'); raise SystemExit
n = 0; tags = []
for m in d:
    ts = m.get('RepoTags') or []
    n += len(ts); tags += ts
print(n, len(set(tags)), ' '.join(sorted(set(tags))))
" 2>/dev/null)
    if [ -z "$tags_json" ] || [ "${tags_json%% *}" = "PARSE_ERROR" ]; then
      fail "归档无法解析 manifest.json(截断或损坏): $ARCHIVE"
    else
      n_total=$(echo "$tags_json" | awk '{print $1}')
      n_uniq=$(echo "$tags_json" | awk '{print $2}')
      if [ "$n_uniq" -ge "$expected_tags" ] && [ "$expected_tags" -gt 0 ]; then
        pass "归档含 $n_uniq 个唯一 tag(≥ manifest 的 $expected_tags)"
      else
        fail "归档 tag 不足: 实际唯一 tag=$n_uniq, manifest 预期=$expected_tags —— 勿使用此归档"
      fi
      # 关键 tag 抽查
      for t in sweb.base.x86_64:latest sweb.env.x86_64.764c21123474adcba1e003:latest sweb.eval.x86_64.astropy__astropy-8872:latest; do
        echo "$tags_json" | grep -qw "$t" || warn "归档缺少关键 tag: $t"
      done
    fi
  fi
  if [ -n "$recorded" ]; then
    actual=$(sha256sum "$ARCHIVE" | cut -d' ' -f1)
    [ "$actual" = "$recorded" ] && pass "归档 sha256 与记录一致" || fail "归档 sha256 与记录不一致"
  else
    warn "无 $R/images-env-verified030-v2.sha256,跳过哈希比对"
  fi
else
  fail "镜像归档不存在: $ARCHIVE(需重建或从云盘恢复)"
fi

# ---------- 3. 已载入镜像 ----------
say "-- 3. Docker 已载入镜像"
if docker info >/dev/null 2>&1; then
  pass "docker daemon 可访问"
  if [ -f "$ARCHIVE_MANIFEST" ]; then
    missing=0; mismatch=0
    while read -r tag digest; do
      actual=$(docker image inspect --format '{{.Id}}' "$tag" 2>/dev/null)
      if [ -z "$actual" ]; then
        missing=$((missing+1))
      elif [ -n "$digest" ] && [ "$actual" != "$digest" ]; then
        mismatch=$((mismatch+1))
      fi
    done < "$ARCHIVE_MANIFEST"
    [ "$missing" = 0 ] && pass "manifest 全部 tag 已载入" || warn "有 $missing 个 tag 未载入(如需重新生成/评分会触发联网构建)"
    [ "$mismatch" = 0 ] && pass "已载入镜像 ID 与 manifest 一致" || warn "有 $mismatch 个镜像 ID 与 manifest 不一致(重建过,属预期时确认已重新记录)"
  fi
  free_gb=$(df --output=avail -BG "$(docker info --format '{{.DockerRootDir}}' 2>/dev/null)" 2>/dev/null | tail -1 | tr -dc '0-9')
  if [ -n "${free_gb:-}" ] && [ "$free_gb" -ge "$MIN_FREE_GB" ]; then
    pass "docker 数据盘剩余 ${free_gb}GB(≥${MIN_FREE_GB})"
  else
    fail "docker 数据盘剩余 ${free_gb:-?}GB < ${MIN_FREE_GB}GB,载入镜像可能中途 quota 超限"
  fi
else
  fail "docker daemon 不可访问"
fi

# ---------- 4. Python 环境 ----------
say "-- 4. Python 环境"
VENV_PY="$HOME/.venvs/swebench/bin/python"
if [ -x "$VENV_PY" ]; then
  pass "venv 存在"
  if "$VENV_PY" -c "import swebench, docker, pandas, datasets" 2>/dev/null; then
    pass "swebench/docker/pandas/datasets 可导入"
  else
    fail "关键包导入失败(venv 可能未恢复 python311-packages.tar.gz)"
  fi
  if [ "$QUICK" = 1 ]; then
    warn "quick 模式跳过 pytest"
  elif "$VENV_PY" -m pytest -q test/test_swebench.py >/dev/null 2>&1; then
    pass "test/test_swebench.py 通过"
  else
    fail "test/test_swebench.py 失败"
  fi
else
  fail "venv 不存在: $VENV_PY(按 runbook §1 重建)"
fi

# ---------- 5. 数据集文件 ----------
say "-- 5. 数据集文件"
PUB=artifacts/swebench/verified-030.public.jsonl
FULL="$G/SWE-bench_Verified-verified030.json"
if [ -f "$PUB" ] && [ -f "$FULL" ]; then
  out=$("$VENV_PY" - <<PY 2>&1
import json
pub = [json.loads(l)["instance_id"] for l in open("$PUB")]
full = {i["instance_id"] for i in json.load(open("$FULL"))}
missing = set(pub) - full
print(len(pub), len(missing))
PY
)
  n_pub=$(echo "$out" | awk '{print $1}'); n_missing=$(echo "$out" | awk '{print $2}')
  if [ "$n_pub" = "30" ] && [ "$n_missing" = "0" ]; then
    pass "public.jsonl 30 题且完整数据集全覆盖"
  else
    fail "数据集异常: public=$n_pub 题, 完整数据缺失 $n_missing 题"
  fi
else
  fail "缺少 $PUB 或 $FULL"
fi

# ---------- 6. 网络(含外网依赖测试目标) ----------
say "-- 6. 网络可达性"
if curl -sI --max-time 10 https://pypi.org/simple/ >/dev/null 2>&1; then
  pass "PyPI 可达(env 镜像重建/era 钉版需要)"
else
  warn "PyPI 不可达——重建镜像类操作会失败"
fi
if curl -sI --max-time 10 https://github.com >/dev/null 2>&1; then
  pass "github.com 可达(容器内 clone 仍可能间歇 TLS 失败,重试即可)"
else
  warn "github.com 不可达——生成/评分的镜像构建将失败,建议宿主机 git 镜像方案"
fi
for iid in "${!NET_DEPENDENT_TESTS[@]}"; do
  url="${NET_DEPENDENT_TESTS[$iid]}"
  if curl -sI --max-time 10 "$url" >/dev/null 2>&1; then
    pass "$iid 的外网测试目标可达: $url"
  else
    warn "$iid 的测试依赖 $url,本网络不可达——该题会必然误判 unresolved,重跑无意义"
  fi
done

# ---------- 7. era 钉版抽检 ----------
say "-- 7. era 钉版抽检(防依赖漂移回归)"
ASTROPY_ENV=sweb.env.x86_64.428468730904ff6b4232aa:latest
if docker image inspect "$ASTROPY_ENV" >/dev/null 2>&1; then
  cons=$(docker run --rm --entrypoint cat "$ASTROPY_ENV" /opt/constraints.txt 2>/dev/null)
  envs=$(docker image inspect --format '{{.Config.Env}}' "$ASTROPY_ENV")
  echo "$cons" | grep -q 'pyparsing==2.4.7' && pass "astropy env constraints 含 pyparsing 钉版" || warn "astropy env 缺 pyparsing==2.4.7 钉版(pyparsing warning-as-error 会复发)"
  echo "$envs" | grep -q 'SETUPTOOLS_USE_DISTUTILS=stdlib' && pass "astropy env 已设 stdlib distutils" || warn "astropy env 缺 SETUPTOOLS_USE_DISTUTILS=stdlib(distutils DeprecationWarning 会复发)"
else
  warn "astropy env 镜像未载入,跳过钉版抽检"
fi

# ---------- 8. 孤儿进程与 API 配置 ----------
say "-- 8. 运行前检查"
orphans=$(for p in /proc/[0-9]*/cmdline; do c=$(tr '\0' ' ' < "$p" 2>/dev/null); case "$c" in *run_swebench*|*swebench.worker*) echo "$p";; esac; done | wc -l)
[ "$orphans" = 0 ] && pass "无 run_swebench 孤儿进程" || fail "发现 $orphans 个 run_swebench 孤儿进程,先 kill 再启动(防双 runner 写同一目录)"
if [ -f .env ] && grep -q '^API_KEY=.\+' .env && grep -q '^BASE_URL=.\+' .env; then
  pass ".env 含 API_KEY/BASE_URL(重新生成需要)"
else
  warn ".env 缺 API_KEY/BASE_URL——只能重评已有 patch,不能重新生成"
fi

# ---------- 汇总 ----------
say "== 预检完成: PASS=$PASS WARN=$WARN FAIL=$FAIL =="
if [ "$FAIL" -gt 0 ]; then
  say "必须先解决:"
  for f in "${FAILS[@]}"; do say "  FAIL: $f"; done
  exit 1
fi
[ "$WARN" -gt 0 ] && { say "留意:"; for w in "${WARNS[@]}"; do say "  WARN: $w"; done; }
exit 0
