# MotherDuck 网站设计风格规范

> 本文档详细分析 MotherDuck (https://motherduck.com/) 的设计风格，并提供可复刻的设计规范。

---

## 一、总体设计风格

### 1.1 设计理念

- **极简现代主义**：强调"空间感"（white space / negative space），通过大量留白突出核心内容
- **友好科技感**：使用鸭子插图（duck illustrations）和趣味元素，降低企业软件的冷感
- **清晰视觉层次**：明确的信息层级，引导用户视线流动
- **柔和与专业并存**：色调偏柔和干净，但保持专业感

### 1.2 设计关键词

```
极简 | 留白 | 现代 | 友好 | 科技 | 扁平 | 清晰 | 专业
```

---

## 二、色彩系统 (Color Palette)

### 2.1 基础色彩

```css
:root {
  /* 背景色 */
  --color-bg-primary: #FFFFFF;           /* 主背景 - 纯白 */
  --color-bg-secondary: #F9FAFB;         /* 次级背景 - 极浅灰 */
  --color-bg-tertiary: #F3F4F6;          /* 第三级背景 - 浅灰 */
  
  /* 文本色 */
  --color-text-primary: #111827;         /* 主文本 - 深灰/近黑 */
  --color-text-secondary: #4B5563;       /* 次级文本 - 中灰 */
  --color-text-tertiary: #9CA3AF;        /* 辅助文本 - 浅灰 */
  --color-text-inverse: #FFFFFF;         /* 反色文本 - 白 */
  
  /* 强调色 / 品牌色 */
  --color-accent-primary: #FFCC00;       /* 主强调 - 鸭子黄 */
  --color-accent-secondary: #FF6B35;     /* 次强调 - 活力橙 */
  --color-accent-blue: #3B82F6;          /* 链接蓝 */
  --color-accent-green: #10B981;         /* 成功绿 */
  
  /* 边框色 */
  --color-border-light: #E5E7EB;         /* 浅边框 */
  --color-border-medium: #D1D5DB;        /* 中等边框 */
  
  /* 阴影色 */
  --color-shadow: rgba(0, 0, 0, 0.08);   /* 基础阴影 */
  --color-shadow-light: rgba(0, 0, 0, 0.04); /* 轻阴影 */
}
```

### 2.2 语义化色彩

```css
:root {
  /* 状态色 */
  --color-success: #10B981;
  --color-warning: #F59E0B;
  --color-error: #EF4444;
  --color-info: #3B82F6;
  
  /* 交互状态 */
  --color-hover-overlay: rgba(0, 0, 0, 0.04);
  --color-active-overlay: rgba(0, 0, 0, 0.08);
  --color-focus-ring: rgba(59, 130, 246, 0.5);
}
```

### 2.3 渐变色

```css
:root {
  /* 背景渐变 */
  --gradient-hero: linear-gradient(180deg, #FFFFFF 0%, #F9FAFB 100%);
  --gradient-accent: linear-gradient(135deg, #FFCC00 0%, #FF6B35 100%);
  --gradient-subtle: linear-gradient(180deg, rgba(255,204,0,0.05) 0%, rgba(255,255,255,0) 100%);
}
```

---

## 三、字体排版 (Typography)

### 3.1 字体族

```css
:root {
  /* 主字体 - 无衬线 */
  --font-family-sans: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  
  /* 代码字体 */
  --font-family-mono: 'JetBrains Mono', 'SF Mono', 'Fira Code', Consolas, monospace;
}
```

### 3.2 字体大小

```css
:root {
  /* 标题字号 */
  --font-size-display: 4rem;      /* 64px - 超大展示标题 */
  --font-size-h1: 3rem;           /* 48px - H1 标题 */
  --font-size-h2: 2.25rem;        /* 36px - H2 标题 */
  --font-size-h3: 1.75rem;        /* 28px - H3 标题 */
  --font-size-h4: 1.375rem;       /* 22px - H4 标题 */
  --font-size-h5: 1.125rem;       /* 18px - H5 标题 */
  
  /* 正文字号 */
  --font-size-lg: 1.125rem;       /* 18px - 大正文 */
  --font-size-base: 1rem;         /* 16px - 标准正文 */
  --font-size-sm: 0.875rem;       /* 14px - 小正文 */
  --font-size-xs: 0.75rem;        /* 12px - 辅助文字 */
}
```

### 3.3 字重

```css
:root {
  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  --font-weight-extrabold: 800;
}
```

### 3.4 行高

```css
:root {
  --line-height-tight: 1.2;       /* 标题 */
  --line-height-snug: 1.375;      /* 副标题 */
  --line-height-normal: 1.5;      /* 正文 */
  --line-height-relaxed: 1.625;   /* 长文本 */
  --line-height-loose: 2;         /* 宽松 */
}
```

### 3.5 字间距

```css
:root {
  --letter-spacing-tight: -0.025em;   /* 标题 */
  --letter-spacing-normal: 0;          /* 正文 */
  --letter-spacing-wide: 0.025em;      /* 大写文字 */
  --letter-spacing-wider: 0.05em;      /* 按钮/标签 */
}
```

### 3.6 排版预设

```css
/* 展示标题 */
.text-display {
  font-size: var(--font-size-display);
  font-weight: var(--font-weight-bold);
  line-height: var(--line-height-tight);
  letter-spacing: var(--letter-spacing-tight);
  color: var(--color-text-primary);
}

/* H1 标题 */
.text-h1 {
  font-size: var(--font-size-h1);
  font-weight: var(--font-weight-bold);
  line-height: var(--line-height-tight);
  letter-spacing: var(--letter-spacing-tight);
}

/* H2 标题 */
.text-h2 {
  font-size: var(--font-size-h2);
  font-weight: var(--font-weight-semibold);
  line-height: var(--line-height-snug);
  letter-spacing: var(--letter-spacing-tight);
}

/* H3 标题 */
.text-h3 {
  font-size: var(--font-size-h3);
  font-weight: var(--font-weight-semibold);
  line-height: var(--line-height-snug);
}

/* 正文 - 大 */
.text-body-lg {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-regular);
  line-height: var(--line-height-relaxed);
}

/* 正文 - 标准 */
.text-body {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-regular);
  line-height: var(--line-height-normal);
}

/* 正文 - 小 */
.text-body-sm {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-regular);
  line-height: var(--line-height-normal);
}

/* 标签/辅助文字 */
.text-caption {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-normal);
  letter-spacing: var(--letter-spacing-wide);
  text-transform: uppercase;
}
```

---

## 四、间距系统 (Spacing)

### 4.1 基础间距

```css
:root {
  /* 基础单位: 4px */
  --spacing-0: 0;
  --spacing-1: 0.25rem;    /* 4px */
  --spacing-2: 0.5rem;     /* 8px */
  --spacing-3: 0.75rem;    /* 12px */
  --spacing-4: 1rem;       /* 16px */
  --spacing-5: 1.25rem;    /* 20px */
  --spacing-6: 1.5rem;     /* 24px */
  --spacing-8: 2rem;       /* 32px */
  --spacing-10: 2.5rem;    /* 40px */
  --spacing-12: 3rem;      /* 48px */
  --spacing-16: 4rem;      /* 64px */
  --spacing-20: 5rem;      /* 80px */
  --spacing-24: 6rem;      /* 96px */
  --spacing-32: 8rem;      /* 128px */
}
```

### 4.2 语义化间距

```css
:root {
  /* 组件内部间距 */
  --padding-xs: var(--spacing-2);     /* 8px - 紧凑 */
  --padding-sm: var(--spacing-3);     /* 12px - 小 */
  --padding-md: var(--spacing-4);     /* 16px - 中等 */
  --padding-lg: var(--spacing-6);     /* 24px - 大 */
  --padding-xl: var(--spacing-8);     /* 32px - 超大 */
  
  /* 区块间距 */
  --section-gap-sm: var(--spacing-12);   /* 48px */
  --section-gap-md: var(--spacing-16);   /* 64px */
  --section-gap-lg: var(--spacing-24);   /* 96px */
  --section-gap-xl: var(--spacing-32);   /* 128px */
  
  /* 容器内边距 */
  --container-padding-x: var(--spacing-6);   /* 24px - 移动端 */
  --container-padding-x-md: var(--spacing-8); /* 32px - 平板 */
  --container-padding-x-lg: var(--spacing-16); /* 64px - 桌面端 */
}
```

---

## 五、布局系统 (Layout)

### 5.1 容器宽度

```css
:root {
  --container-xs: 320px;     /* 超窄容器 */
  --container-sm: 640px;     /* 窄容器 */
  --container-md: 768px;     /* 中等容器 */
  --container-lg: 1024px;    /* 大容器 */
  --container-xl: 1200px;    /* 超大容器 - 主内容 */
  --container-2xl: 1440px;   /* 最大容器 */
}
```

### 5.2 响应式断点

```css
/* 断点定义 */
$breakpoint-sm: 640px;    /* 小屏手机 */
$breakpoint-md: 768px;    /* 平板 */
$breakpoint-lg: 1024px;   /* 小桌面 */
$breakpoint-xl: 1280px;   /* 大桌面 */
$breakpoint-2xl: 1536px;  /* 超大屏 */
```

### 5.3 栅格系统

```css
:root {
  --grid-columns: 12;
  --grid-gap: var(--spacing-6);       /* 24px */
  --grid-gap-lg: var(--spacing-8);    /* 32px */
}

/* 栅格容器 */
.grid-container {
  display: grid;
  grid-template-columns: repeat(var(--grid-columns), 1fr);
  gap: var(--grid-gap);
}
```

### 5.4 主容器

```css
.container {
  width: 100%;
  max-width: var(--container-xl);
  margin-left: auto;
  margin-right: auto;
  padding-left: var(--container-padding-x);
  padding-right: var(--container-padding-x);
}

@media (min-width: 768px) {
  .container {
    padding-left: var(--container-padding-x-md);
    padding-right: var(--container-padding-x-md);
  }
}

@media (min-width: 1024px) {
  .container {
    padding-left: var(--container-padding-x-lg);
    padding-right: var(--container-padding-x-lg);
  }
}
```

---

## 六、边框与圆角 (Border & Border Radius)

### 6.1 边框

```css
:root {
  /* 边框宽度 */
  --border-width-thin: 1px;
  --border-width-medium: 2px;
  --border-width-thick: 3px;
  
  /* 边框样式预设 */
  --border-light: var(--border-width-thin) solid var(--color-border-light);
  --border-medium: var(--border-width-thin) solid var(--color-border-medium);
  --border-accent: var(--border-width-medium) solid var(--color-accent-primary);
}
```

### 6.2 圆角

```css
:root {
  --radius-none: 0;
  --radius-sm: 0.25rem;     /* 4px - 小圆角 */
  --radius-md: 0.5rem;      /* 8px - 中等圆角 */
  --radius-lg: 0.75rem;     /* 12px - 大圆角 */
  --radius-xl: 1rem;        /* 16px - 超大圆角 */
  --radius-2xl: 1.5rem;     /* 24px - 特大圆角 */
  --radius-full: 9999px;    /* 完全圆角 (胶囊形) */
}
```

### 6.3 圆角使用场景

| 组件 | 圆角值 | 说明 |
|------|--------|------|
| 按钮 | `--radius-lg` (12px) | 柔和圆润 |
| 卡片 | `--radius-xl` (16px) | 明显圆角 |
| 输入框 | `--radius-md` (8px) | 中等圆角 |
| 图片 | `--radius-lg` (12px) | 与内容一致 |
| 标签/Badge | `--radius-full` | 胶囊形状 |
| Modal/弹窗 | `--radius-2xl` (24px) | 大圆角 |
| Tooltip | `--radius-md` (8px) | 小巧圆角 |

---

## 七、阴影系统 (Shadows)

### 7.1 阴影层级

```css
:root {
  /* 阴影 - 由浅到深 */
  --shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 
               0 1px 2px -1px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 
               0 2px 4px -2px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 
               0 4px 6px -4px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 
               0 8px 10px -6px rgba(0, 0, 0, 0.1);
  --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  
  /* 内阴影 */
  --shadow-inner: inset 0 2px 4px 0 rgba(0, 0, 0, 0.05);
  
  /* 无阴影 */
  --shadow-none: none;
}
```

### 7.2 阴影使用场景

| 组件 | 阴影 | 说明 |
|------|------|------|
| 卡片 (默认) | `--shadow-sm` | 轻微浮起 |
| 卡片 (悬停) | `--shadow-lg` | 明显浮起 |
| 导航栏 (滚动后) | `--shadow-md` | 分层效果 |
| 下拉菜单 | `--shadow-lg` | 浮动层 |
| Modal | `--shadow-2xl` | 最高层级 |
| 按钮 (默认) | `--shadow-xs` | 微妙深度 |
| 按钮 (悬停) | `--shadow-sm` | 轻微提升 |

---

## 八、UI 组件规范 (Components)

### 8.1 按钮 (Buttons)

```css
/* 按钮基础样式 */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  
  padding: var(--spacing-3) var(--spacing-6);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  line-height: 1;
  
  border-radius: var(--radius-lg);
  border: none;
  cursor: pointer;
  
  transition: all 0.2s ease;
}

/* 主按钮 */
.btn-primary {
  background-color: var(--color-accent-primary);
  color: var(--color-text-primary);
  box-shadow: var(--shadow-xs);
}

.btn-primary:hover {
  background-color: #E6B800;
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

/* 次级按钮 */
.btn-secondary {
  background-color: transparent;
  color: var(--color-text-primary);
  border: var(--border-width-thin) solid var(--color-border-medium);
}

.btn-secondary:hover {
  background-color: var(--color-bg-secondary);
  border-color: var(--color-text-secondary);
}

/* 幽灵按钮 */
.btn-ghost {
  background-color: transparent;
  color: var(--color-text-primary);
}

.btn-ghost:hover {
  background-color: var(--color-hover-overlay);
}

/* 按钮尺寸 */
.btn-sm {
  padding: var(--spacing-2) var(--spacing-4);
  font-size: var(--font-size-sm);
}

.btn-lg {
  padding: var(--spacing-4) var(--spacing-8);
  font-size: var(--font-size-lg);
}
```

### 8.2 卡片 (Cards)

```css
.card {
  background-color: var(--color-bg-primary);
  border-radius: var(--radius-xl);
  padding: var(--padding-lg);
  
  box-shadow: var(--shadow-sm);
  border: var(--border-light);
  
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-4px);
}

/* 卡片头部 */
.card-header {
  margin-bottom: var(--spacing-4);
}

/* 卡片内容 */
.card-content {
  color: var(--color-text-secondary);
}

/* 卡片底部 */
.card-footer {
  margin-top: var(--spacing-6);
  padding-top: var(--spacing-4);
  border-top: var(--border-light);
}
```

### 8.3 导航栏 (Navbar)

```css
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  
  display: flex;
  align-items: center;
  justify-content: space-between;
  
  height: 72px;
  padding: 0 var(--spacing-6);
  
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  
  transition: all 0.3s ease;
}

.navbar.scrolled {
  box-shadow: var(--shadow-md);
  background-color: rgba(255, 255, 255, 0.95);
}

/* 导航链接 */
.nav-link {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  
  padding: var(--spacing-2) var(--spacing-4);
  border-radius: var(--radius-md);
  
  transition: all 0.2s ease;
}

.nav-link:hover {
  color: var(--color-text-primary);
  background-color: var(--color-hover-overlay);
}

/* 导航 CTA */
.nav-cta {
  margin-left: var(--spacing-4);
}
```

### 8.4 Hero 区域

```css
.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  
  padding-top: calc(72px + var(--spacing-24)); /* navbar height + spacing */
  padding-bottom: var(--spacing-24);
  padding-left: var(--container-padding-x);
  padding-right: var(--container-padding-x);
  
  background: var(--gradient-hero);
}

.hero-title {
  font-size: var(--font-size-display);
  font-weight: var(--font-weight-bold);
  line-height: var(--line-height-tight);
  letter-spacing: var(--letter-spacing-tight);
  
  max-width: 900px;
  margin-bottom: var(--spacing-6);
}

.hero-subtitle {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  
  max-width: 600px;
  margin-bottom: var(--spacing-10);
}

.hero-actions {
  display: flex;
  gap: var(--spacing-4);
  flex-wrap: wrap;
  justify-content: center;
}

/* 响应式 */
@media (max-width: 768px) {
  .hero-title {
    font-size: var(--font-size-h1);
  }
  
  .hero-subtitle {
    font-size: var(--font-size-base);
  }
}
```

### 8.5 功能区块 (Feature Section)

```css
.feature-section {
  padding: var(--section-gap-lg) 0;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--grid-gap-lg);
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.feature-icon {
  width: 48px;
  height: 48px;
  margin-bottom: var(--spacing-4);
  
  display: flex;
  align-items: center;
  justify-content: center;
  
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
}

.feature-title {
  font-size: var(--font-size-h4);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-3);
}

.feature-description {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
}

/* 响应式 */
@media (max-width: 1024px) {
  .feature-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .feature-grid {
    grid-template-columns: 1fr;
  }
}
```

### 8.6 输入框 (Inputs)

```css
.input {
  width: 100%;
  padding: var(--spacing-3) var(--spacing-4);
  
  font-size: var(--font-size-base);
  font-family: var(--font-family-sans);
  color: var(--color-text-primary);
  
  background-color: var(--color-bg-primary);
  border: var(--border-light);
  border-radius: var(--radius-md);
  
  transition: all 0.2s ease;
}

.input:focus {
  outline: none;
  border-color: var(--color-accent-primary);
  box-shadow: 0 0 0 3px var(--color-focus-ring);
}

.input::placeholder {
  color: var(--color-text-tertiary);
}

.input:disabled {
  background-color: var(--color-bg-secondary);
  cursor: not-allowed;
  opacity: 0.6;
}
```

### 8.7 Badge / 标签

```css
.badge {
  display: inline-flex;
  align-items: center;
  
  padding: var(--spacing-1) var(--spacing-3);
  
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  
  border-radius: var(--radius-full);
  background-color: var(--color-bg-secondary);
  color: var(--color-text-secondary);
}

.badge-accent {
  background-color: var(--color-accent-primary);
  color: var(--color-text-primary);
}

.badge-success {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}
```

---

## 九、动效与过渡 (Motion & Transitions)

### 9.1 过渡时间

```css
:root {
  --duration-fast: 150ms;
  --duration-normal: 200ms;
  --duration-slow: 300ms;
  --duration-slower: 500ms;
}
```

### 9.2 缓动函数

```css
:root {
  --ease-linear: linear;
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
```

### 9.3 通用过渡

```css
/* 默认过渡 */
.transition {
  transition-property: color, background-color, border-color, box-shadow, transform, opacity;
  transition-timing-function: var(--ease-in-out);
  transition-duration: var(--duration-normal);
}

/* 快速过渡 */
.transition-fast {
  transition-duration: var(--duration-fast);
}

/* 慢速过渡 */
.transition-slow {
  transition-duration: var(--duration-slow);
}
```

### 9.4 动画预设

```css
/* 淡入 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 从下滑入 */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 缩放进入 */
@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 应用动画 */
.animate-fadeIn {
  animation: fadeIn var(--duration-slow) var(--ease-out);
}

.animate-slideUp {
  animation: slideUp var(--duration-slow) var(--ease-out);
}

.animate-scaleIn {
  animation: scaleIn var(--duration-normal) var(--ease-out);
}
```

### 9.5 交错动画

```css
/* 用于列表项的交错进入动画 */
.stagger-item {
  animation: slideUp var(--duration-slow) var(--ease-out) backwards;
}

.stagger-item:nth-child(1) { animation-delay: 0ms; }
.stagger-item:nth-child(2) { animation-delay: 50ms; }
.stagger-item:nth-child(3) { animation-delay: 100ms; }
.stagger-item:nth-child(4) { animation-delay: 150ms; }
.stagger-item:nth-child(5) { animation-delay: 200ms; }
```

---

## 十、图标与插图 (Icons & Illustrations)

### 10.1 图标规范

```css
:root {
  /* 图标尺寸 */
  --icon-xs: 12px;
  --icon-sm: 16px;
  --icon-md: 20px;
  --icon-lg: 24px;
  --icon-xl: 32px;
  --icon-2xl: 48px;
}

/* 图标容器 */
.icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-sm { width: var(--icon-sm); height: var(--icon-sm); }
.icon-md { width: var(--icon-md); height: var(--icon-md); }
.icon-lg { width: var(--icon-lg); height: var(--icon-lg); }
```

### 10.2 插图风格指南

- **风格**: 扁平设计 (Flat Design) 或半扁平 (Semi-flat)
- **颜色**: 使用品牌色调，保持一致性
- **线条**: 简洁清晰，线宽统一
- **质感**: 可添加轻微渐变或高光，但不过于立体
- **主题**: 融入鸭子元素，保持趣味性

---

## 十一、可访问性 (Accessibility)

### 11.1 对比度要求

- 正常文本与背景对比度 ≥ 4.5:1 (WCAG AA)
- 大文本与背景对比度 ≥ 3:1
- UI 组件与背景对比度 ≥ 3:1

### 11.2 焦点状态

```css
/* 全局焦点样式 */
:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--color-focus-ring);
}

/* 按钮焦点 */
.btn:focus-visible {
  box-shadow: 0 0 0 3px var(--color-focus-ring);
}

/* 链接焦点 */
a:focus-visible {
  outline: 2px solid var(--color-accent-blue);
  outline-offset: 2px;
}
```

### 11.3 触控目标

```css
/* 最小触控目标尺寸: 44x44px */
.touch-target {
  min-width: 44px;
  min-height: 44px;
}
```

---

## 十二、Tailwind CSS 配置参考

如果使用 Tailwind CSS，以下是配置参考：

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'bg-primary': '#FFFFFF',
        'bg-secondary': '#F9FAFB',
        'bg-tertiary': '#F3F4F6',
        'text-primary': '#111827',
        'text-secondary': '#4B5563',
        'text-tertiary': '#9CA3AF',
        'accent-primary': '#FFCC00',
        'accent-secondary': '#FF6B35',
        'accent-blue': '#3B82F6',
        'border-light': '#E5E7EB',
        'border-medium': '#D1D5DB',
      },
      fontFamily: {
        sans: ['Inter', 'SF Pro Display', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['JetBrains Mono', 'SF Mono', 'Fira Code', 'monospace'],
      },
      fontSize: {
        'display': ['4rem', { lineHeight: '1.2', letterSpacing: '-0.025em' }],
        'h1': ['3rem', { lineHeight: '1.2', letterSpacing: '-0.025em' }],
        'h2': ['2.25rem', { lineHeight: '1.375', letterSpacing: '-0.025em' }],
        'h3': ['1.75rem', { lineHeight: '1.375' }],
        'h4': ['1.375rem', { lineHeight: '1.375' }],
      },
      borderRadius: {
        'sm': '0.25rem',
        'md': '0.5rem',
        'lg': '0.75rem',
        'xl': '1rem',
        '2xl': '1.5rem',
      },
      boxShadow: {
        'xs': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
        'card-hover': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
      },
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
      },
      maxWidth: {
        'container': '1200px',
        'content': '900px',
        'narrow': '600px',
      },
      animation: {
        'fadeIn': 'fadeIn 0.3s ease-out',
        'slideUp': 'slideUp 0.3s ease-out',
        'scaleIn': 'scaleIn 0.2s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
    },
  },
}
```

---

## 十三、设计检查清单

### ✅ 色彩
- [ ] 背景使用纯白或极浅灰
- [ ] 主文本使用深灰/近黑
- [ ] 强调色使用鲜明的黄色/橙色
- [ ] 对比度符合 WCAG AA 标准

### ✅ 排版
- [ ] 使用 Inter 或类似现代无衬线字体
- [ ] 标题使用粗体，层级分明
- [ ] 行高舒展，阅读舒适
- [ ] 字间距适当调整

### ✅ 间距
- [ ] 大量使用留白
- [ ] 区块间距充裕 (64-96px)
- [ ] 组件内边距适中 (16-24px)
- [ ] 遵循 4px 基础单位

### ✅ 组件
- [ ] 按钮圆角柔和 (12px)
- [ ] 卡片有轻微阴影和悬停效果
- [ ] 导航栏固定且有毛玻璃效果
- [ ] 输入框简洁有焦点样式

### ✅ 动效
- [ ] 过渡时间 150-300ms
- [ ] 使用 ease-out 缓动
- [ ] 悬停有轻微位移效果
- [ ] 页面元素有交错进入动画

### ✅ 响应式
- [ ] Mobile First 设计
- [ ] 断点: 640px / 768px / 1024px / 1280px
- [ ] 触控目标 ≥ 44px
- [ ] 内容在小屏上垂直堆叠

---

## 十四、示例代码

### 完整 Hero 区域示例

```html
<section class="hero">
  <div class="container">
    <span class="badge badge-accent">New Release</span>
    
    <h1 class="hero-title">
      The Serverless Data Warehouse for DuckDB
    </h1>
    
    <p class="hero-subtitle">
      Run analytical queries on your data with zero infrastructure. 
      Fast, simple, and affordable.
    </p>
    
    <div class="hero-actions">
      <a href="#" class="btn btn-primary btn-lg">
        Start Free
      </a>
      <a href="#" class="btn btn-secondary btn-lg">
        Learn More
      </a>
    </div>
  </div>
</section>
```

### 特性卡片示例

```html
<section class="feature-section">
  <div class="container">
    <h2 class="text-h2 text-center mb-16">Why MotherDuck?</h2>
    
    <div class="feature-grid">
      <div class="card">
        <div class="feature-icon">
          ⚡
        </div>
        <h3 class="feature-title">Blazing Fast</h3>
        <p class="feature-description">
          Powered by DuckDB, execute queries in milliseconds 
          on billions of rows.
        </p>
      </div>
      
      <div class="card">
        <div class="feature-icon">
          🔒
        </div>
        <h3 class="feature-title">Secure by Default</h3>
        <p class="feature-description">
          Enterprise-grade security with encryption at rest 
          and in transit.
        </p>
      </div>
      
      <div class="card">
        <div class="feature-icon">
          💰
        </div>
        <h3 class="feature-title">Cost Effective</h3>
        <p class="feature-description">
          Pay only for what you use with transparent pricing 
          and no hidden fees.
        </p>
      </div>
    </div>
  </div>
</section>
```

---

*本设计规范基于 MotherDuck 官网 (https://motherduck.com/) 分析整理，可用于复刻类似的现代、极简、友好的科技产品网站设计。*
