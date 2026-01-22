# Instructions

## AI Slides explore（Gemini）

帮我研究一下市面上关于使用AI进行slides生成的工具，尤其是Manus和NotebookLM的slide功能。探索它实现的原理。另外，探索如果使用google最新推出的nana banana pro来做slides生成（思考：根据文本生成图片，把所有图片以幻灯片的形式连接起来播放就构成了slides，类似NotebookLM里的slides生成，要求：图片的视觉风格要统一，用户可以提供一个视觉风格图片或者文字描述）。


## prd

根据 @specs/w7/genslide.png 的内容， 仔细阅读并思考，生成一个./specs/w7/0001-prd.md的PR。要求：使用中文。这个app 是一个本地运行的单页 app,使用 nano banaba pro 生成图片 slides， 可以以走马灯的形式全屏播出。后端使用 Python，前端使用 Typescript。

prd需要修改：
1.对于侧边栏slide，选中并拖拽可以改变顺序
2.用户单击侧边栏slide，在右侧预览区显示对应图片
3.用户双击侧边栏slide，可以编辑slide的文字内容。

prd需要修改：
1.文字内容变更后触发新图片生成

prd需要修改：
1.文本内容变化后，如果图片中没有对应文本hash的图片，在主图片区域下放一个按钮，用户点击可以生成新的图片
2.主图片区域底部显示该slide所有图片的缩略图，用户可切换预览。
3.播放功能支持键盘控制（左右箭头切换、ESC退出）
4.在界面上展示当前slides的总体生成成本，帮助用户了解API调用费用

prd需要修改：
1.outline.yml中需要保存用户选择的风格图片。当第一次打开时，如果没有风格图片，需要有个popup，用户可以输入一段文字，生成两个图片，让用户选择，用户选中的作为slides 的风格，以后生成新的图片时参考这张图片
2.nano banaba pro API key -> Genimi API Key

prd需要修改：
1.outline 里的 style 包含： prompt 和 iamge，不要仅保存style.jpg
2.后续生成新图片时，将风格图片作为参考一并传给Gemini API
3.用户可以在设置中重新选择或生成新的风格图片，修改风格后不影响已生成的图片
4.Logo右边需要新增slides 题头输入框

prd需要修改：
1.文本内容变化后，如果图片中没有对应文本hash的图片，不要立即生成图片，在主图片区域下放一个按钮，用户点击可以生成新的图片

## 生成 design spec

根据 ./specs/w7/0001-prd.md 文件和@specs/w7/genslide.png的内容，生成一个 ./specs/w7/0002-design-spec.md 文件，输出为中文。注意所有前端所需的API接口要定义清楚。整体项目的目录结构也要定义清楚，后端代码层次清晰，API/业务/存储要保持清晰的边界。


google ai sdk 使用：https://ai.google.dev/gemini-api/docs/image-generation，其中核心代码：
from google import genai
from google.genai import types
from PIL import Image

client = genai.Client()

prompt = ("Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme")
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[prompt],
)

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = part.as_image()
        image.save("generated_image.png")

这里 nano banana pro的模型名： 更新 design spec


注意项目使用 uv 所有的 dep 管理和命令度使用uv。请确保所有的 dep 都使用最新版本

## 生成目录结构

根据 ./specs/w7/0002-design-spec.md 文件，生成项目的空的目录结构。先不要生成代码。在backend/和frontend/目录下分别生成 CLAUDE.md 文件，内容考虑：

- 所使用语言框架的best practices
- 架构设计遵循的原则： SOLID/YAGNI/KISS/DRY/etc.
- 代码的组织结构
- 并发处理
- 错误处理和日志处理

项目放在./w7/genslides目录下。

## 页面风格



目前前端界面有很大的问题：
1. 界面很粗糙，没有美感
2.请再次阅读@specs/w7/genslide.png和./specs/w7/0002-design-spec.md中的设计稿，优化界面，使其更加美观，符合设计稿的要求。
3.侧边栏slide中不应该显示图片，直接显示所有文字，不要显示图片，主图片区域底部的文字去掉。
4.主图片区域底部显示该slide所有图片的缩略图，用户可切换预览。


主图片区域底部应该有缩略图，缩略图应该居中，浮在图片上。生成图片的按钮不需要了，其功能放在缩略图列表即可：当文字和图片没有匹配时，显示+button（tooltip：生成当前文字的图片）


请仔细阅读./w7/genslides/frontend下代码，以及./specs/w7/0002-design-spec.md中的设计稿，优化界面：
1.对于侧边栏slide，选中并拖拽可以改变顺序
2.左上角应该有LoGo和工具名称GenSlides，请根据当前系统的功能设计LoGO
3.用户点击某个 slide 后设定锚点，按回车键在该 slide 下方创建新的 slide



请仔细阅读./w7/genslides/frontend下代码，以及./specs/w7/0002-design-spec.md中的设计稿，优化如下功能：
 1.首次进入http://localhost:5173/后，提示新建项目或者选择已有项目。
 2.也可直接访问http://localhost:5173/<slug>，<slug>为项目名称，如http://localhost:5173/my-project。



1.现在按回车会直接新建slide，而不是用户点击某个 slide 后设定锚点，按回车键在该 slide 下方创建新的 slide，请修复
2.Logo和工具名称叛变的 项目名称和新建项目时保持一致，url路径中<slug>应该根据项目名称生成唯一字符串



## 生成图片提示词 

使用浅黄色/红褐色的水彩画风格，走可爱卡通路线，主要角色是一只黄色的可爱的鸭子，类似motherduck的风格

Gen slide 介绍

标题： Gen slide 介绍
要求： 文字显眼，水平/垂直都居中

根据项目代码分别生成 ascii chart:
1.前端架构
2.后端架构
3.数据流图
4.前端技术栈
5.后端技术栈

保存到./specs/w7/0003-ascii-chart.md文件中

前端架构：


标题：前端架构
