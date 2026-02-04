import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { Toaster } from 'sonner';
import { NewListingPage } from './features/admin/pages/NewListingPage';
import { ListingListPage } from './features/listing/pages/ListingListPage';
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
          <Route path="/" element={<ListingListPage />} />
        </Routes>
        <Toaster />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;