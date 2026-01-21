# GenSlides 技术设计规格文档

## 1. 概述

本文档基于 [PRD](./0001-prd.md) 定义 GenSlides 的技术实现细节，包括项目结构、后端架构、前端架构、API 接口规格等。

## 2. 项目目录结构

```
genslides/
├── backend/                          # 后端 Python 代码
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI 应用入口
│   │   ├── config.py                 # 配置管理
│   │   │
│   │   ├── api/                      # API 层 - 路由和请求处理
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── slides.py         # Slides CRUD 路由
│   │   │   │   ├── style.py          # 风格相关路由
│   │   │   │   ├── images.py         # 图片相关路由
│   │   │   │   └── websocket.py      # WebSocket 路由
│   │   │   ├── schemas/              # Pydantic 请求/响应模型
│   │   │   │   ├── __init__.py
│   │   │   │   ├── slides.py
│   │   │   │   ├── style.py
│   │   │   │   └── images.py
│   │   │   └── dependencies.py       # 依赖注入
│   │   │
│   │   ├── services/                 # 业务层 - 核心业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── slides_service.py     # Slides 业务逻辑
│   │   │   ├── style_service.py      # 风格业务逻辑
│   │   │   ├── image_service.py      # 图片生成业务逻辑
│   │   │   ├── gemini_service.py     # Gemini API 封装
│   │   │   └── cost_service.py       # 成本计算服务
│   │   │
│   │   ├── repositories/             # 存储层 - 数据访问
│   │   │   ├── __init__.py
│   │   │   ├── slides_repository.py  # Slides 数据存取
│   │   │   ├── style_repository.py   # 风格数据存取
│   │   │   └── image_repository.py   # 图片文件存取
│   │   │
│   │   ├── models/                   # 领域模型
│   │   │   ├── __init__.py
│   │   │   ├── slide.py
│   │   │   ├── style.py
│   │   │   └── project.py
│   │   │
│   │   └── utils/                    # 工具函数
│   │       ├── __init__.py
│   │       ├── hash.py               # Blake3 哈希工具
│   │       └── file.py               # 文件操作工具
│   │
│   ├── tests/                        # 后端测试
│   │   ├── __init__.py
│   │   ├── test_slides.py
│   │   ├── test_style.py
│   │   └── test_images.py
│   │
│   ├── requirements.txt              # Python 依赖
│   └── pyproject.toml
│
├── frontend/                         # 前端 TypeScript 代码
│   ├── src/
│   │   ├── main.tsx                  # 应用入口
│   │   ├── App.tsx                   # 根组件
│   │   │
│   │   ├── components/               # UI 组件
│   │   │   ├── Header/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── TitleInput.tsx
│   │   │   │   ├── StyleBadge.tsx
│   │   │   │   ├── CostDisplay.tsx
│   │   │   │   └── PlayButton.tsx
│   │   │   ├── Sidebar/
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── SlideItem.tsx
│   │   │   │   └── SlideList.tsx
│   │   │   ├── Preview/
│   │   │   │   ├── Preview.tsx
│   │   │   │   ├── MainImage.tsx
│   │   │   │   ├── GenerateButton.tsx
│   │   │   │   └── ThumbnailList.tsx
│   │   │   ├── Player/
│   │   │   │   └── FullscreenPlayer.tsx
│   │   │   ├── Modals/
│   │   │   │   ├── StyleSetupModal.tsx
│   │   │   │   └── StyleSettingsModal.tsx
│   │   │   └── common/
│   │   │       ├── Button.tsx
│   │   │       ├── Input.tsx
│   │   │       ├── Modal.tsx
│   │   │       └── Loading.tsx
│   │   │
│   │   ├── stores/                   # Zustand 状态管理
│   │   │   ├── index.ts
│   │   │   ├── slidesStore.ts
│   │   │   ├── styleStore.ts
│   │   │   ├── uiStore.ts
│   │   │   └── playerStore.ts
│   │   │
│   │   ├── api/                      # API 客户端
│   │   │   ├── index.ts
│   │   │   ├── client.ts             # Axios/Fetch 配置
│   │   │   ├── slides.ts
│   │   │   ├── style.ts
│   │   │   ├── images.ts
│   │   │   └── websocket.ts
│   │   │
│   │   ├── hooks/                    # 自定义 Hooks
│   │   │   ├── useSlides.ts
│   │   │   ├── useStyle.ts
│   │   │   ├── useWebSocket.ts
│   │   │   └── useKeyboard.ts
│   │   │
│   │   ├── types/                    # TypeScript 类型定义
│   │   │   ├── index.ts
│   │   │   ├── slides.ts
│   │   │   ├── style.ts
│   │   │   └── api.ts
│   │   │
│   │   └── utils/                    # 工具函数
│   │       ├── index.ts
│   │       └── format.ts
│   │
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── vite.config.ts
│
├── slides/                           # 数据存储目录
│   └── <slug>/
│       ├── outline.yml
│       ├── style/
│       │   └── style.jpg
│       └── images/
│           └── <sid>/
│               └── <blake3hash>.jpg
│
├── .env                              # 环境变量
├── .env.example
├── docker-compose.yml                # Docker 配置（可选）
└── README.md
```

## 3. 后端架构设计

### 3.1 分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                        API 层 (api/)                        │
│  - 路由定义 (routes/)                                        │
│  - 请求/响应模型 (schemas/)                                   │
│  - 参数验证、错误处理                                          │
├─────────────────────────────────────────────────────────────┤
│                      业务层 (services/)                      │
│  - 核心业务逻辑                                               │
│  - Gemini API 调用                                          │
│  - 成本计算                                                  │
├─────────────────────────────────────────────────────────────┤
│                     存储层 (repositories/)                   │
│  - YAML 文件读写                                             │
│  - 图片文件管理                                               │
│  - 目录结构管理                                               │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 领域模型

```python
# models/slide.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Slide:
    sid: str
    content: str
    created_at: datetime
    updated_at: datetime

@dataclass
class SlideImage:
    sid: str
    hash: str              # blake3 hash
    path: str              # 相对路径
    created_at: datetime

# models/style.py
@dataclass
class Style:
    prompt: str
    image: str             # 相对路径
    created_at: datetime

# models/project.py
@dataclass
class Project:
    slug: str
    title: str
    style: Optional[Style]
    slides: List[Slide]
    created_at: datetime
    updated_at: datetime
```

## 4. API 接口规格

### 4.1 基础信息

- **Base URL**: `http://localhost:3003/api`
- **Content-Type**: `application/json`
- **图片资源**: `http://localhost:3003/static/slides/{slug}/...`

### 4.2 Slides 接口

#### 4.2.1 获取项目信息

```
GET /api/slides/{slug}
```

**响应**:
```json
{
  "slug": "hello-world",
  "title": "演示标题",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T14:20:00Z",
  "style": {
    "prompt": "简约商务风格，蓝色调，现代感",
    "image": "/static/slides/hello-world/style/style.jpg",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "slides": [
    {
      "sid": "slide-001",
      "content": "第一张幻灯片的文字内容",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "current_image": {
        "hash": "abc123",
        "url": "/static/slides/hello-world/images/slide-001/abc123.jpg",
        "matched": true
      }
    }
  ],
  "cost": {
    "total_images": 5,
    "estimated_cost": 0.12
  }
}
```

**状态码**:
- `200`: 成功
- `404`: 项目不存在（首次访问时自动创建空项目）

#### 4.2.2 更新项目标题

```
PUT /api/slides/{slug}/title
```

**请求**:
```json
{
  "title": "新标题"
}
```

**响应**:
```json
{
  "slug": "hello-world",
  "title": "新标题",
  "updated_at": "2024-01-15T14:30:00Z"
}
```

#### 4.2.3 创建新 Slide

```
POST /api/slides/{slug}
```

**请求**:
```json
{
  "content": "新幻灯片的文字内容",
  "after_sid": "slide-001"  // 可选，在指定 slide 后插入；为空则添加到末尾
}
```

**响应**:
```json
{
  "sid": "slide-002",
  "content": "新幻灯片的文字内容",
  "created_at": "2024-01-15T14:35:00Z",
  "updated_at": "2024-01-15T14:35:00Z",
  "current_image": null
}
```

#### 4.2.4 更新 Slide 内容

```
PUT /api/slides/{slug}/{sid}
```

**请求**:
```json
{
  "content": "更新后的文字内容"
}
```

**响应**:
```json
{
  "sid": "slide-001",
  "content": "更新后的文字内容",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T14:40:00Z",
  "current_image": {
    "hash": "def456",
    "url": "/static/slides/hello-world/images/slide-001/def456.jpg",
    "matched": false  // 内容已变更，hash 不匹配
  }
}
```

#### 4.2.5 更新 Slides 顺序

```
PUT /api/slides/{slug}/reorder
```

**请求**:
```json
{
  "order": ["slide-003", "slide-001", "slide-002"]
}
```

**响应**:
```json
{
  "success": true,
  "slides": [
    { "sid": "slide-003", "content": "..." },
    { "sid": "slide-001", "content": "..." },
    { "sid": "slide-002", "content": "..." }
  ]
}
```

#### 4.2.6 删除 Slide

```
DELETE /api/slides/{slug}/{sid}
```

**响应**:
```json
{
  "success": true,
  "deleted_sid": "slide-001"
}
```

### 4.3 图片接口

#### 4.3.1 获取 Slide 的所有图片

```
GET /api/slides/{slug}/{sid}/images
```

**响应**:
```json
{
  "sid": "slide-001",
  "content_hash": "abc123",  // 当前内容的 blake3 hash
  "images": [
    {
      "hash": "abc123",
      "url": "/static/slides/hello-world/images/slide-001/abc123.jpg",
      "thumbnail_url": "/static/slides/hello-world/images/slide-001/abc123_thumb.jpg",
      "created_at": "2024-01-15T10:35:00Z",
      "matched": true  // hash 与当前内容匹配
    },
    {
      "hash": "xyz789",
      "url": "/static/slides/hello-world/images/slide-001/xyz789.jpg",
      "thumbnail_url": "/static/slides/hello-world/images/slide-001/xyz789_thumb.jpg",
      "created_at": "2024-01-15T10:32:00Z",
      "matched": false
    }
  ],
  "has_matched_image": true
}
```

#### 4.3.2 生成图片

```
POST /api/slides/{slug}/{sid}/generate
```

**请求**:
```json
{
  "force": false  // 可选，true 时强制重新生成（即使已有匹配图片）
}
```

**响应**:
```json
{
  "task_id": "task-uuid-123",
  "status": "pending",
  "message": "图片生成任务已提交"
}
```

**说明**: 图片生成是异步的，完成后通过 WebSocket 通知。

### 4.4 风格接口

#### 4.4.1 获取当前风格

```
GET /api/slides/{slug}/style
```

**响应**:
```json
{
  "has_style": true,
  "style": {
    "prompt": "简约商务风格，蓝色调，现代感",
    "image": "/static/slides/hello-world/style/style.jpg",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

或（未设置风格时）:
```json
{
  "has_style": false,
  "style": null
}
```

#### 4.4.2 生成候选风格图片

```
POST /api/slides/{slug}/style/generate
```

**请求**:
```json
{
  "prompt": "简约商务风格，蓝色调，现代感"
}
```

**响应**:
```json
{
  "candidates": [
    {
      "id": "candidate-1",
      "url": "/static/slides/hello-world/style/candidates/candidate-1.jpg"
    },
    {
      "id": "candidate-2",
      "url": "/static/slides/hello-world/style/candidates/candidate-2.jpg"
    }
  ],
  "prompt": "简约商务风格，蓝色调，现代感"
}
```

#### 4.4.3 保存选择的风格

```
PUT /api/slides/{slug}/style
```

**请求**:
```json
{
  "prompt": "简约商务风格，蓝色调，现代感",
  "candidate_id": "candidate-1"
}
```

**响应**:
```json
{
  "success": true,
  "style": {
    "prompt": "简约商务风格，蓝色调，现代感",
    "image": "/static/slides/hello-world/style/style.jpg",
    "created_at": "2024-01-15T14:50:00Z"
  }
}
```

### 4.5 成本接口

#### 4.5.1 获取成本统计

```
GET /api/slides/{slug}/cost
```

**响应**:
```json
{
  "total_images": 12,
  "style_generations": 2,
  "slide_generations": 10,
  "estimated_cost": 0.24,
  "currency": "USD",
  "breakdown": {
    "style_cost": 0.04,
    "slides_cost": 0.20
  }
}
```

### 4.6 WebSocket 接口

#### 4.6.1 连接

```
WebSocket /ws/slides/{slug}
```

#### 4.6.2 消息类型

**服务端 → 客户端**:

```typescript
// 图片生成开始
{
  "type": "generation_started",
  "data": {
    "task_id": "task-uuid-123",
    "sid": "slide-001"
  }
}

// 图片生成完成
{
  "type": "generation_completed",
  "data": {
    "task_id": "task-uuid-123",
    "sid": "slide-001",
    "image": {
      "hash": "abc123",
      "url": "/static/slides/hello-world/images/slide-001/abc123.jpg",
      "thumbnail_url": "/static/slides/hello-world/images/slide-001/abc123_thumb.jpg"
    }
  }
}

// 图片生成失败
{
  "type": "generation_failed",
  "data": {
    "task_id": "task-uuid-123",
    "sid": "slide-001",
    "error": "API 调用失败"
  }
}

// 风格生成完成
{
  "type": "style_generation_completed",
  "data": {
    "candidates": [...]
  }
}

// 成本更新
{
  "type": "cost_updated",
  "data": {
    "total_images": 13,
    "estimated_cost": 0.26
  }
}
```

**客户端 → 服务端**:

```typescript
// 心跳
{
  "type": "ping"
}
```

## 5. 前端类型定义

```typescript
// types/slides.ts

export interface Slide {
  sid: string;
  content: string;
  created_at: string;
  updated_at: string;
  current_image: SlideImage | null;
}

export interface SlideImage {
  hash: string;
  url: string;
  thumbnail_url?: string;
  created_at: string;
  matched: boolean;
}

export interface Style {
  prompt: string;
  image: string;
  created_at: string;
}

export interface Project {
  slug: string;
  title: string;
  created_at: string;
  updated_at: string;
  style: Style | null;
  slides: Slide[];
  cost: CostInfo;
}

export interface CostInfo {
  total_images: number;
  estimated_cost: number;
  currency: string;
}

export interface StyleCandidate {
  id: string;
  url: string;
}

// types/api.ts

export interface ApiResponse<T> {
  data: T;
  error?: string;
}

export interface GenerateTaskResponse {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  message: string;
}

// WebSocket 消息类型
export type WSMessageType =
  | 'generation_started'
  | 'generation_completed'
  | 'generation_failed'
  | 'style_generation_completed'
  | 'cost_updated';

export interface WSMessage<T = unknown> {
  type: WSMessageType;
  data: T;
}
```

## 6. 前端状态管理

### 6.1 Slides Store

```typescript
// stores/slidesStore.ts
import { create } from 'zustand';

interface SlidesState {
  slug: string | null;
  title: string;
  slides: Slide[];
  selectedSid: string | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  setSlug: (slug: string) => void;
  setTitle: (title: string) => void;
  setSlides: (slides: Slide[]) => void;
  selectSlide: (sid: string) => void;
  addSlide: (slide: Slide, afterSid?: string) => void;
  updateSlide: (sid: string, content: string) => void;
  deleteSlide: (sid: string) => void;
  reorderSlides: (order: string[]) => void;
  updateSlideImage: (sid: string, image: SlideImage) => void;
}
```

### 6.2 Style Store

```typescript
// stores/styleStore.ts
interface StyleState {
  style: Style | null;
  candidates: StyleCandidate[];
  isGenerating: boolean;
  showSetupModal: boolean;
  showSettingsModal: boolean;

  // Actions
  setStyle: (style: Style) => void;
  setCandidates: (candidates: StyleCandidate[]) => void;
  setGenerating: (isGenerating: boolean) => void;
  openSetupModal: () => void;
  closeSetupModal: () => void;
  openSettingsModal: () => void;
  closeSettingsModal: () => void;
}
```

### 6.3 Player Store

```typescript
// stores/playerStore.ts
interface PlayerState {
  isPlaying: boolean;
  currentIndex: number;
  isFullscreen: boolean;

  // Actions
  play: (startIndex?: number) => void;
  pause: () => void;
  next: () => void;
  prev: () => void;
  goTo: (index: number) => void;
  enterFullscreen: () => void;
  exitFullscreen: () => void;
}
```

## 7. 关键流程

### 7.1 首次打开项目流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ 用户访问 URL │────▶│ 获取项目信息 │────▶│ 检查风格设置 │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌──────────────────────────┴──────────────────────────┐
                    │                                                      │
                    ▼                                                      ▼
           ┌───────────────┐                                    ┌───────────────┐
           │  有风格设置    │                                    │  无风格设置    │
           └───────┬───────┘                                    └───────┬───────┘
                   │                                                    │
                   ▼                                                    ▼
           ┌───────────────┐                                    ┌───────────────┐
           │  显示主界面    │                                    │ 弹出风格设置   │
           └───────────────┘                                    └───────┬───────┘
                                                                       │
                                                                       ▼
                                                               ┌───────────────┐
                                                               │ 用户输入 prompt│
                                                               └───────┬───────┘
                                                                       │
                                                                       ▼
                                                               ┌───────────────┐
                                                               │ 生成2张候选图  │
                                                               └───────┬───────┘
                                                                       │
                                                                       ▼
                                                               ┌───────────────┐
                                                               │ 用户选择风格   │
                                                               └───────┬───────┘
                                                                       │
                                                                       ▼
                                                               ┌───────────────┐
                                                               │ 保存并显示主界面│
                                                               └───────────────┘
```

### 7.2 图片生成流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ 用户点击生成 │────▶│ 发送生成请求 │────▶│ 返回 task_id │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │ 显示加载状态 │
                                        └──────┬──────┘
                                               │
                                        ┌──────┴──────┐
                                        │  WebSocket  │
                                        │  等待通知    │
                                        └──────┬──────┘
                                               │
                    ┌──────────────────────────┴──────────────────────────┐
                    │                                                      │
                    ▼                                                      ▼
           ┌───────────────┐                                    ┌───────────────┐
           │ 生成成功通知   │                                    │ 生成失败通知   │
           └───────┬───────┘                                    └───────┬───────┘
                   │                                                    │
                   ▼                                                    ▼
           ┌───────────────┐                                    ┌───────────────┐
           │ 更新图片展示   │                                    │ 显示错误信息   │
           │ 更新成本统计   │                                    └───────────────┘
           └───────────────┘
```

## 8. 后端服务实现要点

### 8.1 Gemini Service

```python
# services/gemini_service.py
from google import genai
from typing import List
import base64

class GeminiService:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    async def generate_style_images(
        self,
        prompt: str,
        count: int = 2
    ) -> List[bytes]:
        """根据 prompt 生成风格候选图片"""
        pass

    async def generate_slide_image(
        self,
        content: str,
        style_image: bytes,
        style_prompt: str
    ) -> bytes:
        """根据内容和风格参考生成 slide 图片"""
        pass
```

### 8.2 Blake3 Hash 工具

```python
# utils/hash.py
import blake3

def compute_content_hash(content: str) -> str:
    """计算内容的 blake3 hash"""
    return blake3.blake3(content.encode('utf-8')).hexdigest()[:16]
```

### 8.3 Slides Repository

```python
# repositories/slides_repository.py
import yaml
from pathlib import Path
from typing import Optional
from models.project import Project

class SlidesRepository:
    def __init__(self, base_path: str = "./slides"):
        self.base_path = Path(base_path)

    def get_project(self, slug: str) -> Optional[Project]:
        """读取项目信息"""
        pass

    def save_project(self, project: Project) -> None:
        """保存项目信息到 outline.yml"""
        pass

    def ensure_project_structure(self, slug: str) -> None:
        """确保项目目录结构存在"""
        pass
```

## 9. 错误处理

### 9.1 错误响应格式

```json
{
  "error": {
    "code": "SLIDE_NOT_FOUND",
    "message": "指定的 slide 不存在",
    "details": {
      "sid": "slide-999"
    }
  }
}
```

### 9.2 错误码定义

| 错误码 | HTTP 状态码 | 描述 |
|--------|-------------|------|
| `PROJECT_NOT_FOUND` | 404 | 项目不存在 |
| `SLIDE_NOT_FOUND` | 404 | Slide 不存在 |
| `STYLE_NOT_SET` | 400 | 风格未设置 |
| `GENERATION_FAILED` | 500 | 图片生成失败 |
| `INVALID_REQUEST` | 400 | 请求参数无效 |
| `GEMINI_API_ERROR` | 502 | Gemini API 调用失败 |

## 10. 配置

### 10.1 环境变量

```bash
# .env
GEMINI_API_KEY=your_api_key_here
SLIDES_BASE_PATH=./slides
SERVER_HOST=0.0.0.0
SERVER_PORT=3003
CORS_ORIGINS=http://localhost:5173
```

### 10.2 后端配置

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    slides_base_path: str = "./slides"
    server_host: str = "0.0.0.0"
    server_port: int = 3003
    cors_origins: list[str] = ["http://localhost:5173"]

    # Gemini API 成本配置（USD per image）
    cost_per_style_image: float = 0.02
    cost_per_slide_image: float = 0.02

    class Config:
        env_file = ".env"
```

## 11. 安全考虑

1. **输入验证**: 所有 API 输入使用 Pydantic 进行严格验证
2. **路径安全**: 防止路径遍历攻击，slug 和 sid 只允许安全字符
3. **CORS**: 仅允许配置的源访问 API
4. **API Key 保护**: Gemini API Key 仅在后端使用，不暴露给前端
