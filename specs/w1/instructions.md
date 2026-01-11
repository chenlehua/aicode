# Instructions

## project alpha 需求和设计档

构建一个简单的，使用标签分类和管理 ticket 的工具。
它基于 Postgres数据库， 使用 Fast API 作为后端，使用Typescript/Vite/Tailwind/Shadcn 作为前端。无需用户系统，当前用户可以：

- 创建/编辑/删除/完成/取消完成 ticket
- 创建/删除 ticket 的标签
- 按照不同的标签查看 ticket 列表
- 按 title 搜索ticket

按照这个想法，帮我生成详细的需求和设计文档，放在./specs/w1/0001-spec.md 文件中, 输出为中文。

## implementation plan

按照 ./specs/w1/0001-spec.md 文件中的需求和设计文档，帮我生成实现计划，放在./specs/w1/0002-implementation-plan.md 文件中, 输出为中文。

## phased implementation

按照 ./specs/w1/0002-implementation-plan.md 完整实现这个项目的 phase 1代码。

## api test

帮我根据rest client 撰写一个文件，里面包含对所有支持的 API 的测试

## seed sql

添加一个seed.sql 里面放50个 meaningful的ticket 和 几十个tags(包含platform tag，如ios，project tag 如viking，功能性tag如autocomplete,等等)。要求seed文件正确可以通过psql执行。

## pre commit

use pre-commit to init the config and setup prcommit for python and typescript for this project, also setup github action properly.
