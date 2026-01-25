# Instructions

## 构建 postgres 查询的 skill

在当前项目下创建一个新的skill，要求：

1. 首先通过psql（localhost：5432，postgres，postgres）
探索这几个数据库：blog_db、ecommerce_db、erp_db，了解它们都有哪些 table/view/types/index等等， 每个数据库一个 md 文件， 作为skill 的reference。
2. 用户可以给特定自然语言描述的查询的需求，skill 根据用户输入找到相应的数据库的 reference文件，然后根据这些信息以及用户的输入来生成正确的SQL。SQL只允许查询语句， 不能有任何的写操作， 不能有任何安全漏洞比如SQL注入，不能有任何危险的操作比如 sleep，不能有任何的敏感信息比如 API key 等。
3. 使用 psql 测试这个SQL确保它能够执行并且返回有意义的结果。如果执行失败，则深度思考，重新生成SQL，回到第3步。
4. 把用户的输入， 生成的SQL， 以及返回的结果的一部分进行分析来确认结果是不是有意义， 根据分析打个分数。10分非常confident， 0分非常不confident。r如果小于7分， 则深度思考， 重新生成SQL，回到第3步。
5. 最后根据用户的输入是返回SQL还是返回SQL查询之后的结果（默认）来返回相应的内容。

这个skill放在当前项目的 ./claude/skills/pg-data下
