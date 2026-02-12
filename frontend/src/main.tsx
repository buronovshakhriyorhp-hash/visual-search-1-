import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx' // Import App.jsx (ignoring TS warning for now or using allowJs)
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>,
)
