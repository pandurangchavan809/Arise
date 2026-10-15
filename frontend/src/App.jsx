import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import AppLayout from './pages/AppLayout';
import AssistantPage from './pages/AssistantPage';
import MemoryBrowserPage from './pages/MemoryBrowserPage';
import QualityInspectorPage from './pages/QualityInspectorPage';
import DeveloperPage from './pages/DeveloperPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Landing Page */}
        <Route path="/" element={<LandingPage />} />

        {/* Product Application Shell */}
        <Route path="/app" element={<AppLayout />}>
          <Route index element={<Navigate to="/app/assistant" replace />} />
          <Route path="assistant" element={<AssistantPage />} />
          <Route path="memory" element={<MemoryBrowserPage />} />
          <Route path="quality" element={<QualityInspectorPage />} />
          <Route path="developer" element={<DeveloperPage />} />
        </Route>

        {/* Catch-all route */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
