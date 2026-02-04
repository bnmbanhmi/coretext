import { useState } from 'react'
import './App.css'
import NewListingPage from './pages/NewListingPage'
import HomePage from './pages/HomePage'

function App() {
  const [currentPage, setCurrentPage] = useState('home')

  const handleSuccess = () => {
    // Redirect to home or detail after success (Detail page not implemented yet per story scope, creating placeholder)
    alert("Redirecting to Detail Page (Not Implemented)")
    setCurrentPage('home')
  }

  return (
    <div className="app-container">
      <header>
        <h1>Trore Real Estate</h1>
        <nav>
          <button onClick={() => setCurrentPage('home')}>Home</button>
          <button onClick={() => setCurrentPage('new-listing')}>New Listing</button>
        </nav>
      </header>

      <main>
        {currentPage === 'home' && (
          <HomePage />
        )}
        {currentPage === 'new-listing' && (
          <NewListingPage onSuccess={handleSuccess} />
        )}
      </main>
    </div>
  )
}

export default App
