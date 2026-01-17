/** Home page - welcome screen when no database is selected. */

import { DatabaseOutlined, ThunderboltOutlined, SearchOutlined, CodeOutlined } from '@ant-design/icons';

export function HomePage() {
  return (
    <div className="h-full flex items-center justify-center bg-gradient-to-b from-white to-bg-secondary">
      <div className="text-center max-w-2xl mx-auto px-8 animate-fade-in">
        {/* Logo / Icon */}
        <div className="mb-8 animate-slide-up">
          <div className="inline-flex items-center justify-center w-24 h-24 rounded-3xl bg-accent-primary shadow-lg shadow-accent-primary/30">
            <DatabaseOutlined className="text-5xl text-text-primary" />
          </div>
        </div>

        {/* Title */}
        <h1 className="text-4xl md:text-5xl font-bold text-text-primary mb-4 animate-slide-up stagger-1">
          数据库查询工具
        </h1>

        {/* Subtitle */}
        <p className="text-lg text-text-secondary mb-12 leading-relaxed animate-slide-up stagger-2">
          使用自然语言或 SQL 轻松查询您的数据库
          <br />
          <span className="text-text-tertiary">支持 PostgreSQL 数据库</span>
        </p>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="card-static p-6 animate-slide-up stagger-3 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
            <div className="w-12 h-12 rounded-xl bg-accent-primary/20 flex items-center justify-center mb-4 mx-auto">
              <SearchOutlined className="text-2xl text-accent-secondary" />
            </div>
            <h3 className="font-semibold text-text-primary mb-2">自然语言查询</h3>
            <p className="text-sm text-text-secondary">
              用中文或英文描述您的查询需求
            </p>
          </div>

          <div className="card-static p-6 animate-slide-up stagger-4 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
            <div className="w-12 h-12 rounded-xl bg-accent-blue/20 flex items-center justify-center mb-4 mx-auto">
              <CodeOutlined className="text-2xl text-accent-blue" />
            </div>
            <h3 className="font-semibold text-text-primary mb-2">SQL 编辑器</h3>
            <p className="text-sm text-text-secondary">
              专业的 Monaco 编辑器支持
            </p>
          </div>

          <div className="card-static p-6 animate-slide-up stagger-5 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
            <div className="w-12 h-12 rounded-xl bg-accent-green/20 flex items-center justify-center mb-4 mx-auto">
              <ThunderboltOutlined className="text-2xl text-accent-green" />
            </div>
            <h3 className="font-semibold text-text-primary mb-2">快速执行</h3>
            <p className="text-sm text-text-secondary">
              高效查询并实时显示结果
            </p>
          </div>
        </div>

        {/* Call to Action */}
        <div className="animate-slide-up stagger-5">
          <div className="inline-flex items-center gap-2 px-5 py-2.5 bg-bg-tertiary rounded-full text-sm text-text-secondary">
            <span className="w-2 h-2 rounded-full bg-accent-green animate-pulse"></span>
            从左侧选择或添加数据库开始查询
          </div>
        </div>
      </div>
    </div>
  );
}
