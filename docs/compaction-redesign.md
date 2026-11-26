# 压缩总设计方案(Context Compaction Redesign)

> 日期:2026-11-26
> 状态:设计定稿,待遥测裁决后实施
> 涉及代码:`src/compact.py`、`src/agent_loop.py`、`src/_constants.py`、`src/tools/*`

## 0. 设计前提与目标

**前提约束**:endpoint 侧前缀 cache 生效(仓库无显式 `cache_control`,走 implicit cache;`src/observability.py` 已在追踪 `ephemeral_*_input_tokens`)。任何对历史中段的改写都会从改写点击穿 cache,**因此设计目标是:最小化历史改写事件的次数,而不是分层越多越好**。

**量化依据**:

- cache 读 ~0.1x 底价;一次改写事件代价 ≈ `1.15 × 改写后上下文大小`(miss 重读 + 写入溢价),一次性;
- 清掉 D tokens 对剩余 M 次调用的节省 ≈ `0.1 × D × M`;
- 盈亏平衡:M ≈ 10-12 轮后续调用。触发太早或 run 快结束,压缩净亏。

**目标状态**:每 100 轮 run 全程 **2-3 次压缩事件**,每次代价已知、可入账;压缩事件之外历史完全冻结。

## 1. 现状诊断(为什么当前 L1/L2/L3 要重设计)

| 现状组件 | 位置 | 问题 |
|---|---|---|
| L1 per-block 截断(>3K tokens) | `src/compact.py:_compact_oversized_blocks` | 压缩时惰性执行;截断结果与原长无关但按 chars 换算,CJK 下突破自身目标 6 倍 |
| L2 LLM 摘要(触发 70%) | `src/compact.py:llm_compact_messages` | 触发过早(70%);keep_recent=4 条固定;退让阶梯 4→2→0 在 keep_recent=0 时产生不受控 collapse(丢光近期只留 2K 摘要) |
| L3 CONTEXT_COLLAPSE(触发 85%) | `src/compact.py:_context_collapse` | **架构上不可达**:外层触发在 70% 刚过线时执行,此时估值必然 <85%,`allow_collapse` 永远为 False;且 L2 退让阶梯必然收敛,"L2 不够 → defer" 分支走不到。死代码 |
| reactive compact | `src/agent_loop.py` prompt-too-long 路径 | 丢到剩 5 条消息、无摘要、直接丢弃(docstring 自认 teaching implementation),是事实上的最后防线 |

关键触发链:所有调用点(`agent_loop.py` ×3、`agent_teams.py` ×1)均不传 `allow_collapse`,L3 门控在压缩执行瞬间才检查,而触发本身发生在 70%,两者用同一估值 → L3 数学上不可达。

## 2. 事件模型:单一触发线 + 原子合并事件

| 项 | 设计 | 依据 |
|---|---|---|
| 触发线 | **85%**(85K / 100K 预算) | 与 Claude Code ~92%、OpenCode 87.5% 同量级,取保守值 |
| 事件动作 | **原子执行**:三段分级清理(见 §3)→ 结构化摘要 → 落到 ~35-40% | 恰好一次 cache miss;先清再摘同时把摘要 LLM 输入砍掉 60-80% |
| 迟滞 | 事件后记录水位;落点 35-40% + 增长 2-5K/轮 → 下次事件在 40-50 轮后 | 迟滞是唯一的频率控制 |
| 进度守卫 | 事件后释放 < 10% 预算 → 不空转,直接升级摘要 | 防止文本为主会话的清理空转循环 |

被否决的备选:**60% 独立清理层**(初版方案)。在有 cache 的前提下被否决——清@60% + 摘@85% 会在摘要必然发生时产生两次 cache miss(+35K token 等价成本),单次合并事件只 miss 一次。该方案仅在"endpoint 无前缀 cache"分支下重新成立(见 §6)。

同样被否决:**连续滑窗淘汰**(每轮固定淘汰最旧工具结果)——cache 场景下每轮碎一次 cache,是灾难;且改变短会话行为,违背"尽量晚、尽量少"。

## 3. 事件内部:工具输出三段分级

| 带 | 判定 | 形态 | 体量预算 | 理由 |
|---|---|---|---|---|
| recent 窗(在用) | 最近 ~20% 预算(~20K tokens)内的工具输出 | **原文,不动** | ~20K | 是 agent 手上的活,截断有害 |
| 次近带(刚出窗) | 窗外最近的 ~10 块 | **3K 残渣**(head+tail,报错通常在尾部) | ~30K | 保住"回头看报错"的能力;块数 × 常数 = 可预算 |
| 远带 | 其余全部 | **~20 token 占位符** `[cleared: {tool} {args}]`(保留 tool_use_id 满足 API 配对) | → 0 | 真正压总量的力;损失可逆(可重跑工具) |

**分工 invariant**:入口层管单块上界,3K 档管次近带的总量可预算,清理管总和。压缩目标长度与原长**不成比例**是有意的——目标由任务相关性决定,不由输出大小决定;比例映射会让每轮迭代增长失去上界,阈值数学失效。

**层级长度映射(四级级联,各管一件事)**:

| 层 | 位置 | 映射形式 | 常数 |
|---|---|---|---|
| 接口层 | read_file 分页(offset/limit)/ run_command `_truncate_output` | 模型请求时控制 + 上限 | 2000 行 / 30K chars |
| 入口层 | `_truncate_for_context` | 固定天花板 | 110K chars |
| 3K 截断 | `_compact_oversized_blocks`(前移到入栈) | 阶跃:>3K 一律 → 3K | 3K tokens |
| 清理 | 压缩事件内 | 常数占位符 | ~20 tokens |

## 4. 摘要与兜底

- **摘要 prompt**:替换现有 `COMPACT_SYSTEM_PROMPT`,补齐 Claude Code 8 段式核心——任务清单与完成状态、关键决策、文件改动、**下一步动作(next step)**,保证压缩后无缝续做;recent 窗按 token 比例保留(非固定条数)。
- **机械兜底**(替代现 L3 CONTEXT_COLLAPSE):摘要 LLM 调用连续失败时,不换一个 LLM prompt 再试,直接执行"清全部 tool_result + 保留全部对话原文"。**LLM 手段失败退回确定性手段,而不是换一个 LLM 手段**。
- **reactive 路径**(API 报 prompt too long):不再"丢到剩 5 条无摘要",改为清理 + 摘要的强制组合(此时 cache 已碎,无额外代价)。

## 5. 必修的正确性问题(与阈值无关,可先行)

1. **单位不一致 bug**:入口层 110K chars vs 预算 tokens,靠 4 chars/token 换算;CJK 是 1.5 tokens/char(`estimate_tokens`),导致:
   - L1 截到 12K chars 实际 ~18K tokens,突破自身 3K 目标 6 倍;
   - 入口层在 CJK 下根本限不住 token(110K chars 可达 165K tokens)。
   修法:截断长度用 `estimate_tokens` 反解,入口层按 token 计量。
2. **reactive_compact 丢弃式实现**:按 §4 替换为清理 + 摘要组合。

## 6. 条件分支(上线前用遥测裁决)

| 待决点 | 数据来源 | 判据 |
|---|---|---|
| **endpoint 是否真有前缀 cache** | verified-030 的 `ephemeral_*_input_tokens` 占比 | 无 cache → 改两段式:60% 独立清理层 + 85% 摘要层(无 cache 时早清纯赚) |
| 85% 是否有收益(压缩到底触不触发) | verified-030 中 `context.compact` 事件数/run | 多数 run 未触发过 → 阈值讨论整体推迟,只做 §5 |
| 工具输出占 context 比例 | 长 run 的 `estimated_tokens_before` 内 tool_result 占比 | <50% → 进度守卫会频繁兜底,考虑上调触发线至 65-70% |
| 次近带是否值得保留(3K 档) | L1 实际截断块的原长分布 | 极少触发 → 简化为两段(原文/占位符) |
| 入口层 110K 是否收紧到 ~50K chars | 同上 | 入口给 110K 只为压缩时砍到 12K 的块占比高 → 收紧 |

## 7. 与现状的差异清单

| 现状 | 新设计 |
|---|---|
| L2 触发 70%,keep_recent=4 条 | 单线 85%,recent 窗按 token 比例(~20K) |
| L3 COLLAPSE(架构上不可达,死代码) | 删除;机械兜底仅在摘要失败时启用 |
| L1 截断在压缩时惰性执行 | 前移到入栈时,之后冻结 |
| 无清理层 | 三段分级(原文 / 3K 残渣 / 占位符) |
| reactive 丢到剩 5 条、无摘要 | 清理 + 摘要强制组合 |
| 压完仍 >70% 会每轮重触发 | 迟滞 + 进度守卫 |

## 8. 测量语义与推迟分支

- **基线断裂**:任何压缩行为变化都会改变长任务上 agent 的实际行为,verified-030(19/30)中触发过压缩的 run 纵向不可比。若遥测显示触发极少,断裂面也很小。
- **推迟分支**:遥测确认压缩几乎不触发 → 只做 §5 正确性修复,§2-4 整体推迟。
- **硬重启条件**:
  1. 单 run 压缩触发 ≥2 次(摘要在压缩已摘要的内容,复利损失已发生);
  2. 任何 run 走到 reactive 丢弃路径;
  3. 打算对比"长迭代任务"跨基线的结果。
- **绑定要求**:实施 §2-4 应与下一轮 benchmark 重跑绑定,新旧数字不入同一张表。

**实施顺序**:§5(正确性)→ 遥测裁决(§6)→ 按裁决实施 §2-4,与重跑绑定。
