/**
 * Core API Client Type Definitions
 */

import { ApiSuccess, ApiErrorData, ApiResponse, PaginatedResponse, PaginationMeta } from '../../types';
import { FrontendApiError } from './errors';

export type { ApiSuccess, ApiErrorData, ApiResponse, PaginatedResponse, PaginationMeta, FrontendApiError };

export interface RequestOptions {
  headers?: Record<string, string>;
  params?: Record<string, unknown>;
  timeout?: number;
}
