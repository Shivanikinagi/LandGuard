import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './hooks/useAuth.jsx'
import { ToastContainer } from 'react-toastify'
import { ThemeProvider, CssBaseline } from '@mui/material'
import theme from './theme'
import 'react-toastify/dist/ReactToastify.css'
import './styles/App.css'

// Components
import Layout from './components/Layout'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import LandRecordList from './components/LandRecordList'
import LandRecordDetail from './components/LandRecordDetail'
import AnalysisView from './components/AnalysisView'
import BulkUpload from './components/BulkUpload'
import ReportCenter from './components/ReportCenter'
import UserManagement from './components/UserManagement'

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('token')
  
  if (!token) {
    return <Navigate to="/login" replace />
  }
  
  return children
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <AuthProvider>
          <Routes>
            {/* Public Route */}
            <Route path="/login" element={<Login />} />
            
            {/* Protected Routes with Layout */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="land-records" element={<LandRecordList />} />
              <Route path="land-records/:id" element={<LandRecordDetail />} />
              <Route path="analysis" element={<AnalysisView />} />
              <Route path="bulk-upload" element={<BulkUpload />} />
              <Route path="reports" element={<ReportCenter />} />
              <Route path="users" element={<UserManagement />} />
            </Route>
          </Routes>
          
          <ToastContainer
            position="top-right"
            autoClose={3000}
            hideProgressBar={false}
            newestOnTop
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
          />
        </AuthProvider>
      </Router>
    </ThemeProvider>
  )
}

export default App