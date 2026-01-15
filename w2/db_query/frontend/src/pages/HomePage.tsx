/** Home page - welcome screen when no database is selected. */

import { Card, Empty, Typography } from 'antd';
import { DatabaseOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

export function HomePage() {
  return (
    <div className="h-full flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100">
      <Card className="text-center shadow-lg border-0 rounded-xl" style={{ maxWidth: 500 }}>
        <div className="flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 mx-auto mb-6 shadow-lg">
          <DatabaseOutlined className="text-4xl text-white" />
        </div>
        <Title level={2} className="!mb-3 !text-gray-800">
          欢迎使用数据库查询工具
        </Title>
        <Text className="text-gray-600 text-base mb-6 block leading-relaxed">
          请从左侧边栏选择一个数据库连接，或点击"新增连接"添加新的数据库连接。
        </Text>
        <Empty
          description={
            <Text className="text-gray-500">从左侧选择数据库开始查询</Text>
          }
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    </div>
  );
}
