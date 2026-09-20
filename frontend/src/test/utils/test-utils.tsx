import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, MemoryRouterProps } from 'react-router-dom';

/**
 * Creates an isolated QueryClient configured for unit tests
 * (no retries, zero cache latency).
 */
export function createTestQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });
}

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  route?: string;
  queryClient?: QueryClient;
}

/**
 * Custom render function injecting isolated QueryClient and MemoryRouter
 */
export function renderWithProviders(
  ui: ReactElement,
  {
    route = '/',
    queryClient = createTestQueryClient(),
    ...renderOptions
  }: CustomRenderOptions = {}
) {
  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    return (
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={[route]}>
          {children}
        </MemoryRouter>
      </QueryClientProvider>
    );
  };

  return {
    ...render(ui, { wrapper: Wrapper, ...renderOptions }),
    queryClient,
  };
}

export * from '@testing-library/react';
