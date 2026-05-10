/**
 * Main App with Routing
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import PDFLibrary from './pages/PDFLibrary';
import ChatPage from './pages/ChatPage';
import QuizPage from './pages/QuizPage';
import AnalyticsPage from './pages/AnalyticsPage';
import EvaluationPage from './pages/EvaluationPage';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthService } from './utils/auth';

function App() {
    const isAuthenticated = AuthService.isAuthenticated();

    return (
        <BrowserRouter>
            <Routes>
                {/* Public Routes */}
                <Route
                    path="/login"
                    element={isAuthenticated ? <Navigate to="/dashboard" /> : <Login />}
                />
                <Route
                    path="/register"
                    element={isAuthenticated ? <Navigate to="/dashboard" /> : <Register />}
                />

                {/* Protected Routes */}
                <Route
                    path="/dashboard"
                    element={
                        <ProtectedRoute>
                            <Dashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/pdfs"
                    element={
                        <ProtectedRoute>
                            <PDFLibrary />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/chat/:pdfId"
                    element={
                        <ProtectedRoute>
                            <ChatPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/quiz/:pdfId?"
                    element={
                        <ProtectedRoute>
                            <QuizPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/analytics"
                    element={
                        <ProtectedRoute>
                            <AnalyticsPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/evaluation"
                    element={
                        <ProtectedRoute>
                            <EvaluationPage />
                        </ProtectedRoute>
                    }
                />

                {/* Redirect root to dashboard or login */}
                <Route
                    path="/"
                    element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />}
                />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
