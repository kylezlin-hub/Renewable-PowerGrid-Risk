import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './theme.css'
import { runSelfTest } from './lib/selftest.js'

// In dev, verify the JS math matches the Python-exported validation targets.
if (import.meta.env.DEV) {
  runSelfTest()
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
