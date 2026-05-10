/**
 * Main Layout with Navigation
 */
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { AuthService } from '../utils/auth';

function Layout({ children }) {
    const navigate = useNavigate();
    const location = useLocation();
    const user = AuthService.getUser();

    const handleLogout = () => {
        AuthService.logout();
        navigate('/login');
    };

    const navItems = [
        { path: '/dashboard', label: 'Dashboard', icon: '🏠' },
        { path: '/pdfs', label: 'My PDFs', icon: '📚' },
        { path: '/analytics', label: 'Analytics', icon: '📊' },
        { path: '/evaluation', label: 'Evaluation', icon: '🔬' },
    ];

    return (
        <div className="min-h-screen bg-neutral-50">
            {/* Top Navigation */}
            <nav className="bg-white shadow-sm border-b border-neutral-200">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        {/* Logo */}
                        <div className="flex items-center">
                            <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-primary-dark bg-clip-text text-transparent">
                                Gradeup AI
                            </h1>
                        </div>

                        {/* Nav Links */}
                        <div className="flex items-center space-x-4">
                            {navItems.map((item) => (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${location.pathname === item.path
                                            ? 'bg-primary text-white'
                                            : 'text-neutral-700 hover:bg-neutral-100'
                                        }`}
                                >
                                    <span className="mr-2">{item.icon}</span>
                                    {item.label}
                                </Link>
                            ))}

                            {/* User Menu */}
                            <div className="flex items-center space-x-3 ml-4 pl-4 border-l border-neutral-200">
                                <span className="text-sm text-neutral-600">{user?.email}</span>
                                <button
                                    onClick={handleLogout}
                                    className="btn-secondary text-sm py-2 px-4"
                                >
                                    Logout
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {children}
            </main>
        </div>
    );
}

export default Layout;
