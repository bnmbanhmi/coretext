import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';
import HomePage from './pages/HomePage';
import NewListingPage from './pages/NewListingPage';
import ListingDetailPage from './pages/ListingDetailPage';
import AdminDashboard from './pages/admin/AdminDashboard';
import EditListingPage from './pages/admin/EditListingPage';

function AppContent() {
  const navigate = useNavigate();

  return (
    <div className="app-container">
      <header>
        <h1>Trore Real Estate</h1>
        <nav className="flex gap-4 justify-center my-4">
          <Link to="/" className="text-blue-500 hover:underline">Home</Link>
          <Link to="/new-listing" className="text-blue-500 hover:underline">New Listing</Link>
          <Link to="/admin/listings" className="text-blue-500 hover:underline">Admin Dashboard</Link>
        </nav>
      </header>

      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/new-listing" element={<NewListingPage onSuccess={() => navigate('/')} />} />
          <Route path="/listing/:id" element={<ListingDetailPage />} />
          <Route path="/admin/listings" element={<AdminDashboard />} />
          <Route path="/admin/listings/:id/edit" element={<EditListingPage />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  )
}

export default App
