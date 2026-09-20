import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from '../layouts/AppLayout';
import { ProtectedRoute } from '../routes/ProtectedRoute';
import { WorkspacePage } from '../pages/WorkspacePage';
import { HistoryPage } from '../pages/HistoryPage';
import { FavoritesPage } from '../pages/FavoritesPage';
import { DashboardPage } from '../pages/DashboardPage';
import { ProfilePage } from '../pages/ProfilePage';
import { PreferencesPage } from '../pages/PreferencesPage';
import { HistoryDetailPage } from '../pages/HistoryDetailPage';
import { LoginPage } from '../pages/LoginPage';
import { RegisterPage } from '../pages/RegisterPage';
import { NotFoundPage } from '../pages/NotFoundPage';
import { QuantumOverviewPage } from '../pages/quantum/QuantumOverviewPage';
import { QuantumTextPage } from '../pages/quantum/QuantumTextPage';
import { QuantumEmotionPage } from '../pages/quantum/QuantumEmotionPage';
import { QuantumSemanticPage } from '../pages/quantum/QuantumSemanticPage';
import { QuantumCircuitLabPage } from '../pages/quantum/QuantumCircuitLabPage';
import { QuantumBenchmarkPage } from '../pages/quantum/QuantumBenchmarkPage';

export const AppRouter: React.FC = () => {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        {/* Landing / Default redirect to Dashboard */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/app" element={<Navigate to="/dashboard" replace />} />
        <Route path="/app/dashboard" element={<Navigate to="/dashboard" replace />} />
        <Route path="/app/create" element={<Navigate to="/workspace" replace />} />
        <Route path="/app/workspace" element={<Navigate to="/workspace" replace />} />
        <Route path="/app/history" element={<Navigate to="/history" replace />} />
        <Route path="/app/history/:id" element={<HistoryDetailPage />} />
        <Route path="/app/favorites" element={<Navigate to="/favorites" replace />} />
        <Route path="/app/profile" element={<Navigate to="/profile" replace />} />
        <Route path="/app/preferences" element={<Navigate to="/preferences" replace />} />
        <Route path="/app/quantum" element={<Navigate to="/quantum" replace />} />

        {/* Public Authentication Routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected Application Routes */}
        <Route element={<ProtectedRoute />}>
          {/* Core Speech & Studio Routes */}
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/workspace" element={<WorkspacePage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/history/:id" element={<HistoryDetailPage />} />
          <Route path="/favorites" element={<FavoritesPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/preferences" element={<PreferencesPage />} />

          {/* Quantum Intelligence Laboratory Routes */}
          <Route path="/quantum" element={<QuantumOverviewPage />} />
          <Route path="/quantum/text" element={<QuantumTextPage />} />
          <Route path="/quantum/emotion" element={<QuantumEmotionPage />} />
          <Route path="/quantum/semantic" element={<QuantumSemanticPage />} />
          <Route path="/quantum/circuits" element={<QuantumCircuitLabPage />} />
          <Route path="/quantum/benchmark" element={<QuantumBenchmarkPage />} />
        </Route>

        {/* Catch-all 404 Route */}
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
};
