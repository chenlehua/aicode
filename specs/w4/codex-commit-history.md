# Codex 代码变更历史脉络分析

> 本文档梳理 OpenAI Codex CLI 项目的 commit history，分析其代码变更的演进脉络。

## 目录

1. [项目概览](#1-项目概览)
2. [时间线总览](#2-时间线总览)
3. [版本演进](#3-版本演进)
4. [核心功能演进](#4-核心功能演进)
5. [架构演进](#5-架构演进)
6. [主要贡献者](#6-主要贡献者)
7. [关键里程碑](#7-关键里程碑)

---

## 1. 项目概览

### 1.1 基本统计

| 指标 | 数值 |
|------|------|
| 总 Commit 数 | 11,448 |
| 项目起始时间 | 2025年4月 |
| 主要语言演进 | TypeScript → Rust |
| 当前版本 | 0.88.x |

### 1.2 月度 Commit 分布

```mermaid
xychart-beta
    title "Codex 月度 Commit 分布"
    x-axis ["Apr'25", "May'25", "Jun'25", "Jul'25", "Aug'25", "Sep'25", "Oct'25", "Nov'25", "Dec'25", "Jan'26"]
    y-axis "Commits" 0 --> 2000
    bar [793, 1124, 604, 754, 1761, 1431, 1214, 1308, 1381, 1078]
```

**观察**：
- 2025年8月达到开发高峰（1761 commits）
- 保持每月 1000+ commits 的高频迭代
- 显示出快速迭代的开发节奏

---

## 2. 时间线总览

```mermaid
timeline
    title Codex 项目演进时间线

    section 2025年4月
        项目启动 : 初始 TypeScript 实现
                 : Node.js CLI 框架
                 : 基础 Agent 循环

    section 2025年5月
        Rust 引入 : codex-rs 目录创建
                  : 核心逻辑 Rust 重写
                  : 沙箱系统设计

    section 2025年6月
        安全加固 : Seatbelt (macOS) 沙箱
                 : Landlock (Linux) 沙箱
                 : 执行策略系统

    section 2025年7-8月
        功能爆发 : MCP 协议支持
                 : TUI 界面完善
                 : SDK 发布
                 : App Server (IDE)

    section 2025年9-10月
        稳定优化 : apply_patch 工具完善
                 : 并行工具调用
                 : Windows 支持

    section 2025年11月-2026年1月
        高级功能 : 协作功能 (Collab)
                 : 多代理控制
                 : TUI2 实验版
                 : Web Search
```

---

## 3. 版本演进

### 3.1 主要版本里程碑

```mermaid
gitGraph
    commit id: "0.1.x" tag: "Initial"
    commit id: "0.7x" tag: "Rust Core"
    branch feature/sandbox
    commit id: "Sandbox"
    checkout main
    merge feature/sandbox
    commit id: "0.72.0"
    branch feature/mcp
    commit id: "MCP"
    checkout main
    merge feature/mcp
    commit id: "0.74.0"
    commit id: "0.75.0"
    commit id: "0.76.0"
    commit id: "0.77.0"
    commit id: "0.78.0" tag: "Stable"
    commit id: "0.79.x"
    commit id: "0.80.x"
    commit id: "0.81.x"
    commit id: "0.82.x"
    branch feature/collab
    commit id: "Collab"
    checkout main
    merge feature/collab
    commit id: "0.85.x"
    commit id: "0.86.x"
    commit id: "0.87.x"
    commit id: "0.88.x" tag: "Current"
```

### 3.2 版本发布统计

| 主版本 | Alpha 版本数 | 主要变更 |
|--------|-------------|---------|
| 0.72.x | 8 | 基础架构稳定 |
| 0.73.x | 3 | MCP 集成 |
| 0.74.x | 9 | 工具系统完善 |
| 0.75.x | 1 | 稳定版本 |
| 0.76.x | 9 | TUI 改进 |
| 0.77.x | 3 | SDK 增强 |
| 0.78.x | 12 | 沙箱优化 |
| 0.79.x | 3 | App Server |
| 0.80.x | 6 | 会话管理 |
| 0.81.x | 11 | Unified Exec |
| 0.82.x | 3 | 配置系统 |
| 0.85.x | 2 | 协作功能 |
| 0.86.x | 1 | 热重载 |
| 0.87.x | 2 | 多代理 |
| 0.88.x | 4+ | 当前开发 |

---

## 4. 核心功能演进

### 4.1 功能演进时间线

```mermaid
flowchart TB
    subgraph "Phase 1: 基础 (2025.04)"
        P1_1["初始 TypeScript 实现"]
        P1_2["基础 CLI 框架"]
        P1_3["OpenAI API 集成"]
        P1_4["简单 Agent 循环"]
    end

    subgraph "Phase 2: Rust 核心 (2025.05)"
        P2_1["codex-rs 引入"]
        P2_2["异步架构 (Tokio)"]
        P2_3["协议定义"]
        P2_4["沙箱设计"]
    end

    subgraph "Phase 3: 安全 (2025.06)"
        P3_1["macOS Seatbelt"]
        P3_2["Linux Landlock"]
        P3_3["执行策略"]
        P3_4["审批机制"]
    end

    subgraph "Phase 4: 扩展 (2025.07-08)"
        P4_1["MCP 协议"]
        P4_2["TUI 界面"]
        P4_3["TypeScript SDK"]
        P4_4["App Server"]
    end

    subgraph "Phase 5: 工具 (2025.09-10)"
        P5_1["apply_patch"]
        P5_2["Unified Exec"]
        P5_3["并行执行"]
        P5_4["Windows 沙箱"]
    end

    subgraph "Phase 6: 协作 (2025.11-2026.01)"
        P6_1["多代理控制"]
        P6_2["协作工具"]
        P6_3["TUI2"]
        P6_4["Web Search"]
    end

    P1_1 --> P1_2 --> P1_3 --> P1_4
    P1_4 --> P2_1
    P2_1 --> P2_2 --> P2_3 --> P2_4
    P2_4 --> P3_1
    P3_1 --> P3_2 --> P3_3 --> P3_4
    P3_4 --> P4_1
    P4_1 --> P4_2 --> P4_3 --> P4_4
    P4_4 --> P5_1
    P5_1 --> P5_2 --> P5_3 --> P5_4
    P5_4 --> P6_1
    P6_1 --> P6_2 --> P6_3 --> P6_4
```

### 4.2 沙箱系统演进

```mermaid
flowchart LR
    subgraph "2025.05-06"
        S1["基础沙箱设计"]
        S2["macOS Seatbelt"]
        S3["Linux Landlock + seccomp"]
    end

    subgraph "2025.08-09"
        S4["Windows Sandbox"]
        S5["沙箱策略系统"]
        S6["动态权限"]
    end

    subgraph "2025.11-2026.01"
        S7["只读绑定挂载"]
        S8["用户命名空间回退"]
        S9["提升沙箱 NUX"]
    end

    S1 --> S2 --> S3
    S3 --> S4 --> S5 --> S6
    S6 --> S7 --> S8 --> S9
```

**关键 Commit**:
- `feat: initial import of Rust implementation` - Rust 核心引入
- `[codex-rs] More fine-grained sandbox flag support on Linux` - Linux 沙箱
- `feat: add support for read-only bind mounts in the linux sandbox` - 只读挂载
- `linux-sandbox: fallback to userns when mountns is denied` - 命名空间回退

### 4.3 MCP 协议演进

```mermaid
flowchart TB
    subgraph "初期 (2025.07)"
        M1["MCP 类型定义"]
        M2["基础连接管理"]
        M3["工具注册"]
    end

    subgraph "中期 (2025.09)"
        M4["MCP 服务器热重载"]
        M5["静态回调 URI"]
        M6["工具名称清理"]
    end

    subgraph "近期 (2025.12-2026.01)"
        M7["线程 ID 传递"]
        M8["需求限制"]
        M9["禁用原因传播"]
    end

    M1 --> M2 --> M3
    M3 --> M4 --> M5 --> M6
    M6 --> M7 --> M8 --> M9
```

### 4.4 执行系统演进

```mermaid
flowchart LR
    subgraph "Shell 工具"
        E1["shell (基础)"]
        E2["local_shell"]
        E3["shell_command"]
    end

    subgraph "Unified Exec"
        E4["exec_command"]
        E5["write_stdin"]
        E6["长运行会话"]
    end

    subgraph "增强"
        E7["PTY 支持"]
        E8["管道回退"]
        E9["输出流控制"]
    end

    E1 --> E2 --> E3
    E3 --> E4 --> E5 --> E6
    E6 --> E7 --> E8 --> E9
```

### 4.5 协作功能演进

```mermaid
flowchart TB
    subgraph "2025.11 基础"
        C1["Agent Controller"]
        C2["spawn_agent"]
        C3["send_input"]
    end

    subgraph "2025.12 完善"
        C4["wait 工具"]
        C5["close_agent"]
        C6["事件发射"]
    end

    subgraph "2026.01 高级"
        C7["协作模式"]
        C8["角色预设"]
        C9["中断能力"]
        C10["多 ID 等待"]
    end

    C1 --> C2 --> C3
    C3 --> C4 --> C5 --> C6
    C6 --> C7 --> C8 --> C9 --> C10
```

---

## 5. 架构演进

### 5.1 从 TypeScript 到 Rust

```mermaid
flowchart TB
    subgraph "TypeScript 时代 (2025.04-05)"
        TS1["codex-cli/"]
        TS2["Node.js 运行时"]
        TS3["单进程架构"]
    end

    subgraph "Rust 过渡 (2025.05-06)"
        R1["codex-rs/core"]
        R2["Tokio 异步"]
        R3["多 crate 架构"]
    end

    subgraph "Rust 主导 (2025.06+)"
        R4["50+ crates"]
        R5["TypeScript → 启动器"]
        R6["完整生态"]
    end

    TS1 --> R1
    TS2 --> R2
    TS3 --> R3
    R1 --> R4
    R2 --> R5
    R3 --> R6
```

**关键转折点**:
```
59a180dde Initial commit                                    # 项目开始
31d0d7a30 feat: initial import of Rust implementation      # Rust 引入
```

### 5.2 模块架构演进

```mermaid
graph TB
    subgraph "早期 (少量模块)"
        E1["core"]
        E2["cli"]
        E3["protocol"]
    end

    subgraph "中期 (功能模块)"
        M1["tui"]
        M2["exec"]
        M3["sandbox"]
        M4["mcp"]
    end

    subgraph "当前 (50+ crates)"
        L1["核心层"]
        L2["界面层"]
        L3["执行层"]
        L4["安全层"]
        L5["集成层"]
    end

    E1 --> L1
    E2 --> L2
    E3 --> L1

    M1 --> L2
    M2 --> L3
    M3 --> L4
    M4 --> L5
```

### 5.3 配置系统演进

```mermaid
flowchart LR
    subgraph "早期"
        C1["简单 config.toml"]
        C2["CLI 参数"]
    end

    subgraph "中期"
        C3["分层配置"]
        C4["AGENTS.md 支持"]
        C5["约束验证"]
    end

    subgraph "当前"
        C6["ConfigBuilder"]
        C7["requirements.toml"]
        C8["热重载"]
    end

    C1 --> C3 --> C6
    C2 --> C4 --> C7
    C3 --> C5 --> C8
```

---

## 6. 主要贡献者

### 6.1 Top 20 贡献者

| 排名 | 贡献者 | Commits | 主要贡献领域 |
|------|--------|---------|-------------|
| 1 | Michael Bolin | 4,289 | 核心架构、TUI、工具系统 |
| 2 | Ahmed Ibrahim | 1,043 | 核心功能、MCP |
| 3 | github-actions[bot] | 744 | CI/CD 自动化 |
| 4 | jif-oai | 651 | 协作功能、Agent Control |
| 5 | kevin zhao | 361 | 执行系统 |
| 6 | Jeremy Rose | 335 | Windows 支持 |
| 7 | pakrym-oai | 303 | SDK、协议 |
| 8 | Rai (Michael Pokorny) | 251 | 沙箱系统 |
| 9 | Dylan Hurd | 192 | TUI、文档 |
| 10 | jimmyfraiture | 192 | 配置系统 |
| 11 | easong-openai | 165 | App Server |
| 12 | Daniel Edrisian | 163 | MCP 集成 |
| 13 | pap | 158 | 测试、质量 |
| 14 | Owen Lin | 154 | 功能开发 |
| 15 | aibrahim-oai | 149 | 核心功能 |
| 16 | Gabriel Peal | 132 | 执行系统 |
| 17 | Thibault Sottiaux | 124 | 界面改进 |
| 18 | Eric Traut | 120 | TypeScript |
| 19 | dependabot[bot] | 107 | 依赖更新 |
| 20 | Fouad Matin | 100 | 功能开发 |

### 6.2 贡献分布

```mermaid
pie title Commit 贡献分布
    "Michael Bolin" : 37.5
    "Ahmed Ibrahim" : 9.1
    "自动化" : 7.4
    "jif-oai" : 5.7
    "kevin zhao" : 3.2
    "Jeremy Rose" : 2.9
    "其他" : 34.2
```

---

## 7. 关键里程碑

### 7.1 里程碑列表

```mermaid
flowchart TB
    subgraph "2025年4月"
        M1["🚀 项目启动<br/>Initial commit"]
    end

    subgraph "2025年5月"
        M2["🦀 Rust 核心引入<br/>codex-rs 目录"]
    end

    subgraph "2025年6月"
        M3["🔒 沙箱系统完成<br/>多平台支持"]
    end

    subgraph "2025年7月"
        M4["🔌 MCP 协议支持<br/>外部工具集成"]
    end

    subgraph "2025年8月"
        M5["📱 TUI 完善<br/>交互式界面"]
        M6["📦 SDK 发布<br/>TypeScript SDK"]
    end

    subgraph "2025年9月"
        M7["🖥️ App Server<br/>IDE 集成"]
    end

    subgraph "2025年10月"
        M8["🪟 Windows 支持<br/>完整跨平台"]
    end

    subgraph "2025年11月"
        M9["🤝 协作功能<br/>多代理控制"]
    end

    subgraph "2025年12月"
        M10["🔄 热重载<br/>MCP 服务器"]
    end

    subgraph "2026年1月"
        M11["🌐 Web Search<br/>网络搜索"]
        M12["📋 TUI2<br/>实验界面"]
    end

    M1 --> M2 --> M3 --> M4
    M4 --> M5 --> M6 --> M7
    M7 --> M8 --> M9 --> M10
    M10 --> M11 --> M12
```

### 7.2 关键 Commit 详解

#### 项目启动
```
59a180dde Initial commit
ae7b518c5 Initial commit
```
- 项目初始化
- TypeScript/Node.js 架构

#### Rust 核心引入
```
31d0d7a30 feat: initial import of Rust implementation of Codex CLI in codex-rs/ (#629)
```
- 标志性的架构转型
- 引入 50+ crate 的 Rust 实现

#### 沙箱系统
```
b34ed2ab8 [codex-rs] More fine-grained sandbox flag support on Linux (#632)
```
- Linux Landlock + seccomp
- macOS Seatbelt
- 执行策略系统

#### MCP 支持
```
987dd7fde Chore: remove rmcp feature and exp flag usages (#8087)
53f53173a chore: upgrade rmcp crate from 0.10.0 to 0.12.0 (#8288)
```
- MCP 协议从实验性到稳定
- 外部工具生态集成

#### 协作功能
```
b43e04d9c feat: agent controller (#8783)
246f50655 Introduce collaboration modes (#9340)
```
- 多代理控制架构
- 协作模式和角色预设

#### Unified Exec
```
72b95db12 feat: intercept apply_patch for unified_exec (#7446)
813bdb901 feat: fallback unified_exec to shell_command (#8075)
```
- 统一的执行系统
- 长运行会话支持

---

## 8. 代码变更模式分析

### 8.1 Commit 类型分布

```mermaid
pie title Commit 类型分布
    "feat: 功能" : 35
    "fix: 修复" : 25
    "chore: 杂项" : 20
    "docs: 文档" : 5
    "refactor: 重构" : 8
    "test: 测试" : 5
    "其他" : 2
```

### 8.2 变更频率热图

| 模块 | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec | Jan |
|------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| core | 🟡 | 🟢 | 🟢 | 🟢 | 🔴 | 🔴 | 🟢 | 🟢 | 🟢 | 🟢 |
| tui | ⚪ | 🟡 | 🟢 | 🟢 | 🔴 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| sandbox | ⚪ | 🟡 | 🔴 | 🟢 | 🟢 | 🟢 | 🟡 | 🟡 | 🟢 | 🟢 |
| mcp | ⚪ | ⚪ | 🟡 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| sdk | ⚪ | ⚪ | ⚪ | 🟡 | 🟢 | 🟢 | 🟢 | 🟡 | 🟡 | 🟡 |
| collab | ⚪ | ⚪ | ⚪ | ⚪ | ⚪ | ⚪ | ⚪ | 🟢 | 🔴 | 🔴 |

图例: ⚪无 🟡低 🟢中 🔴高

---

## 9. 总结

### 9.1 项目演进特点

1. **快速迭代**
   - 月均 1000+ commits
   - 频繁的 alpha 版本发布
   - 持续的功能迭代

2. **架构演进**
   - TypeScript → Rust 的成功迁移
   - 模块化的 crate 架构
   - 清晰的分层设计

3. **安全优先**
   - 早期就引入沙箱系统
   - 多平台安全支持
   - 持续的安全加固

4. **生态扩展**
   - MCP 协议支持外部工具
   - SDK 支持程序化使用
   - IDE 集成 (App Server)

5. **协作能力**
   - 多代理控制
   - 协作工具
   - 角色预设

### 9.2 技术债务管理

```mermaid
flowchart LR
    subgraph "已清理"
        D1["TypeScript 代码迁移"]
        D2["实验性功能稳定化"]
        D3["API 规范化"]
    end

    subgraph "进行中"
        D4["TUI2 统一"]
        D5["配置系统简化"]
    end

    subgraph "计划中"
        D6["测试覆盖提升"]
        D7["文档完善"]
    end

    D1 --> D4
    D2 --> D5
    D3 --> D6 --> D7
```

### 9.3 未来展望

基于 commit history 的趋势，可以预见：

- **协作功能深化** - 更强大的多代理协作
- **TUI2 成熟** - 统一的终端界面
- **生态扩展** - 更多 MCP 集成
- **性能优化** - 持续的 Rust 优化
- **跨平台完善** - Windows 体验提升

---

*本文档基于 Codex 仓库 11,448 个 commits 的分析生成，版本日期：2026-01-19*
