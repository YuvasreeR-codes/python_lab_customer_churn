import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { BrowserRouter } from 'react-router-dom'
import CustomerSearch from './pages/CustomerSearch.jsx'
import ChurnSummary from './pages/ChurnSummary.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    
    <App />
    {/* <CustomerSearch />
    <ChurnSummary /> */}
  </StrictMode>,
)
