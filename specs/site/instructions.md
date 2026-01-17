## 详细介绍 speckit

深度思考，查阅网上资料，帮我撰写一个./site/speckit-intro.mdx文件，内容为speckit的完整学习资料，包括 speckit 的架构， 设计， 组件， 流程等， 使用 mermaid 绘制架构，设计，组件，流程等图表并详细说明。然后再介绍speckit的用法。


## UI/UX cursor rules设计

仔细浏览https://motherduck.com/，分析其页面的设计风格，抽取设计风格的核心要素，如border/padding/margin/font/color/typographics/components,撰写一个可以复刻motherduck的网站设计风格。

生成一个 motherduck 风格的前端设计 rules 放在 .cursor/rules/motherduck-style.md ，以下我获取到的要素：


## 更换网站设计风格

@.cursor/rules/motherduck-style.md 基于新的设计风格，把./sites 的整体风格重构一下

更新： @.cursor/rules/motherduck-style.md以及网站 global css: motherduck不使用圆角，全部是直角，并且特定的border是黑粗线条；页面背景颜色需要改成和它一致的颜色。另外，很多地方的padding/margin似乎都乱了。请仔细阅读代码并修复所有的问题。

很多页面元素的间距有问题，请一个个排查，使用playwright mcp检查确保每个页面都显示正确。

所有页面都需要处理。文字的间距也要妥善处理，nav/footer也都不对。

修复所有组件和页面的css style问题，现在组件间间距，文字间间距都有些问题。

按钮之间的间距也要好一些。另外，line要黑粗，像motherduck 风格。

section之间用不同的颜色和粗线条过渡。
