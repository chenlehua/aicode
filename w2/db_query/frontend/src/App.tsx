import { Refine } from '@refinedev/core';
import { RefineKbar, RefineKbarProvider } from '@refinedev/kbar';
import {
  ErrorComponent,
  useNotificationProvider,
} from '@refinedev/antd';
import dataProvider from '@refinedev/simple-rest';
import routerProvider, {
  DocumentTitleHandler,
  UnsavedChangesNotifier,
} from '@refinedev/react-router-v6';
import { BrowserRouter, Outlet, Route, Routes } from 'react-router-dom';
import { ConfigProvider, Layout } from 'antd';
import '@refinedev/antd/dist/reset.css';

import { API_BASE } from './services/api';
import { HomePage } from './pages/HomePage';
import { DatabasePage } from './pages/DatabasePage';
import { CustomSider } from './components/CustomSider';

const { Sider, Content } = Layout;

// MotherDuck Theme Configuration
const themeConfig = {
  token: {
    colorPrimary: '#FFCC00',
    colorSuccess: '#10B981',
    colorWarning: '#F59E0B',
    colorError: '#EF4444',
    colorInfo: '#3B82F6',
    colorTextBase: '#111827',
    colorBgBase: '#FFFFFF',
    borderRadius: 8,
    fontFamily: "'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif",
    fontSize: 14,
    lineHeight: 1.6,
  },
  components: {
    Button: {
      borderRadius: 12,
      controlHeight: 40,
      fontWeight: 600,
    },
    Input: {
      borderRadius: 8,
      controlHeight: 40,
    },
    Card: {
      borderRadius: 16,
    },
    Modal: {
      borderRadius: 24,
    },
  },
};

function App() {
  return (
    <BrowserRouter>
      <RefineKbarProvider>
        <ConfigProvider theme={themeConfig}>
          <Refine
            dataProvider={dataProvider(API_BASE)}
            routerProvider={routerProvider}
            notificationProvider={useNotificationProvider}
            resources={[
              {
                name: 'databases',
                list: '/',
              },
            ]}
            options={{
              syncWithLocation: true,
              warnWhenUnsavedChanges: true,
              useNewQueryKeys: true,
            }}
          >
            <Routes>
              <Route
                element={
                  <Layout className="h-screen bg-bg-secondary">
                    <Sider
                      width={320}
                      className="border-r border-border-light shadow-sm"
                      style={{ background: '#FFFFFF' }}
                    >
                      <CustomSider />
                    </Sider>
                    <Content className="overflow-auto bg-bg-secondary">
                      <Outlet />
                    </Content>
                  </Layout>
                }
              >
                <Route index element={<HomePage />} />
                <Route path="/databases/:name" element={<DatabasePage />} />
                <Route path="*" element={<ErrorComponent />} />
              </Route>
            </Routes>
            <RefineKbar />
            <UnsavedChangesNotifier />
            <DocumentTitleHandler />
          </Refine>
        </ConfigProvider>
      </RefineKbarProvider>
    </BrowserRouter>
  );
}

export default App;
