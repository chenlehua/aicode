# Instructions

## 基本思路

这是一个数据库查询工具，用户可以添加一个 db url，系统会连接到数据库，获取数据库的 metadata，然后将数据库中的table 和 view 的信息展示出来，然后用户可以自己输入 sql 查询，也可以通过自然语言来生成 sql 查询。

基本想法：
- 数据库连接字符串和数据库的 metadata 都会存储到 sqlite 数据库中。我们可以根据 postgres 的功能来查询系统中的表和视图的信息，然后用LLM来将这些信息转换成 json 格式，然后存储到 sqlite 数据库中。这些信息以后可以复用。
- 当用户使用 LLM 来生成 sql 查询时， 我们可以把系统中的表和视图的信息作为 context 传递给LLM， 然后 LLM会根据这些信息来生成sql 查询。
- 任何输入的sql语句，都需要经过sqlparser解析，确保语法正确，并且包含select语句。如果语法不正确，需要给出错误信息。
- 如果查询不包含 limit 子句，则默认添加limit 1000 子句。
- 输出格式是json，前端将其组织成表格，并显示出来。

后端使用 Python （uv）/FastAPI /sqlglot /openai sdk来实现
前端使用React/refine 5/tailwind /ant design 来实现。sql editor使用monaco editor来实现。
