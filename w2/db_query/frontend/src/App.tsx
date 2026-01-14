import { Refine } from '@refinedev/core';
import { RefineKbar, RefineKbarProvider } from '@refinedev/kbar';
import {
  ErrorComponent,
  ThemedLayoutV2,
  ThemedSiderV2,
  useNotificationProvider,
} from '@refinedev/antd';
import dataProvider from '@refinedev/simple-rest';
import routerProvider, {
  DocumentTitleHandler,
  UnsavedChangesNotifier,
} from '@refinedev/react-router-v6';
import { BrowserRouter, Outlet, Route, Routes } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import '@refinedev/antd/dist/reset.css';

import { API_BASE } from './services/api';

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
                  <ThemedLayoutV2 Sider={() => <ThemedSiderV2 fixed />}>
                    <Outlet />
                  </ThemedLayoutV2>
                }
              >
                <Route index element={<div>Home Page - Coming in Phase 3</div>} />
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
