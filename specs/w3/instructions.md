# Instructions

## code review command

帮我参照 @./claude/commands/speckit.specify.md 的结构，think ultra hard，构建一个对 Python 和 Typescript 代码进行深度代码审查的命令，放在 @./claude/commands/ 目录下。主要考虑一下几个方面：

- 架构和设计： 是否考虑 Python 和 typescript 的架构和设计z最佳实践？是否有清晰的接口设计？是否考虑一定程度的可扩展性
- KISS 原则
- 代码质量： DRY, YAGNI, SOLID, etc.函数原则上不超过 150 行，参数原则上不超过 7 个。
- 使用 builder 模式



## Python Review

你是一个 Python 开发的资深系统级工程师， 可以进行优雅的架构设计， 遵循Python哲学， 并对并发异步/web/grpc/数据库/缓存/消息队列/异步任务/定时任务/日志/监控/报警/告警/大数据处理等有深刻的理解。


帮我仔细查看 ./w2/db_query/backend 的架构，目前因为添加了新的数据库， 需要重新考虑整体的设计， 最好设计一套interface，为以后添加更多数据库留有余地，不至于到处修改已有代码。 设计要符合 Open-Close 和 SOLID 原则。新的设计放在 ./specs/w2/0001-improvement.md


按照 ./specs/w2/0001-improvement.md 文件中的重构设计，帮我生成实现计划，放在./specs/w2/0002-improvement-implementation-plan.md 文件中, 输出为中文。


根据以上的重构设计 ./specs/w2/0001-improvement.md 和 ./specs/w2/0002-improvement-implementation-plan.md，完整实现所有 phase，并确保  ./w2/db_query/fixtures/test-mysql.rest 和 test.rest中的所有测试用例全部通过。
