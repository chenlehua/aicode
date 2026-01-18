# Raflow

Raflow 是一款类似 Wispr Flow 的语音转文字桌面应用，基于 Tauri 2 + Svelte 5 + Rust 构建，使用 ElevenLabs Scribe v2 实时 API 进行语音识别。

## 功能特性

- **实时语音转文字** - 基于 ElevenLabs Scribe v2 Realtime API
- **全局快捷键** - 可配置的快捷键切换录音 (默认 ⌘+⇧+\)
- **系统托盘** - 后台运行，托盘图标快速访问
- **智能文本插入** - 自动在光标位置插入转录文本，或复制到剪贴板
- **多语言支持** - 支持中文、英语、日语、韩语等17种语言
- **VAD 语音活动检测** - 自动检测语音段落
- **设置持久化** - 配置自动保存和加载

## 系统要求

- **macOS** 10.15+ (Catalina 或更高版本)
- **Rust** 1.85+ (需要 Rust 2024 edition)
- **Node.js** 18+
- **ElevenLabs API Key** - 从 [elevenlabs.io](https://elevenlabs.io) 获取

## 快速开始

### 1. 安装依赖

```bash
# 安装 Rust (如果尚未安装)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 安装 Node.js 依赖
npm install
```

### 2. 配置环境

首次运行应用后，在设置面板中配置：
- ElevenLabs API Key
- 识别语言
- 全局快捷键

或者手动创建配置文件 `~/.config/raflow/settings.json`:

```json
{
  "api_key": "your-elevenlabs-api-key",
  "language_code": "zh",
  "sample_rate": 16000,
  "vad_enabled": true,
  "vad_silence_threshold": 1.5,
  "hotkey": "CommandOrControl+Shift+\\"
}
```

### 3. 开发模式运行

```bash
npm run tauri dev
```



### 4. 构建生产版本

```bash
npm run tauri build
```

构建产物位于:
- `src-tauri/target/release/bundle/macos/Raflow.app`
- `src-tauri/target/release/bundle/dmg/Raflow_0.1.0_aarch64.dmg`

## 开发指南

### 项目结构

```
raflow/
├── src/                          # Svelte 前端代码
│   ├── App.svelte               # 主应用组件
│   ├── main.ts                  # 入口文件
│   └── lib/
│       ├── components/          # UI 组件
│       │   ├── StatusBar.svelte
│       │   ├── TranscriptPreview.svelte
│       │   ├── SettingsPanel.svelte
│       │   └── HotkeyHint.svelte
│       ├── stores/              # Svelte stores
│       │   ├── appState.ts
│       │   └── settings.ts
│       └── utils/
│           └── tauri.ts
├── src-tauri/                   # Rust 后端代码
│   ├── src/
│   │   ├── main.rs             # 应用入口
│   │   ├── lib.rs              # 库导出
│   │   ├── commands.rs         # Tauri 命令
│   │   ├── state.rs            # 应用状态管理
│   │   ├── error.rs            # 错误处理
│   │   ├── hotkey.rs           # 全局快捷键
│   │   ├── tray.rs             # 系统托盘
│   │   ├── settings_store.rs   # 设置持久化
│   │   ├── audio/              # 音频捕获
│   │   │   ├── mod.rs
│   │   │   └── capture.rs
│   │   ├── transcriber/        # 转录客户端
│   │   │   ├── mod.rs
│   │   │   ├── client.rs
│   │   │   └── message.rs
│   │   └── input/              # 文本插入
│   │       ├── mod.rs
│   │       ├── clipboard.rs
│   │       └── inserter.rs
│   ├── Cargo.toml
│   ├── tauri.conf.json
│   └── capabilities/
│       └── main.json
├── package.json
├── vite.config.ts
└── tsconfig.json
```

### 常用命令

```bash
# 开发模式
npm run tauri dev

# 构建生产版本
npm run tauri build

# 仅运行前端开发服务器
npm run dev

# 前端类型检查
npm run check

# Rust 代码检查
cd src-tauri && cargo check

# 运行 Rust 测试
cd src-tauri && cargo test

# 格式化 Rust 代码
cd src-tauri && cargo fmt

# Rust 代码静态分析
cd src-tauri && cargo clippy
```

### 调试

#### 前端调试

1. 开发模式下，应用窗口支持开发者工具
2. 使用 `console.log()` 输出调试信息
3. 在 `npm run tauri dev` 模式下，前端代码支持热重载

#### 后端调试

1. 设置日志级别:
   ```bash
   RUST_LOG=debug npm run tauri dev
   ```

2. 日志级别选项:
   - `error` - 仅错误
   - `warn` - 警告和错误
   - `info` - 一般信息 (默认)
   - `debug` - 调试信息
   - `trace` - 详细跟踪

3. 在 Rust 代码中使用日志:
   ```rust
   log::info!("Recording started");
   log::debug!("Audio chunk size: {}", chunk.len());
   log::error!("Failed to connect: {}", e);
   ```

#### VS Code 调试配置

创建 `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "lldb",
      "request": "launch",
      "name": "Debug Tauri",
      "cargo": {
        "args": ["build", "--manifest-path=./src-tauri/Cargo.toml"]
      },
      "args": [],
      "cwd": "${workspaceFolder}"
    }
  ]
}
```

### 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 框架 | Tauri | 2.x |
| 前端 | Svelte | 5.x |
| 后端 | Rust | 2024 edition |
| 音频 | cpal | 0.15 |
| WebSocket | tokio-tungstenite | 0.28 |
| 剪贴板 | arboard | 3.6 |
| 键盘模拟 | enigo | 0.2 |
| 状态管理 | arc-swap | 1.7 |

### Rust 编码规范

根据 `CLAUDE.md` 中的规范:

- 使用 Rust 2024 edition
- 优先使用 `mpsc` channel 而非 shared memory
- 对于配置等很少改动的数据，使用 `ArcSwap` 而非 `Mutex`
- 如需并发 HashMap，使用 `DashMap`
- 不使用 `unsafe` 代码
- 不使用 `unwrap()` 或 `expect()`，正确处理错误

## 使用说明

### 基本操作

1. **启动应用** - 应用会在系统托盘显示图标
2. **开始录音** - 按下全局快捷键 (默认 ⌘+⇧+\) 或点击托盘菜单
3. **停止录音** - 再次按下快捷键，转录文本将自动插入到当前光标位置
4. **打开设置** - 点击托盘菜单中的 "Settings..."

### 设置选项

| 选项 | 说明 |
|------|------|
| ElevenLabs API Key | 用于语音识别的 API 密钥 |
| Language | 识别语言 |
| Global Hotkey | 切换录音的快捷键 |
| VAD | 语音活动检测开关 |
| VAD Silence Threshold | 静音检测阈值 (秒) |

### 支持的快捷键格式

- `CommandOrControl+Shift+\` - 推荐，跨平台兼容
- `Cmd+Shift+R` - macOS 专用
- `Ctrl+Alt+Space` - 自定义组合
- `F8`, `F9`, `F10` - 功能键

## 故障排除

### 常见问题

**Q: 快捷键不工作？**
- 检查是否有其他应用占用了相同的快捷键
- 尝试在设置中更换其他快捷键
- 确保应用已获得辅助功能权限

**Q: 没有声音输入？**
- 检查系统麦克风权限设置
- 确保选择了正确的输入设备

**Q: API 连接失败？**
- 验证 API Key 是否正确
- 检查网络连接
- 查看应用日志获取详细错误信息

### 权限设置 (macOS)

应用需要以下权限:
- **麦克风** - 系统偏好设置 > 安全性与隐私 > 隐私 > 麦克风
- **辅助功能** - 系统偏好设置 > 安全性与隐私 > 隐私 > 辅助功能

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request。
