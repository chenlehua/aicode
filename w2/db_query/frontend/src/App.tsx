import { Refine } from '@refinedev/core';
import { RefineKbar, RefineKbarProvider } from '@refinedev/kbar';
import {
  ErrorComponent,
  ThemedLayoutV2,
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

function App() {
  return (
    <BrowserRouter>
      <RefineKbarProvider>
        <ConfigProvider>
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
                  <Layout className="h-screen">
                    <Sider width={300} className="border-r border-gray-200">
                      <CustomSider />
                    </Sider>
                    <Content className="overflow-auto">
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
