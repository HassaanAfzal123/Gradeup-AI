/**
 * Protected Route Component - Requires authentication
 */
import { Navigate } from 'react-router-dom';
import { AuthService } from '../utils/auth';

function ProtectedRoute({ children }) {
    if (!AuthService.isAuthenticated()) {
        return <Navigate to="/login" replace />;
    }

    return children;
}

export default ProtectedRoute;
