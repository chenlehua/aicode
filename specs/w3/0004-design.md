# Raflow 详细设计文档

> **版本**: 2.0.0  
> **更新日期**: 2026-01-18  
> **基于代码版本**: 0.1.0

---

## 1. 概述

### 1.1 项目简介

Raflow 是一款类似 [Wispr Flow](https://wisprflow.ai/) 的语音转文字桌面应用，基于 **Tauri 2** + **Svelte 5** + **Rust 2024 Edition** 构建。应用使用 **ElevenLabs Scribe v2 Realtime API** 进行实时语音识别，支持**实时文本插入**——在用户说话的同时，转录文本会实时出现在目标应用的光标位置。

### 1.2 核心功能

| 功能 | 描述 |
|------|------|
| **实时语音转文字** | 基于 ElevenLabs Scribe v2 Realtime API，延迟约 150-250ms |
| **实时文本插入** | 转录文本实时插入到目标应用光标位置，支持增量更新 |
| **音频降噪** | 使用 nnnoiseless (RNNoise) 进行实时音频降噪 |
| **全局快捷键** | 可配置的全局快捷键切换录音（默认 ⌘+⇧+\） |
| **系统托盘** | 后台运行，托盘图标快速访问 |
| **多语言支持** | 支持中文、英语、日语、韩语等多种语言 |
| **VAD 检测** | 语音活动检测，自动分段提交 |
| **设置持久化** | 配置自动保存到本地文件 |

### 1.3 系统架构总览

```mermaid
graph TB
    subgraph "用户交互层"
        A[🎹 全局快捷键<br/>Cmd+Shift+\] --> B[状态切换]
        C[📱 系统托盘] --> D[菜单操作]
        E[⚙️ 设置界面] --> F[配置管理]
    end

    subgraph "Tauri 2 应用"
        subgraph "前端 WebView (Svelte 5)"
            G[StatusBar 组件]
            H[TranscriptPreview 组件]
            I[SettingsPanel 组件]
            J[HotkeyHint 组件]
        end

        subgraph "Rust 后端"
            K[🎤 音频捕获模块<br/>cpal + nnnoiseless]
            L[🌐 WebSocket 客户端<br/>tokio-tungstenite]
            M[⌨️ 文本插入模块<br/>enigo + arboard]
            N[🔄 状态管理器<br/>ArcSwap + RwLock]
        end
    end

    subgraph "外部服务"
        O[☁️ ElevenLabs<br/>Scribe v2 Realtime API]
    end

    subgraph "目标应用"
        P[📝 当前活跃窗口<br/>文本输入位置]
    end

    B --> N
    D --> N
    N --> K
    K -->|PCM 16kHz| L
    L -->|WebSocket| O
    O -->|转录文本| L
    L --> N
    L --> M
    M -->|实时插入| P
    N --> G
    N --> H
    F --> N
```

---

## 2. 技术栈

### 2.1 后端依赖 (Rust)

| 依赖包 | 版本 | 用途 |
|--------|------|------|
| `tauri` | 2.0 | 应用框架 |
| `tauri-plugin-global-shortcut` | 2.0 | 全局快捷键 |
| `tokio` | 1.49 | 异步运行时 |
| `tokio-tungstenite` | 0.28 | WebSocket 客户端 |
| `cpal` | 0.15 | 跨平台音频捕获 |
| `nnnoiseless` | 0.5 | RNNoise 音频降噪 |
| `enigo` | 0.2 | 键盘/鼠标模拟 |
| `arboard` | 3.6 | 剪贴板操作 |
| `arc-swap` | 1.7 | 无锁原子指针交换 |
| `serde` / `serde_json` | 1.0 | 序列化 |
| `base64` | 0.22 | Base64 编解码 |
| `thiserror` | 2.0 | 错误定义 |
| `dirs` | 6.0 | 跨平台目录 |

### 2.2 前端依赖 (TypeScript)

| 依赖包 | 版本 | 用途 |
|--------|------|------|
| `svelte` | ^5.46 | UI 框架 |
| `vite` | ^6.0 | 构建工具 |
| `@tauri-apps/api` | ^2.9 | Tauri JS API |
| `@tauri-apps/plugin-global-shortcut` | ^2.3 | 快捷键插件 |
| `typescript` | ^5.7 | 类型支持 |

### 2.3 Rust 版本要求

```toml
[package]
edition = "2024"
rust-version = "1.85"
```

---

## 3. 项目结构

```
raflow/
├── src/                              # Svelte 前端代码
│   ├── App.svelte                   # 主应用组件
│   ├── main.ts                      # 入口文件
│   └── lib/
│       ├── components/              # UI 组件
│       │   ├── StatusBar.svelte     # 状态栏
│       │   ├── TranscriptPreview.svelte  # 转录预览
│       │   ├── SettingsPanel.svelte # 设置面板
│       │   └── HotkeyHint.svelte    # 快捷键提示
│       └── stores/                  # Svelte stores
│           ├── appState.ts          # 应用状态
│           └── settings.ts          # 设置状态
│
├── src-tauri/                       # Rust 后端代码
│   ├── Cargo.toml                   # Rust 依赖
│   ├── tauri.conf.json              # Tauri 配置
│   ├── capabilities/main.json       # 权限配置
│   ├── entitlements.plist           # macOS 权限
│   ├── Info.plist                   # macOS 应用信息
│   └── src/
│       ├── main.rs                  # 应用入口
│       ├── lib.rs                   # 库导出
│       ├── commands.rs              # Tauri 命令 (423 行)
│       ├── state.rs                 # 状态管理 (231 行)
│       ├── error.rs                 # 错误定义 (98 行)
│       ├── hotkey.rs                # 快捷键处理 (221 行)
│       ├── tray.rs                  # 系统托盘 (110 行)
│       ├── settings_store.rs        # 设置持久化 (66 行)
│       ├── audio/                   # 音频处理模块
│       │   ├── mod.rs               # 模块导出
│       │   ├── capture.rs           # 音频捕获 (340 行)
│       │   └── denoise.rs           # 音频降噪 (151 行)
│       ├── transcriber/             # 转录客户端模块
│       │   ├── mod.rs               # 模块导出
│       │   ├── client.rs            # WebSocket 客户端 (279 行)
│       │   └── message.rs           # 消息类型定义 (204 行)
│       └── input/                   # 文本插入模块
│           ├── mod.rs               # 模块导出
│           ├── inserter.rs          # 文本插入器 (455 行)
│           └── clipboard.rs         # 剪贴板管理 (35 行)
│
├── package.json                     # 前端依赖
├── vite.config.ts                   # Vite 配置
├── tsconfig.json                    # TypeScript 配置
└── README.md                        # 项目说明
```

---

## 4. 核心模块设计

### 4.1 模块依赖关系

```mermaid
graph TB
    subgraph "入口层"
        main[main.rs<br/>应用入口]
    end

    subgraph "核心模块"
        commands[commands.rs<br/>Tauri 命令]
        state[state.rs<br/>状态管理]
        hotkey[hotkey.rs<br/>快捷键]
        tray[tray.rs<br/>系统托盘]
        settings[settings_store.rs<br/>设置持久化]
    end

    subgraph "音频模块"
        audio_mod[audio/mod.rs]
        capture[audio/capture.rs<br/>音频捕获]
        denoise[audio/denoise.rs<br/>降噪处理]
    end

    subgraph "转录模块"
        trans_mod[transcriber/mod.rs]
        client[transcriber/client.rs<br/>WebSocket 客户端]
        message[transcriber/message.rs<br/>消息类型]
    end

    subgraph "输入模块"
        input_mod[input/mod.rs]
        inserter[input/inserter.rs<br/>文本插入]
        clipboard[input/clipboard.rs<br/>剪贴板]
    end

    subgraph "错误处理"
        error[error.rs<br/>错误类型]
    end

    main --> commands
    main --> state
    main --> hotkey
    main --> tray
    main --> settings

    commands --> state
    commands --> audio_mod
    commands --> trans_mod
    commands --> input_mod
    commands --> settings

    hotkey --> state
    hotkey --> input_mod

    audio_mod --> capture
    audio_mod --> denoise
    capture --> denoise

    trans_mod --> client
    trans_mod --> message
    client --> message

    input_mod --> inserter
    input_mod --> clipboard
    inserter --> clipboard

    commands --> error
    state --> error
    capture --> error
    client --> error
    inserter --> error
```

### 4.2 类型定义

```mermaid
classDiagram
    class AppState {
        -recording_state: RwLock~RecordingState~
        -connection_status: RwLock~ConnectionStatus~
        -transcript_buffer: RwLock~String~
        -recording_start_ms: AtomicU64
        -is_recording: AtomicBool
        -settings: ArcSwap~AppSettings~
        -target_app: RwLock~Option~String~~
        +is_recording() bool
        +set_recording(bool)
        +get_recording_state() RecordingState
        +set_connection_status(ConnectionStatus)
        +append_transcript(str)
        +take_transcript() String
        +get_settings() Arc~AppSettings~
        +update_settings(AppSettings)
        +set_target_app(Option~String~)
    }

    class AppSettings {
        +api_key: String
        +language_code: String
        +sample_rate: u32
        +vad_enabled: bool
        +vad_silence_threshold: f32
        +hotkey: String
    }

    class RecordingState {
        <<enumeration>>
        Idle
        Recording
        Processing
    }

    class ConnectionStatus {
        <<enumeration>>
        Disconnected
        Connecting
        Connected
        Error
    }

    class RecordingSession {
        +audio_tx: Sender~Vec~i16~~
        +shutdown_tx: Sender~()~
        +transcriber_handle: JoinHandle~()~
        +transcript_handler: JoinHandle~()~
    }

    class AudioCapture {
        -stream: Option~cpal::Stream~
        -is_recording: Arc~AtomicBool~
        +start(sample_rate, audio_tx)
        +stop()
        +is_recording() bool
    }

    class AudioDenoiser {
        -state: Box~DenoiseState~
        -buffer: Vec~f32~
        +process(input) Vec~f32~
        +flush() Vec~f32~
        +reset()
    }

    class TranscriberClient {
        -api_key: String
        -language_code: String
        -vad_enabled: bool
        -vad_threshold: f32
        +run(audio_rx, transcript_tx, shutdown_rx)
    }

    class TranscriptEvent {
        <<enumeration>>
        Partial(String)
        Committed(String)
    }

    class TextInserter {
        -clipboard: ClipboardManager
        +insert_text_to_app(text, target_app)
        +copy_to_clipboard(text)
        +send_paste_keystroke()
        +send_backspace_keystrokes(count)
    }

    AppState --> AppSettings
    AppState --> RecordingState
    AppState --> ConnectionStatus
    TranscriberClient --> TranscriptEvent
    TextInserter --> ClipboardManager
```

---

## 5. 应用启动流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant Main as main.rs
    participant Plugin as GlobalShortcut 插件
    participant State as AppState
    participant Settings as settings_store
    participant Tray as tray.rs
    participant Hotkey as hotkey.rs
    participant Window as WebView 窗口

    User->>Main: 启动应用
    Main->>Main: 初始化 env_logger
    Main->>Main: tauri::Builder::default()
    
    rect rgb(240, 248, 255)
        Note over Main: setup() 回调
        Main->>Plugin: 注册 global_shortcut 插件
        Main->>State: create_app_state()
        Main->>Settings: load_settings()
        Settings-->>Main: AppSettings
        Main->>State: update_settings()
        Main->>Tray: create_tray()
        Tray-->>Main: TrayIcon
        Main->>Hotkey: register_shortcut()
        Hotkey-->>Main: 注册成功
    end

    Main->>Window: get_webview_window("main")
    
    alt debug 模式
        Main->>Window: window.show()
    else release 模式
        Main->>Window: window.hide()
    end

    Main->>Main: 注册 Tauri 命令处理器
    Main->>Main: app.run()
    
    Note over Main: 应用进入事件循环
```

---

## 6. 录音与转录流程

### 6.1 完整录音流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant Hotkey as 快捷键处理
    participant Frontend as 前端
    participant Commands as commands.rs
    participant State as AppState
    participant Audio as AudioCapture
    participant Denoise as AudioDenoiser
    participant WS as TranscriberClient
    participant API as ElevenLabs API
    participant Inserter as TextInserter
    participant Target as 目标应用

    User->>Hotkey: 按下 Cmd+Shift+\
    Hotkey->>Hotkey: 捕获当前前台应用
    Hotkey->>State: set_target_app(app_name)
    Hotkey->>Frontend: emit("toggle-recording")
    Frontend->>Commands: toggle_recording()
    
    rect rgb(240, 255, 240)
        Note over Commands: 开始录音
        Commands->>State: 检查 API Key
        Commands->>State: clear_transcript()
        Commands->>Audio: 创建音频通道 (500 buffer)
        Commands->>Audio: std::thread::spawn()
        Audio->>Denoise: 初始化 AudioDenoiser
        
        Commands->>WS: tokio::spawn() TranscriberClient
        WS->>API: WebSocket 连接
        API-->>WS: session_started
        
        Commands->>Commands: tokio::spawn() transcript_handler
        Commands->>State: set_recording(true)
        Commands->>Frontend: emit("recording-started")
    end

    loop 录音中
        Audio->>Audio: cpal 捕获音频
        Audio->>Denoise: 重采样到 48kHz
        Denoise->>Denoise: RNNoise 降噪
        Denoise->>Audio: 重采样到 16kHz
        Audio->>WS: audio_tx.send(pcm16)
        
        WS->>WS: 缓冲 250ms 音频
        WS->>API: input_audio_chunk (Base64)
        API-->>WS: partial_transcript
        WS->>Commands: TranscriptEvent::Partial
        
        Commands->>Inserter: copy_to_clipboard(new_text)
        Commands->>Commands: run_on_main_thread()
        Commands->>Inserter: send_backspace_keystrokes(old_len)
        Commands->>Inserter: send_paste_keystroke()
        Inserter->>Target: 实时插入文本
        
        API-->>WS: committed_transcript
        WS->>Commands: TranscriptEvent::Committed
        Commands->>State: append_transcript()
        Commands->>Inserter: 插入空格分隔
    end

    User->>Hotkey: 再次按下 Cmd+Shift+\
    Hotkey->>Frontend: emit("toggle-recording")
    Frontend->>Commands: toggle_recording()
    
    rect rgb(255, 240, 240)
        Note over Commands: 停止录音
        Commands->>WS: shutdown_tx.send()
        Commands->>Audio: drop(audio_tx)
        WS->>API: commit 最后音频
        WS->>WS: 等待最终转录 (500ms)
        Commands->>State: set_recording(false)
        Commands->>State: set_target_app(None)
        Commands->>Frontend: emit("recording-stopped")
    end
```

### 6.2 状态机

```mermaid
stateDiagram-v2
    [*] --> Idle: 应用启动

    state Idle {
        [*] --> 等待触发
        等待触发 --> 等待触发: 监听快捷键/按钮
    }

    Idle --> Recording: toggle_recording() & API Key 有效
    Idle --> Error: toggle_recording() & API Key 无效

    state Recording {
        [*] --> 捕获音频
        捕获音频 --> 降噪处理: cpal 数据
        降噪处理 --> 发送音频: nnnoiseless
        发送音频 --> 接收转录: WebSocket
        接收转录 --> 实时插入: partial/committed
        实时插入 --> 捕获音频
    }

    Recording --> Processing: toggle_recording()

    state Processing {
        [*] --> 发送关闭信号
        发送关闭信号 --> 等待最终转录: shutdown_tx
        等待最终转录 --> 清理资源: timeout 500ms
    }

    Processing --> Idle: 处理完成
    Error --> Idle: 用户确认
```

---

## 7. 音频处理流水线

### 7.1 音频处理架构

```mermaid
flowchart LR
    subgraph "硬件层"
        MIC[🎤 麦克风]
    end

    subgraph "cpal 音频捕获"
        direction TB
        CPAL[cpal::Stream]
        FMT{格式检测}
        CPAL --> FMT
        FMT -->|F32| F32[Float32 处理]
        FMT -->|I16| I16[Int16 处理]
        FMT -->|I32| I32[Int32 处理]
    end

    subgraph "预处理"
        MONO[立体声转单声道]
    end

    subgraph "降噪处理"
        direction TB
        UP[上采样<br/>→ 48kHz]
        DENOISE[nnnoiseless<br/>RNNoise 降噪]
        DOWN[下采样<br/>→ 16kHz]
        UP --> DENOISE --> DOWN
    end

    subgraph "编码传输"
        PCM[PCM 16-bit]
        B64[Base64 编码]
        WS[WebSocket 发送]
    end

    MIC --> CPAL
    F32 --> MONO
    I16 --> MONO
    I32 --> MONO
    MONO --> UP
    DOWN --> PCM --> B64 --> WS
```

### 7.2 降噪处理细节

```mermaid
flowchart TB
    subgraph "AudioDenoiser"
        INPUT[输入音频<br/>48kHz mono f32]
        BUFFER[内部缓冲区<br/>Vec~f32~]
        
        INPUT --> BUFFER
        
        BUFFER --> CHECK{缓冲区 >= 480 样本?}
        CHECK -->|否| WAIT[等待更多数据]
        CHECK -->|是| PROCESS[处理一帧]
        
        PROCESS --> FRAME[取出 480 样本]
        FRAME --> DENOISE[DenoiseState::process_frame]
        DENOISE --> OUTPUT[输出降噪帧]
        OUTPUT --> CHECK
        
        WAIT --> INPUT
    end

    subgraph "参数说明"
        PARAM1[帧大小: 480 样本]
        PARAM2[采样率: 48000 Hz]
        PARAM3[帧时长: 10ms]
    end
```

### 7.3 重采样算法

```rust
/// 线性插值重采样
pub fn resample(input: &[f32], source_rate: u32, target_rate: u32) -> Vec<f32> {
    let ratio = target_rate as f64 / source_rate as f64;
    let output_len = (input.len() as f64 * ratio).ceil() as usize;
    
    (0..output_len).map(|i| {
        let src_idx = i as f64 / ratio;
        let src_floor = src_idx.floor() as usize;
        let frac = (src_idx - src_floor as f64) as f32;
        
        if src_floor + 1 < input.len() {
            input[src_floor] * (1.0 - frac) + input[src_floor + 1] * frac
        } else {
            input.get(src_floor).copied().unwrap_or(0.0)
        }
    }).collect()
}
```

---

## 8. WebSocket 通信协议

### 8.1 连接流程

```mermaid
sequenceDiagram
    participant Client as Rust 客户端
    participant WS as WebSocket
    participant API as ElevenLabs API

    Client->>WS: 建立连接
    Note over WS: URL: wss://api.elevenlabs.io/v1/speech-to-text/realtime
    Note over WS: 查询参数:<br/>model_id=scribe_v2_realtime<br/>sample_rate=16000<br/>language_code=zho<br/>vad_commit_strategy=true<br/>vad_silence_threshold_secs=0.5
    
    WS->>API: WebSocket Upgrade
    Note over WS: Header: xi-api-key: xxx

    API-->>WS: 101 Switching Protocols
    API-->>Client: session_started
    Note over Client: session_id: xxx<br/>config: {...}

    loop 音频流传输
        Client->>API: input_audio_chunk
        Note over Client,API: message_type: "input_audio_chunk"<br/>audio_base_64: "..."<br/>commit: false<br/>sample_rate: 16000
        
        API-->>Client: partial_transcript
        Note over API,Client: message_type: "partial_transcript"<br/>text: "你好"
    end

    Note over API: VAD 检测到静音
    API-->>Client: committed_transcript
    Note over API,Client: message_type: "committed_transcript"<br/>text: "你好世界"

    Client->>API: 发送 commit=true
    API-->>Client: committed_transcript

    Client->>WS: 关闭连接
    WS->>API: Close Frame
```

### 8.2 消息类型定义

```mermaid
classDiagram
    class AudioChunkMessage {
        +message_type: "input_audio_chunk"
        +audio_base_64: String
        +commit: bool
        +sample_rate: u32
    }

    class ServerMessage {
        <<enumeration>>
        SessionStarted
        PartialTranscript
        CommittedTranscript
        Error
        Unknown
    }

    class SessionStartedMessage {
        +session_id: String
        +config: Option~SessionConfig~
    }

    class SessionConfig {
        +sample_rate: u32
        +audio_format: String
        +language_code: String
        +model_id: String
        +vad_commit_strategy: bool
        +vad_silence_threshold_secs: f32
    }

    class TranscriptMessage {
        +text: String
        +timestamp: Option~f64~
    }

    class ErrorMessage {
        +error: String
        +code: Option~String~
    }

    ServerMessage --> SessionStartedMessage
    ServerMessage --> TranscriptMessage
    ServerMessage --> ErrorMessage
    SessionStartedMessage --> SessionConfig
```

---

## 9. 实时文本插入机制

### 9.1 文本插入流程

```mermaid
flowchart TD
    subgraph "接收转录事件"
        E1[TranscriptEvent::Partial]
        E2[TranscriptEvent::Committed]
    end

    subgraph "增量更新算法"
        A[接收新文本]
        B[计算旧文本字符数]
        C[复制新文本到剪贴板]
        D{在主线程执行}
        E[发送 N 个退格键]
        F[发送 Cmd+V 粘贴]
    end

    subgraph "macOS 特殊处理"
        G[enigo 必须在主线程]
        H[run_on_main_thread]
    end

    E1 --> A
    E2 --> A
    A --> B
    B --> C
    C --> D
    D -->|是| H
    H --> E
    E --> F

    subgraph "结果"
        R1[文本实时出现在目标应用]
        R2[用户可以看到逐字更新]
    end

    F --> R1
    R1 --> R2
```

### 9.2 目标应用捕获

```mermaid
sequenceDiagram
    participant User as 用户
    participant App as 目标应用
    participant Hotkey as 快捷键处理
    participant AS as AppleScript
    participant State as AppState

    Note over User,App: 用户在目标应用中编辑
    User->>Hotkey: 按下快捷键
    
    Hotkey->>AS: 执行 AppleScript
    Note over AS: tell application "System Events"<br/>get name of first process<br/>whose frontmost is true
    AS-->>Hotkey: 应用名称 (如 "Code")
    
    Hotkey->>Hotkey: 过滤排除 "Raflow"
    Hotkey->>State: set_target_app("Code")
    
    Note over State: 保存目标应用供后续使用
```

### 9.3 AppleScript 交互

```mermaid
flowchart LR
    subgraph "Rust 代码"
        R1[Command::new osascript]
        R2[-e 参数]
        R3[AppleScript 脚本]
    end

    subgraph "系统调用"
        S1[osascript 执行]
    end

    subgraph "AppleScript 操作"
        A1[激活目标应用]
        A2[发送按键]
        A3[执行粘贴]
    end

    R1 --> S1
    R2 --> S1
    R3 --> S1
    S1 --> A1
    A1 --> A2
    A2 --> A3
```

---

## 10. 状态管理

### 10.1 状态架构

```mermaid
graph TB
    subgraph "AppState (Rust)"
        subgraph "原子操作"
            A1[is_recording: AtomicBool]
            A2[recording_start_ms: AtomicU64]
        end
        
        subgraph "读写锁"
            B1[recording_state: RwLock]
            B2[connection_status: RwLock]
            B3[transcript_buffer: RwLock]
            B4[target_app: RwLock]
        end
        
        subgraph "无锁配置"
            C1[settings: ArcSwap~AppSettings~]
        end
    end

    subgraph "前端 Store (Svelte)"
        D1[appState Store]
        D2[settings Store]
    end

    subgraph "Tauri 命令"
        E1[get_status]
        E2[toggle_recording]
        E3[get_settings]
        E4[update_settings]
    end

    E1 --> B1
    E1 --> B2
    E1 --> B3
    E2 --> A1
    E3 --> C1
    E4 --> C1

    D1 <--> E1
    D1 <--> E2
    D2 <--> E3
    D2 <--> E4
```

### 10.2 并发访问模式

| 数据 | 类型 | 访问模式 | 选择理由 |
|------|------|----------|----------|
| `is_recording` | `AtomicBool` | 高频读取 | 简单布尔值，原子操作最高效 |
| `recording_start_ms` | `AtomicU64` | 低频读取 | 时间戳，原子操作足够 |
| `recording_state` | `RwLock<RecordingState>` | 读多写少 | 枚举状态，需要互斥 |
| `connection_status` | `RwLock<ConnectionStatus>` | 读多写少 | 枚举状态，需要互斥 |
| `transcript_buffer` | `RwLock<String>` | 频繁追加 | 字符串操作，需要互斥 |
| `settings` | `ArcSwap<AppSettings>` | 极少修改 | 配置很少改动，ArcSwap 无锁替换 |

---

## 11. 前端设计

### 11.1 组件结构

```mermaid
graph TB
    subgraph "App.svelte"
        APP[主应用组件]
    end

    subgraph "UI 组件"
        SB[StatusBar.svelte<br/>状态栏]
        TP[TranscriptPreview.svelte<br/>转录预览]
        SP[SettingsPanel.svelte<br/>设置面板]
        HH[HotkeyHint.svelte<br/>快捷键提示]
    end

    subgraph "状态管理"
        AS[appState.ts<br/>应用状态 Store]
        SS[settings.ts<br/>设置 Store]
    end

    APP --> SB
    APP --> TP
    APP --> SP
    APP --> HH

    SB --> AS
    TP --> AS
    SP --> SS
    HH --> SS
```

### 11.2 事件通信

```mermaid
sequenceDiagram
    participant BE as Rust 后端
    participant EV as Tauri 事件
    participant ST as Svelte Store
    participant UI as UI 组件

    BE->>EV: emit("recording-started")
    EV->>ST: appState.update()
    ST->>UI: 响应式更新

    BE->>EV: emit("partial-transcript", text)
    EV->>ST: appState.setTranscript()
    ST->>UI: TranscriptPreview 更新

    BE->>EV: emit("toggle-recording")
    Note over EV: 来自快捷键/托盘
    EV->>ST: appState.toggleRecording()
    ST->>BE: invoke("toggle_recording")
```

### 11.3 界面布局

```
┌─────────────────────────────────────────┐
│  Raflow                              ─ □ │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ ● Recording...                  │   │ ← StatusBar
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ TRANSCRIPT                      │   │
│  ├─────────────────────────────────┤   │
│  │                                 │   │ ← TranscriptPreview
│  │  "你好，这是一段测试..."       │   │
│  │                                 │   │
│  └─────────────────────────────────┘   │
│                                         │
│       Press ⌘ ⇧ \ to toggle            │ ← HotkeyHint
│                                         │
│  ┌──────────────┐  ┌───────────┐       │
│  │ Stop Recording│  │ Settings  │       │ ← 操作按钮
│  └──────────────┘  └───────────┘       │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Settings                        │   │
│  │ ─────────────────────────────── │   │
│  │ ElevenLabs API Key              │   │ ← SettingsPanel
│  │ [••••••••••••••••••••] 👁️       │   │   (可折叠)
│  │                                 │   │
│  │ Language: [Chinese ▼]           │   │
│  │ Hotkey: [Cmd+Shift+\ ]          │   │
│  │ ☑ Enable VAD                    │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

---

## 12. 配置持久化

### 12.1 配置文件位置

| 平台 | 路径 |
|------|------|
| macOS | `~/.config/raflow/settings.json` |
| Windows | `%APPDATA%\raflow\settings.json` |
| Linux | `~/.config/raflow/settings.json` |

### 12.2 配置文件格式

```json
{
  "api_key": "sk-xxxxxxxxxxxxxxxxxxxx",
  "language_code": "zho",
  "sample_rate": 16000,
  "vad_enabled": true,
  "vad_silence_threshold": 0.5,
  "hotkey": "CommandOrControl+Shift+\\"
}
```

### 12.3 配置加载流程

```mermaid
flowchart TD
    A[应用启动] --> B{配置文件存在?}
    B -->|是| C[读取 JSON 文件]
    C --> D{解析成功?}
    D -->|是| E[使用加载的配置]
    D -->|否| F[使用默认配置]
    B -->|否| F
    F --> G[创建默认 AppSettings]
    E --> H[更新 AppState]
    G --> H
    H --> I[应用就绪]
```

---

## 13. 错误处理

### 13.1 错误类型

```mermaid
graph TB
    subgraph "AppError 枚举"
        E1[Audio<br/>音频设备错误]
        E2[WebSocket<br/>网络连接错误]
        E3[Api<br/>API 响应错误]
        E4[Input<br/>文本输入错误]
        E5[Permission<br/>权限不足]
        E6[Config<br/>配置错误]
        E7[State<br/>状态错误]
        E8[Io<br/>IO 错误]
        E9[Serialization<br/>序列化错误]
    end

    subgraph "错误转换 From trait"
        F1[std::io::Error → Io]
        F2[serde_json::Error → Serialization]
        F3[cpal 错误 → Audio]
        F4[tungstenite::Error → WebSocket]
        F5[arboard::Error → Input]
        F6[tauri::Error → Config]
    end

    F1 --> E8
    F2 --> E9
    F3 --> E1
    F4 --> E2
    F5 --> E4
    F6 --> E6
```

### 13.2 错误处理策略

| 错误类型 | 处理策略 |
|----------|----------|
| `Audio` | 显示错误消息，允许重试 |
| `WebSocket` | 自动重试（当前未实现），显示错误 |
| `Api` | 检查 API Key，显示错误详情 |
| `Input` | 降级到剪贴板模式 |
| `Permission` | 引导用户打开系统设置 |
| `Config` | 使用默认配置，记录警告 |

---

## 14. Tauri 命令接口

### 14.1 命令列表

```mermaid
graph LR
    subgraph "Tauri 命令"
        C1[toggle_recording]
        C2[get_status]
        C3[get_transcript]
        C4[clear_transcript]
        C5[update_settings]
        C6[get_settings]
        C7[load_settings]
        C8[update_hotkey]
        C9[check_accessibility]
        C10[request_accessibility]
    end

    subgraph "返回类型"
        R1[RecordingStatus]
        R2[AppStatus]
        R3[String]
        R4[()]
        R5[AppSettings]
        R6[bool]
    end

    C1 --> R1
    C2 --> R2
    C3 --> R3
    C4 --> R4
    C5 --> R4
    C6 --> R5
    C7 --> R5
    C8 --> R4
    C9 --> R6
    C10 --> R4
```

### 14.2 命令参数与返回值

```typescript
// toggle_recording
interface RecordingStatus {
  is_recording: boolean;
  duration_ms: number | null;
}

// get_status
interface AppStatus {
  recording_state: 'Idle' | 'Recording' | 'Processing';
  connection_status: 'Disconnected' | 'Connecting' | 'Connected' | 'Error';
  transcript: string;
  duration_ms: number | null;
}

// get_settings / update_settings
interface AppSettings {
  api_key: string;
  language_code: string;
  sample_rate: number;
  vad_enabled: boolean;
  vad_silence_threshold: number;
  hotkey: string;
}
```

---

## 15. 安全性设计

### 15.1 权限要求

```mermaid
graph TB
    subgraph "macOS 权限"
        P1[🎤 麦克风权限<br/>NSMicrophoneUsageDescription]
        P2[🌐 网络权限<br/>outgoing connections]
        P3[⌨️ 辅助功能权限<br/>Accessibility]
    end

    subgraph "entitlements.plist"
        E1[com.apple.security.app-sandbox: false]
        E2[com.apple.security.device.audio-input: true]
        E3[com.apple.security.network.client: true]
    end

    subgraph "Info.plist"
        I1[NSMicrophoneUsageDescription]
    end

    P1 --> E2
    P1 --> I1
    P2 --> E3
    P3 --> E1
```

### 15.2 CSP 安全策略

```json
{
  "security": {
    "csp": "default-src 'self'; connect-src 'self' wss://api.elevenlabs.io; style-src 'self' 'unsafe-inline'"
  }
}
```

### 15.3 API Key 存储

| 当前实现 | 建议改进 |
|----------|----------|
| JSON 文件明文存储 | macOS Keychain |
| `~/.config/raflow/settings.json` | 使用 `security-framework` crate |

---

## 16. 性能优化

### 16.1 音频处理延迟

```mermaid
gantt
    title 音频处理延迟分析
    dateFormat X
    axisFormat %L ms

    section 音频捕获
    cpal 回调 :a1, 0, 10

    section 降噪处理
    上采样 48kHz :a2, 10, 15
    RNNoise 处理 :a3, 15, 25
    下采样 16kHz :a4, 25, 30

    section 网络传输
    缓冲 250ms :a5, 30, 280
    WebSocket 发送 :a6, 280, 290
    API 处理 :a7, 290, 440

    section 文本插入
    剪贴板写入 :a8, 440, 445
    按键模拟 :a9, 445, 495
```

### 16.2 内存使用

| 组件 | 缓冲区大小 | 说明 |
|------|------------|------|
| 音频通道 | 500 条消息 | `mpsc::channel` |
| 转录通道 | 100 条消息 | `mpsc::channel` |
| 音频块 | 4000 样本 (~250ms) | 16kHz × 0.25s |
| 降噪缓冲 | 1920 样本 | 48kHz × 4 帧 |

### 16.3 延迟目标

| 阶段 | 目标延迟 |
|------|----------|
| 音频捕获 + 降噪 | < 30ms |
| 缓冲 + 编码 | 250ms |
| API 处理 | ~150ms |
| 文本插入 | < 70ms |
| **总端到端延迟** | **< 500ms** |

---

## 17. 构建与部署

### 17.1 构建流程

```mermaid
flowchart LR
    subgraph "前端构建"
        F1[npm install]
        F2[vite build]
        F3[dist/]
    end

    subgraph "Rust 构建"
        R1[cargo build --release]
        R2[编译 Rust 代码]
        R3[链接 tauri-runtime]
    end

    subgraph "Tauri 打包"
        T1[tauri build]
        T2[嵌入前端资源]
        T3[代码签名]
        T4[DMG/App 打包]
    end

    subgraph "输出产物"
        O1[Raflow.app]
        O2[Raflow_0.1.0_aarch64.dmg]
    end

    F1 --> F2 --> F3
    R1 --> R2 --> R3
    F3 --> T1
    R3 --> T1
    T1 --> T2 --> T3 --> T4
    T4 --> O1
    T4 --> O2
```

### 17.2 构建命令

```bash
# 开发模式
npm run tauri dev

# 生产构建
npm run tauri build

# 输出路径
# src-tauri/target/release/bundle/macos/Raflow.app
# src-tauri/target/release/bundle/dmg/Raflow_0.1.0_aarch64.dmg
```

---

## 18. 未来改进方向

### 18.1 功能增强

| 优先级 | 功能 | 描述 |
|--------|------|------|
| 高 | Windows/Linux 支持 | 跨平台文本插入 |
| 高 | API Key 安全存储 | 使用系统 Keychain |
| 中 | WebSocket 重连 | 网络断开后自动重连 |
| 中 | 多语言切换热键 | 快速切换识别语言 |
| 低 | 本地 Whisper 支持 | 离线语音识别 |
| 低 | 语音命令 | 识别特殊命令如 "删除上一句" |

### 18.2 架构优化

```mermaid
graph TB
    subgraph "当前架构"
        A1[单一 WebSocket 连接]
        A2[JSON 配置文件]
        A3[同步文本插入]
    end

    subgraph "优化方向"
        B1[连接池 + 自动重连]
        B2[系统 Keychain 集成]
        B3[异步插入队列]
        B4[本地模型支持]
    end

    A1 -.-> B1
    A2 -.-> B2
    A3 -.-> B3
```

---

## 附录 A: 支持的语言代码

| 代码 | 语言 |
|------|------|
| `zho` | 中文 |
| `eng` | 英语 |
| `jpn` | 日语 |
| `kor` | 韩语 |
| `spa` | 西班牙语 |
| `fra` | 法语 |
| `deu` | 德语 |
| `ita` | 意大利语 |
| `por` | 葡萄牙语 |
| `rus` | 俄语 |
| `ara` | 阿拉伯语 |
| `hin` | 印地语 |
| `tha` | 泰语 |
| `vie` | 越南语 |
| `ind` | 印尼语 |
| `tur` | 土耳其语 |
| `pol` | 波兰语 |

---

## 附录 B: 快捷键格式

### 支持的修饰键

| 修饰键 | 别名 |
|--------|------|
| `Command` | `Cmd`, `Super`, `Meta` |
| `Control` | `Ctrl` |
| `Shift` | - |
| `Alt` | `Option` |
| `CommandOrControl` | `CmdOrCtrl` |

### 支持的按键

| 类型 | 示例 |
|------|------|
| 字母 | `A`-`Z` |
| 数字 | `0`-`9` |
| 功能键 | `F1`-`F12` |
| 符号 | `\`, `/`, `Space`, `Enter`, `Tab` |
| 方向键 | `Up`, `Down`, `Left`, `Right` |

### 示例

```
CommandOrControl+Shift+\
Cmd+R
Ctrl+Alt+Space
F8
Shift+F12
```

---

**文档结束**
