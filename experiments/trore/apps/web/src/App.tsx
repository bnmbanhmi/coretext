import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { Toaster } from 'sonner';
import { NewListingPage } from './features/admin/pages/NewListingPage';
import { EditListingPage } from './features/dashboard/pages/EditListingPage';
import { ListingListPage } from './features/listing/pages/ListingListPage';
import { ListingDetailPage } from './features/listing/pages/ListingDetailPage';
import { AdminRoute } from './lib/auth';
import './App.css';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route 
            path="/admin/listings/new" 
            element={
              <AdminRoute>
                <NewListingPage />
              </AdminRoute>
            } 
          />
          <Route 
            path="/admin/listings/edit/:id" 
            element={
              <AdminRoute>
                <EditListingPage />
              </AdminRoute>
            } 
          />
          <Route path="/listings/:id" element={<ListingDetailPage />} />
          <Route path="/" element={<ListingListPage />} />
        </Routes>
        <Toaster />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;