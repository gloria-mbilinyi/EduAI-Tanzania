import React from 'react'
import ReactDOM from 'react-dom/client'
import {BrowserRouter,Routes,Route,Navigate} from 'react-router-dom'
import {AuthProvider} from './contexts/Auth'
import {I18nProvider} from './i18n'
import {Dashboard} from './layouts/Dashboard'
import {Public,AuthPage} from './pages/Public'
import './styles.css'
function App(){return <Routes><Route path="/" element={<Public/>}/><Route path="/login" element={<AuthPage/>}/><Route path="/register" element={<AuthPage register/>}/><Route path="/app" element={<Dashboard/>}><Route index element={<Navigate to="overview" replace/>}/></Route><Route path="/:section" element={<Public/>}/><Route path="*" element={<Navigate to="/" replace/>}/></Routes>}
ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><BrowserRouter><I18nProvider><AuthProvider><App/></AuthProvider></I18nProvider></BrowserRouter></React.StrictMode>)
