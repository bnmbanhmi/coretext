import React from 'react';
import { Navigate } from 'react-router-dom';

// Mock auth - always true for MVP
const isAuthenticated = true;
const isAdmin = true;

export const AdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  if (!isAuthenticated || !isAdmin) {
    return <Navigate to="/" />;
  }
  return <>{children}</>;
};
