import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';
import HomePage from './pages/HomePage';
import NewListingPage from './pages/NewListingPage';
import ListingDetailPage from './pages/ListingDetailPage';

function AppContent() {
  const navigate = useNavigate();

  return (
    <div className="app-container">
      <header>
        <h1>Trore Real Estate</h1>
        <nav className="flex gap-4 justify-center my-4">
          <Link to="/" className="text-blue-500 hover:underline">Home</Link>
          <Link to="/new-listing" className="text-blue-500 hover:underline">New Listing</Link>
        </nav>
      </header>

      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/new-listing" element={<NewListingPage onSuccess={() => navigate('/')} />} />
          <Route path="/listing/:id" element={<ListingDetailPage />} />
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
