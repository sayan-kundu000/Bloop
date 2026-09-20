import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { AppProviders } from './providers';
import { AppRouter } from './router';
import { ErrorBoundary } from '../components/common/ErrorBoundary';

export const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <AppProviders>
        <BrowserRouter>
          <AppRouter />
        </BrowserRouter>
      </AppProviders>
    </ErrorBoundary>
  );
};

export default App;
