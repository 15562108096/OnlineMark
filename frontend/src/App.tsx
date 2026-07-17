import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./store/AuthContext";
import AppLayout from "./components/AppLayout";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import TemplateListPage from "./pages/TemplateListPage";
import TemplateEditorPage from "./pages/TemplateEditorPage";
import ScanBatchPage from "./pages/ScanBatchPage";
import GradingPage from "./pages/GradingPage";
import ScoresPage from "./pages/ScoresPage";
import UserManagementPage from "./pages/UserManagementPage";
import { Spin } from "antd";

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return <Spin size="large" style={{ display: "block", margin: "200px auto" }} />;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

const App: React.FC = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return <Spin size="large" style={{ display: "block", margin: "200px auto" }} />;
  }

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="templates" element={<TemplateListPage />} />
        <Route path="templates/new" element={<TemplateEditorPage />} />
        <Route path="templates/:id/edit" element={<TemplateEditorPage />} />
        <Route path="scan" element={<ScanBatchPage />} />
        <Route path="grading" element={<GradingPage />} />
        <Route path="scores" element={<ScoresPage />} />
        <Route path="users" element={<UserManagementPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default App;
