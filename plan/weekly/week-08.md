# 第 8 周 · MCP + Skills + 安全（P5）

**日期**：2026-08-10 ~ 08-16  
**项目**：`coding/projects/05-mcp-server`

**最小周验收**：
- [ ] MCP Client 能 `tools/list`
- [ ] `calculator` 或 `kb_search` 至少 1 个工具可调用
- [ ] prompt injection 测试 ≥3 条有记录

**进阶周验收**：
- [ ] `agent_run` 可调用，并能返回 `needs_approval`
- [ ] Skills 注册表有 JSON Schema 文档

---

## D50 · 周一 · MCP 协议入门

| 学习 30m | modelcontextprotocol.io 规范；JSON-RPC |
| 编码 120m | 最小 MCP Server：`tools/list` 返回 1 个工具 |
| 笔记 | `notes/concepts/07-MCP协议.md` |

## D51 · 周二 · 暴露第一个可调用工具

| 编码 120m | 优先封装 `calculator` 或 `kb_search` 为 MCP tool；P2 稳定时再接 `kb_search` |
| 测试 45m | MCP Inspector 或自写 client 调用 |

## D52 · 周三 · Skills 注册表

| 编码 120m | 最小 `skills/registry.yaml`；进阶再做 JSON Schema 文档生成 |

## D53 · 周四 · 权限 + 人工审批

| 编码 120m | 工具 risk_level；高风险返回 `needs_approval` |
| 笔记 | `notes/concepts/08-Agent安全.md` |

## D54 · 周五 · Prompt Injection 测试

| 编码 90m | `security/injection_cases.yaml` ≥3 条，进阶扩到 5 条 |
| 测试 45m | 跑安全测试记录通过率 |

## D55 · 周六 · Client 联调

| 编码 120m | Cursor MCP 配置或 Python MCP Client |

## D56 · 周日 · 复盘

| 文档 | `week-08-复盘.md`；`security_report_v0.md`；tag `p5-v0.1.0` |
| 计划 | 下周一：P6 架构 PRD |
