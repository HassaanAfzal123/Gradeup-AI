/**
 * Authentication utilities
 */
import { jwtDecode } from 'jwt-decode';

export const AuthService = {
    // Store tokens and user data
    setAuth(accessToken, refreshToken, user) {
        localStorage.setItem('access_token', accessToken);
        if (refreshToken) {
            localStorage.setItem('refresh_token', refreshToken);
        }
        localStorage.setItem('user', JSON.stringify(user));
    },

    // Get current user
    getUser() {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    },

    // Get token
    getToken() {
        return localStorage.getItem('access_token');
    },

    // Check if user is authenticated
    isAuthenticated() {
        const token = this.getToken();
        if (!token) return false;

        try {
            const decoded = jwtDecode(token);
            return decoded.exp * 1000 > Date.now();
        } catch {
            return false;
        }
    },

    // Logout
    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    },
};
