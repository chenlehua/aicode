# Speech-to-Text 应用详细设计文档

## 1. 概述

### 1.1 项目简介

本项目旨在构建一个类似 [Wispr Flow](https://wisprflow.ai/) 的语音转文字桌面工具，使用 **Tauri 2** 框架和 **ElevenLabs Scribe v2 Realtime API** 实现实时语音转录功能。

### 1.2 核心功能

- 常驻系统托盘（System Tray）
- 全局快捷键 `Cmd+Shift+\` 开启/停止转录
- 实时语音转文字（延迟 ~150ms）
- 智能文本插入到当前活跃应用光标位置
- 剪贴板降级方案

### 1.3 系统架构总览

```mermaid
graph TB
    subgraph "用户交互层"
        A[全局快捷键<br/>Cmd+Shift+\] --> B[状态切换]
        C[系统托盘] --> D[菜单操作]
        E[设置界面] --> F[配置管理]
    end

    subgraph "Tauri 2 应用"
        subgraph "前端 WebView"
            G[状态显示组件]
            H[转录预览组件]
            I[设置面板]
        end

        subgraph "Rust 后端"
            J[音频捕获模块<br/>cpal]
            K[WebSocket 客户端<br/>tokio-tungstenite]
            L[文本插入模块<br/>enigo + arboard]
            M[状态管理器]
        end
    end

    subgraph "外部服务"
        N[ElevenLabs<br/>Scribe v2 Realtime API]
    end

    subgraph "目标应用"
        O[当前活跃窗口<br/>文本输入位置]
    end

    B --> M
    D --> M
    M --> J
    J -->|PCM 音频流| K
    K -->|WebSocket| N
    N -->|转录文本| K
    K --> M
    M --> L
    L -->|模拟输入/剪贴板| O
    M --> G
    M --> H
    F --> M
```

## 2. 技术栈与依赖版本

### 2.1 Rust 依赖 (Cargo.toml)

| 依赖包 | 版本 | 用途 |
|--------|------|------|
| tauri | 2.9.x | 应用框架 |
| tauri-plugin-global-shortcut | 2.3.0 | 全局快捷键 |
| tokio | 1.49.0 | 异步运行时 |
| tokio-tungstenite | 0.28.0 | WebSocket 客户端 |
| cpal | 0.17.1 | 跨平台音频捕获 |
| enigo | 0.6.1 | 键盘/鼠标模拟 |
| arboard | 3.6.1 | 剪贴板操作 |
| serde | 1.0.228 | 序列化框架 |
| serde_json | 1.0.145 | JSON 处理 |
| base64 | 0.22.1 | Base64 编解码 |
| futures-util | 0.3.31 | 异步工具 |

```toml
[package]
name = "speech-to-text"
version = "0.1.0"
edition = "2021"

[dependencies]
tauri = { version = "2.9", features = ["tray-icon"] }
tauri-plugin-global-shortcut = "2.3"
tokio = { version = "1.49", features = ["full"] }
tokio-tungstenite = { version = "0.28", features = ["native-tls"] }
cpal = "0.17"
enigo = "0.6"
arboard = "3.6"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
base64 = "0.22"
futures-util = "0.3"
http = "1.0"
thiserror = "2.0"
log = "0.4"
env_logger = "0.11"

[build-dependencies]
tauri-build = "2.9"
```

### 2.2 前端依赖 (package.json)

| 依赖包 | 版本 | 用途 |
|--------|------|------|
| svelte | ^5.46 | UI 框架 |
| vite | ^7.3 | 构建工具 |
| @tauri-apps/api | ^2.9 | Tauri JS API |
| @tauri-apps/plugin-global-shortcut | ^2.3 | 快捷键插件 |
| typescript | ^5.7 | 类型支持 |

```json
{
  "name": "speech-to-text",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "tauri": "tauri"
  },
  "dependencies": {
    "@tauri-apps/api": "^2.9.1",
    "@tauri-apps/plugin-global-shortcut": "^2.3.0"
  },
  "devDependencies": {
    "@sveltejs/vite-plugin-svelte": "^5.0.0",
    "@tauri-apps/cli": "^2.9.6",
    "svelte": "^5.46.4",
    "typescript": "^5.7.0",
    "vite": "^7.3.1"
  }
}
```

## 3. 系统架构设计

### 3.1 分层架构

```mermaid
graph LR
    subgraph "表现层 Presentation"
        A1[System Tray UI]
        A2[Settings Window]
        A3[Status Overlay]
    end

    subgraph "业务逻辑层 Business Logic"
        B1[TranscriptionService]
        B2[HotkeyManager]
        B3[StateManager]
    end

    subgraph "基础设施层 Infrastructure"
        C1[AudioCaptureAdapter]
        C2[WebSocketClient]
        C3[TextInputAdapter]
        C4[ClipboardAdapter]
        C5[StorageAdapter]
    end

    subgraph "外部系统 External"
        D1[ElevenLabs API]
        D2[操作系统 macOS/Windows/Linux]
    end

    A1 --> B3
    A2 --> B3
    A3 --> B3
    B1 --> C1
    B1 --> C2
    B1 --> C3
    B1 --> C4
    B2 --> B3
    B3 --> B1
    C2 --> D1
    C1 --> D2
    C3 --> D2
    C4 --> D2
```

### 3.2 模块职责划分

```mermaid
classDiagram
    class App {
        +setup()
        +run()
    }

    class StateManager {
        -is_recording: bool
        -transcript_buffer: String
        -settings: AppSettings
        +toggle_recording()
        +get_state()
        +update_settings()
    }

    class TranscriptionService {
        -audio_capture: AudioCapture
        -ws_client: WebSocketClient
        -text_inserter: TextInserter
        +start()
        +stop()
        +on_transcript()
    }

    class AudioCapture {
        -stream: Option~Stream~
        -sample_rate: u32
        +start(callback)
        +stop()
        +is_recording()
    }

    class WebSocketClient {
        -ws: WebSocket
        -api_key: String
        +connect()
        +send_audio(chunk)
        +on_message(callback)
        +disconnect()
    }

    class TextInserter {
        -enigo: Enigo
        -clipboard: Clipboard
        +insert_text(text)
        +copy_to_clipboard(text)
    }

    class TrayManager {
        -tray: TrayIcon
        +create()
        +update_icon(recording)
        +show_notification(msg)
    }

    class HotkeyManager {
        +register(shortcut, callback)
        +unregister(shortcut)
    }

    App --> StateManager
    App --> TrayManager
    App --> HotkeyManager
    StateManager --> TranscriptionService
    TranscriptionService --> AudioCapture
    TranscriptionService --> WebSocketClient
    TranscriptionService --> TextInserter
```

## 4. 核心流程设计

### 4.1 应用启动流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant App as Tauri App
    participant Tray as System Tray
    participant Hotkey as Hotkey Manager
    participant State as State Manager
    participant Storage as Storage

    User->>App: 启动应用
    App->>Storage: 加载配置
    Storage-->>App: AppSettings
    App->>State: 初始化状态
    App->>Tray: 创建托盘图标
    Tray-->>App: TrayIcon
    App->>Hotkey: 注册全局快捷键
    Hotkey-->>App: 注册成功
    App->>App: 隐藏主窗口
    Note over App: 应用进入待命状态
    Tray-->>User: 显示托盘图标
```

### 4.2 录音与转录流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant Hotkey as Hotkey Manager
    participant State as State Manager
    participant Audio as Audio Capture
    participant WS as WebSocket Client
    participant API as ElevenLabs API
    participant Inserter as Text Inserter
    participant Target as 目标应用

    User->>Hotkey: 按下 Cmd+Shift+\
    Hotkey->>State: toggle_recording()

    alt 开始录音
        State->>Audio: start()
        Audio->>Audio: 获取麦克风权限
        Audio-->>State: 录音开始
        State->>WS: connect()
        WS->>API: WebSocket 握手
        API-->>WS: session_started

        loop 录音进行中
            Audio->>Audio: 捕获 PCM 音频
            Audio->>WS: send_audio(chunk)
            WS->>API: input_audio_chunk
            API-->>WS: partial_transcript
            WS->>State: 更新转录文本
            State->>State: 累积文本到 buffer
        end
    else 停止录音
        User->>Hotkey: 再次按下 Cmd+Shift+\
        Hotkey->>State: toggle_recording()
        State->>Audio: stop()
        State->>WS: disconnect()
        State->>Inserter: insert_text(buffer)

        alt 输入成功
            Inserter->>Target: 模拟 Cmd+V 粘贴
            Target-->>User: 文本已插入
        else 输入失败
            Inserter->>Inserter: copy_to_clipboard()
            Inserter-->>User: 已复制到剪贴板
        end
    end
```

### 4.3 WebSocket 通信流程

```mermaid
sequenceDiagram
    participant Client as Rust Client
    participant WS as WebSocket
    participant API as ElevenLabs API

    Client->>WS: 建立连接
    Note over WS: wss://api.elevenlabs.io/v1/speech-to-text/realtime
    WS->>API: WebSocket Upgrade
    Note over WS: Header: xi-api-key
    API-->>WS: 101 Switching Protocols
    API-->>Client: session_started

    Client->>API: session_config
    Note over Client,API: sample_rate: 16000<br/>language_code: "zh"<br/>vad_commit_strategy: true

    loop 音频流传输
        Client->>API: input_audio_chunk
        Note over Client,API: audio_base_64: "..."<br/>commit: false
        API-->>Client: partial_transcript
        Note over API,Client: text: "你好"
    end

    Client->>API: commit
    API-->>Client: committed_transcript
    Note over API,Client: text: "你好，世界"

    Client->>WS: 关闭连接
    WS->>API: Close Frame
```

### 4.4 文本插入决策流程

```mermaid
flowchart TD
    A[获取转录文本] --> B{文本是否为空?}
    B -->|是| C[结束]
    B -->|否| D[保存原剪贴板内容]
    D --> E[将文本写入剪贴板]
    E --> F[短暂延迟 50ms]
    F --> G[模拟 Cmd+V 粘贴]
    G --> H{粘贴是否成功?}
    H -->|是| I[延迟 100ms]
    I --> J[恢复原剪贴板内容]
    J --> K[通知: 文本已插入]
    H -->|否| L[保留文本在剪贴板]
    L --> M[通知: 已复制到剪贴板]
    K --> C
    M --> C
```

## 5. 组件详细设计

### 5.1 状态管理组件

```mermaid
stateDiagram-v2
    [*] --> Idle: 应用启动

    Idle --> Recording: toggle_recording()
    Recording --> Processing: toggle_recording()
    Processing --> Idle: 处理完成

    state Idle {
        [*] --> WaitingForInput
        WaitingForInput --> WaitingForInput: 等待快捷键
    }

    state Recording {
        [*] --> Capturing
        Capturing --> Transcribing: 音频数据到达
        Transcribing --> Capturing: 继续录音
        Transcribing --> BufferUpdated: 收到转录
        BufferUpdated --> Capturing
    }

    state Processing {
        [*] --> StoppingRecording
        StoppingRecording --> InsertingText
        InsertingText --> TextInserted: 成功
        InsertingText --> CopiedToClipboard: 失败
        TextInserted --> [*]
        CopiedToClipboard --> [*]
    }
```

### 5.2 数据结构设计

```mermaid
erDiagram
    AppState {
        bool is_recording
        string transcript_buffer
        string language_code
        datetime recording_start_time
    }

    AppSettings {
        string api_key
        string language_code
        int sample_rate
        bool vad_enabled
        float vad_silence_threshold
        string hotkey
    }

    TranscriptMessage {
        string message_type
        string text
        float timestamp
        bool is_final
    }

    AudioChunk {
        bytes pcm_data
        int sample_rate
        datetime timestamp
    }

    AppState ||--o{ TranscriptMessage : accumulates
    AppSettings ||--|| AppState : configures
    AudioChunk }o--|| TranscriptMessage : produces
```

### 5.3 错误处理设计

```mermaid
flowchart TD
    subgraph "错误类型"
        E1[AudioError<br/>音频设备错误]
        E2[WebSocketError<br/>网络连接错误]
        E3[ApiError<br/>API 响应错误]
        E4[InputError<br/>文本输入错误]
        E5[PermissionError<br/>权限不足]
    end

    subgraph "处理策略"
        H1[重试机制<br/>指数退避]
        H2[降级方案<br/>剪贴板模式]
        H3[用户通知<br/>Toast/通知]
        H4[权限引导<br/>打开设置]
    end

    E1 --> H3
    E2 --> H1
    E2 --> H3
    E3 --> H1
    E3 --> H3
    E4 --> H2
    E5 --> H4
```

## 6. API 接口设计

### 6.1 ElevenLabs WebSocket API 消息格式

#### 发送消息

```typescript
// 会话配置
interface SessionConfig {
  message_type: "session_config";
  sample_rate: 16000;
  language_code: "zh" | "en" | "ja" | string;
  vad_commit_strategy: boolean;
  vad_silence_threshold_secs?: number;
  include_timestamps?: boolean;
}

// 音频块
interface AudioChunkMessage {
  message_type: "input_audio_chunk";
  audio_base_64: string;  // Base64 编码的 PCM 16-bit 音频
  commit: boolean;
  sample_rate: 16000;
}

// 手动提交
interface CommitMessage {
  message_type: "commit";
}
```

#### 接收消息

```typescript
// 会话开始
interface SessionStarted {
  message_type: "session_started";
  session_id: string;
  config: {
    sample_rate: number;
    audio_format: string;
    language_code: string;
    model_id: "scribe_v2_realtime";
    vad_commit_strategy: boolean;
    vad_silence_threshold_secs: number;
    include_timestamps: boolean;
  };
}

// 部分转录
interface PartialTranscript {
  message_type: "partial_transcript";
  text: string;
  timestamp?: number;
}

// 最终转录
interface CommittedTranscript {
  message_type: "committed_transcript";
  text: string;
  timestamp?: number;
}
```

### 6.2 Tauri 命令接口

```rust
// 前后端通信接口

#[tauri::command]
async fn toggle_recording(
    state: State<'_, AppStateHandle>,
    app: AppHandle,
) -> Result<RecordingStatus, AppError>;

#[tauri::command]
async fn get_status(
    state: State<'_, AppStateHandle>,
) -> Result<AppStatus, AppError>;

#[tauri::command]
async fn update_settings(
    state: State<'_, AppStateHandle>,
    settings: AppSettings,
) -> Result<(), AppError>;

#[tauri::command]
async fn get_settings(
    state: State<'_, AppStateHandle>,
) -> Result<AppSettings, AppError>;

// 返回类型
#[derive(Serialize)]
struct RecordingStatus {
    is_recording: bool,
    duration_ms: Option<u64>,
}

#[derive(Serialize)]
struct AppStatus {
    is_recording: bool,
    transcript: String,
    connection_status: ConnectionStatus,
}

#[derive(Serialize)]
enum ConnectionStatus {
    Disconnected,
    Connecting,
    Connected,
    Error(String),
}
```

## 7. 前端界面设计

### 7.1 组件结构

```mermaid
graph TD
    subgraph "App.svelte"
        A[App Root]
    end

    subgraph "Components"
        B[StatusBar.svelte]
        C[TranscriptPreview.svelte]
        D[SettingsPanel.svelte]
        E[HotkeyHint.svelte]
    end

    subgraph "Stores"
        F[appState.ts]
        G[settings.ts]
    end

    A --> B
    A --> C
    A --> D
    A --> E
    B --> F
    C --> F
    D --> G
    F --> G
```

### 7.2 界面布局

```
┌─────────────────────────────────────┐
│  Speech to Text                   ─ │
├─────────────────────────────────────┤
│                                     │
│   ┌─────────────────────────────┐   │
│   │  ● Recording...             │   │
│   │     00:05                   │   │
│   └─────────────────────────────┘   │
│                                     │
│   ┌─────────────────────────────┐   │
│   │                             │   │
│   │  "你好，这是一段测试..."   │   │
│   │                             │   │
│   └─────────────────────────────┘   │
│                                     │
│        ⌘ + ⇧ + \ to toggle         │
│                                     │
├─────────────────────────────────────┤
│  ⚙️ Settings                        │
└─────────────────────────────────────┘
```

### 7.3 系统托盘菜单

```
┌─────────────────────────┐
│ ● Start Recording       │
│ ─────────────────────── │
│   Settings...           │
│   About                 │
│ ─────────────────────── │
│   Quit                  │
└─────────────────────────┘
```

## 8. 项目目录结构

```
speech-to-text/
├── src-tauri/
│   ├── Cargo.toml
│   ├── build.rs
│   ├── tauri.conf.json
│   ├── capabilities/
│   │   └── main.json
│   ├── icons/
│   │   ├── icon.icns
│   │   ├── icon.ico
│   │   ├── icon.png
│   │   ├── tray-idle.png
│   │   └── tray-recording.png
│   └── src/
│       ├── main.rs              # 入口点
│       ├── lib.rs               # 库导出
│       ├── error.rs             # 错误定义
│       ├── state.rs             # 状态管理
│       ├── commands.rs          # Tauri 命令
│       ├── tray.rs              # 系统托盘
│       ├── hotkey.rs            # 快捷键处理
│       ├── audio/
│       │   ├── mod.rs
│       │   └── capture.rs       # 音频捕获
│       ├── transcriber/
│       │   ├── mod.rs
│       │   ├── client.rs        # WebSocket 客户端
│       │   └── message.rs       # 消息类型
│       └── input/
│           ├── mod.rs
│           ├── inserter.rs      # 文本插入
│           └── clipboard.rs     # 剪贴板操作
│
├── src/
│   ├── main.ts                  # 前端入口
│   ├── App.svelte               # 根组件
│   ├── app.css                  # 全局样式
│   ├── lib/
│   │   ├── stores/
│   │   │   ├── appState.ts      # 应用状态
│   │   │   └── settings.ts      # 设置状态
│   │   ├── components/
│   │   │   ├── StatusBar.svelte
│   │   │   ├── TranscriptPreview.svelte
│   │   │   ├── SettingsPanel.svelte
│   │   │   └── HotkeyHint.svelte
│   │   └── utils/
│   │       └── tauri.ts         # Tauri 工具函数
│   └── vite-env.d.ts
│
├── public/
│   └── favicon.ico
├── index.html
├── package.json
├── tsconfig.json
├── svelte.config.js
└── vite.config.ts
```

## 9. 配置文件设计

### 9.1 Tauri 配置 (tauri.conf.json)

```json
{
  "$schema": "https://schema.tauri.app/config/2",
  "productName": "Speech to Text",
  "identifier": "com.example.speech-to-text",
  "version": "0.1.0",
  "build": {
    "frontendDist": "../dist",
    "devUrl": "http://localhost:5173",
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build"
  },
  "app": {
    "withGlobalTauri": true,
    "trayIcon": {
      "iconPath": "icons/tray-idle.png",
      "iconAsTemplate": true,
      "menuOnLeftClick": false
    },
    "windows": [
      {
        "label": "main",
        "title": "Speech to Text",
        "width": 400,
        "height": 350,
        "minWidth": 350,
        "minHeight": 300,
        "visible": false,
        "center": true,
        "resizable": true,
        "decorations": true,
        "alwaysOnTop": false,
        "skipTaskbar": true
      }
    ],
    "security": {
      "csp": "default-src 'self'; connect-src 'self' wss://api.elevenlabs.io",
      "capabilities": ["main-capability"]
    }
  },
  "bundle": {
    "active": true,
    "targets": ["dmg", "app"],
    "icon": [
      "icons/icon.icns",
      "icons/icon.ico",
      "icons/icon.png"
    ],
    "macOS": {
      "entitlements": "./entitlements.plist",
      "signingIdentity": null,
      "providerShortName": null
    }
  },
  "plugins": {
    "global-shortcut": {}
  }
}
```

### 9.2 macOS 权限配置 (entitlements.plist)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.app-sandbox</key>
    <false/>
    <key>com.apple.security.device.audio-input</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <true/>
</dict>
</plist>
```

### 9.3 Info.plist 补充

```xml
<key>NSMicrophoneUsageDescription</key>
<string>此应用需要麦克风权限以进行语音转文字。</string>
```

## 10. 安全性设计

### 10.1 API Key 存储

```mermaid
flowchart TD
    A[用户输入 API Key] --> B{平台检测}
    B -->|macOS| C[Keychain Access]
    B -->|Windows| D[Credential Manager]
    B -->|Linux| E[Secret Service API]
    C --> F[加密存储]
    D --> F
    E --> F
    F --> G[运行时读取]
    G --> H[内存中使用]
    H --> I[进程退出时清理]
```

### 10.2 安全考虑

| 风险 | 缓解措施 |
|------|----------|
| API Key 泄露 | 使用系统 Keychain 存储，不存储在配置文件 |
| 网络中间人攻击 | 强制使用 TLS 1.3，验证 SSL 证书 |
| 音频数据隐私 | 音频仅在内存中处理，不持久化存储 |
| 权限滥用 | 最小权限原则，仅请求必要的系统权限 |

## 11. 性能优化

### 11.1 音频处理优化

```mermaid
flowchart LR
    A[麦克风] -->|原始音频| B[cpal 捕获]
    B -->|Float32| C[重采样器]
    C -->|16kHz| D[PCM 转换]
    D -->|Int16| E[缓冲区]
    E -->|~256ms| F[Base64 编码]
    F --> G[WebSocket 发送]

    subgraph "优化点"
        H[零拷贝传输]
        I[环形缓冲区]
        J[批量编码]
    end
```

### 11.2 内存管理

- 使用环形缓冲区避免频繁内存分配
- 音频数据使用零拷贝传输
- 转录文本使用 `String` 池化

### 11.3 延迟优化目标

| 阶段 | 目标延迟 |
|------|----------|
| 音频捕获 | < 20ms |
| 编码传输 | < 30ms |
| API 处理 | ~150ms |
| 文本插入 | < 50ms |
| **总延迟** | **< 250ms** |

## 12. 测试策略

### 12.1 测试类型

```mermaid
pie title 测试覆盖分布
    "单元测试" : 40
    "集成测试" : 30
    "端到端测试" : 20
    "手动测试" : 10
```

### 12.2 关键测试场景

| 场景 | 测试内容 |
|------|----------|
| 正常录音 | 快捷键触发、音频捕获、转录返回、文本插入 |
| 网络中断 | WebSocket 断开重连、离线提示 |
| 权限拒绝 | 麦克风权限被拒后的处理 |
| 目标应用不可用 | 剪贴板降级方案 |
| 长时间录音 | 内存使用、转录累积 |
| 多语言切换 | 中/英/日等语言转录准确性 |

## 13. 部署与发布

### 13.1 构建流程

```mermaid
flowchart LR
    A[源代码] --> B[npm run build]
    B --> C[前端构建]
    C --> D[cargo build --release]
    D --> E[Tauri 打包]
    E --> F{平台}
    F -->|macOS| G[.dmg / .app]
    F -->|Windows| H[.msi / .exe]
    F -->|Linux| I[.deb / .AppImage]
```

### 13.2 发布清单

- [ ] 版本号更新
- [ ] CHANGELOG 更新
- [ ] 代码签名（macOS: Developer ID, Windows: Authenticode）
- [ ] 公证（macOS Notarization）
- [ ] 自动更新配置
- [ ] 发布说明

## 14. 参考资料

### 官方文档

- [Tauri 2.0 Documentation](https://v2.tauri.app/)
- [ElevenLabs Scribe v2 Realtime API](https://elevenlabs.io/docs/api-reference/speech-to-text/v-1-speech-to-text-realtime)
- [Svelte 5 Documentation](https://svelte.dev/docs)
- [cpal - Rust Audio I/O](https://docs.rs/cpal/latest/cpal/)
- [enigo - Input Simulation](https://docs.rs/enigo/latest/enigo/)

### 相关项目

- [Wispr Flow](https://wisprflow.ai/) - 参考竞品
- [tauri-plugin-global-shortcut](https://github.com/tauri-apps/plugins-workspace/tree/v2/plugins/global-shortcut)
- [tauri-plugin-mic-recorder](https://github.com/ayangweb/tauri-plugin-mic-recorder)

---

**文档版本**: 1.0.0
**最后更新**: 2026-01-18
**作者**: AI Assistant
