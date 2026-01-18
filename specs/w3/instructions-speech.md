# Instructions


## Specification

帮我探索 elevenlabs实时transcribe API(scribe v2 realtime)的typescript例子， 并帮我构思如何实现一个类似Wispr Flow的工具，要求：app使用tauri 2实现，app打开后，常驻systray,用户使用“cmd+shift+\” hotkey可以开启或者停止transcribing.从scribe v2 api获得的文本插入到当前active app的光标的位置（如何当前光标位置不可输入，那么就在停止transcribing时，把内容拷贝到剪贴板，用户可以粘贴到想要的地方）。


## 构建详细的设计文档

根据./specs/w3/0001-spec.md 中内容， 进行系统的 web search 确保信息的准确性， 尤其是使用最新版本的 dependencies。根据你了解的知识，构建一个详细的设计文档，放在./specs/w3/0002-design.md 文件中, 输出为中文, 使用 mermaid 绘制架构、设计、组件、流程等图表并详细说明。


## 构建实现计划

根据./specs/w3/0002-design.md 文件中的设计，构建一个详细的实现计划，放在./specs/w3/0003-implementation-plan.md 文件中, 输出为中文。

## 实现所有 phase

当前项目的目录在./w3/raflow下，根据./specs/w3/0002-design.md和./specs/w3/0003-implementation-plan.md 文件中的设计，实现所有 phase，并确保所有测试用例全部通过。

## hotkey闪退

按下 hotkey 系统闪退

## 录音错误

有很多buffer相关的错误

## buffer pool 错误

还是有 buffer pool的问题，并且我没有看到在悬浮窗口上实时的transcribe 内容

## TLS设置错误

新的错误， 貌似没有设置好TLS



## 不使用 overlap

现在通过 websocket发送的时间间隔是多少？我们是不是可以收集500ms或者1s的内容再去转译？另外， overlay window没有意义， 我是想把内容直接写到当前活跃窗口 focus的元素中，如果是input则直接插入，不是就写到剪切板，用户可以手工插入。

## 使用 nnnoiseless

使用nnnoiseless来处理噪音， 是的转译结果更加准确

## 使用简体中文

使用简体中文，这个应该是在elevenlabs API配置，请查阅其文档。 另外floating的window大小更大一些， 可以显示更多的内容。


## 生成更新的 design doc

仔细阅读目前 ./w3/raflow的代码， think untra hard， 构建一个更新的 design doc， 放在./specs/w3/0004-design.md 文件中, 输出为中文, 使用 mermaid 绘制架构、设计、组件、流程等图表并详细说明。
