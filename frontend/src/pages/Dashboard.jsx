/**
 * Dashboard Page - Home page with stats and quick actions
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { pdf, quiz, analytics } from '../api/client';

function Dashboard() {
    const [stats, setStats] = useState({
        totalPdfs: 0,
        totalQuizzes: 0,
        averageScore: 0,
        weakConcepts: 0,
    });
    const [recentPdfs, setRecentPdfs] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            const [pdfsRes, progressRes] = await Promise.all([
                pdf.list(),
                analytics.getProgress(),
            ]);

            setRecentPdfs(pdfsRes.data.slice(0, 3));
            setStats({
                totalPdfs: progressRes.data.total_pdfs,
                totalQuizzes: progressRes.data.total_quizzes,
                averageScore: progressRes.data.average_score,
                weakConcepts: progressRes.data.weak_concepts_count,
            });
        } catch (error) {
            console.error('Failed to load dashboard:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Layout>
            <div className="animate-fadeIn">
                {/* Welcome Header */}
                <div className="mb-8">
                    <h2 className="text-3xl font-bold text-neutral-800 mb-2">Welcome Back!</h2>
                    <p className="text-neutral-600">Here's your learning progress</p>
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <StatsCard
                        title="Total PDFs"
                        value={stats.totalPdfs}
                        icon="📚"
                        color="bg-blue-500"
                    />
                    <StatsCard
                        title="Quizzes Taken"
                        value={stats.totalQuizzes}
                        icon="📝"
                        color="bg-green-500"
                    />
                    <StatsCard
                        title="Avg Score"
                        value={`${Math.round(stats.averageScore)}%`}
                        icon="⭐"
                        color="bg-yellow-500"
                    />
                    <StatsCard
                        title="Weak Concepts"
                        value={stats.weakConcepts}
                        icon="💡"
                        color="bg-red-500"
                    />
                </div>

                {/* Quick Actions */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <Link to="/pdfs" className="card hover:shadow-lg transition-all group">
                        <div className="text-4xl mb-4">📄</div>
                        <h3 className="text-xl font-semibold mb-2 group-hover:text-primary">Upload PDF</h3>
                        <p className="text-neutral-600">Upload new study material</p>
                    </Link>

                    <Link to="/quiz" className="card hover:shadow-lg transition-all group">
                        <div className="text-4xl mb-4">🎯</div>
                        <h3 className="text-xl font-semibold mb-2 group-hover:text-primary">Take Quiz</h3>
                        <p className="text-neutral-600">Test your knowledge</p>
                    </Link>

                    <Link to="/analytics" className="card hover:shadow-lg transition-all group">
                        <div className="text-4xl mb-4">📊</div>
                        <h3 className="text-xl font-semibold mb-2 group-hover:text-primary">View Analytics</h3>
                        <p className="text-neutral-600">Track your progress</p>
                    </Link>
                </div>

                {/* Recent PDFs */}
                {recentPdfs.length > 0 && (
                    <div className="card">
                        <h3 className="text-xl font-semibold mb-4">Recent PDFs</h3>
                        <div className="space-y-3">
                            {recentPdfs.map((pdfItem) => (
                                <div key={pdfItem.id} className="flex items-center justify-between p-3 bg-neutral-50 rounded-lg">
                                    <div>
                                        <p className="font-medium">{pdfItem.filename}</p>
                                        <p className="text-sm text-neutral-600">
                                            {new Date(pdfItem.upload_date).toLocaleDateString()}
                                        </p>
                                    </div>
                                    <Link
                                        to={`/chat/${pdfItem.id}`}
                                        className="btn-primary text-sm py-2 px-4"
                                    >
                                        Chat
                                    </Link>
                                </div>
                            ))}
                        </div>
                        <Link to="/pdfs" className="text-primary hover:underline mt-4 inline-block">
                            View all PDFs →
                        </Link>
                    </div>
                )}
            </div>
        </Layout>
    );
}

function StatsCard({ title, value, icon, color }) {
    return (
        <div className="card">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-neutral-600 text-sm mb-1">{title}</p>
                    <p className="text-3xl font-bold">{value}</p>
                </div>
                <div className={`${color} w-12 h-12 rounded-lg flex items-center justify-center text-2xl`}>
                    {icon}
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
