/**
 * Analytics Page - Mastery tracking, recommendations, and progress stats
 */
import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { analytics } from '../api/client';

function AnalyticsPage() {
    const [weaknesses, setWeaknesses] = useState([]);
    const [mastery, setMastery] = useState([]);
    const [recommendations, setRecommendations] = useState(null);
    const [progress, setProgress] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadAnalytics();
    }, []);

    const loadAnalytics = async () => {
        try {
            const [weaknessRes, progressRes, masteryRes, recRes] = await Promise.all([
                analytics.getWeaknesses(),
                analytics.getProgress(),
                analytics.getMastery(),
                analytics.getRecommendations(),
            ]);
            setWeaknesses(weaknessRes.data);
            setProgress(progressRes.data);
            setMastery(masteryRes.data);
            setRecommendations(recRes.data);
        } catch (error) {
            console.error('Failed to load analytics:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <Layout>
                <div className="text-center py-12">
                    <p className="text-neutral-600">Loading analytics...</p>
                </div>
            </Layout>
        );
    }

    return (
        <Layout>
            <div>
                <h2 className="text-3xl font-bold mb-8">Your Analytics</h2>

                {/* Progress Stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div className="card bg-gradient-to-br from-blue-500 to-blue-600 text-white">
                        <p className="text-sm opacity-90 mb-1">Total Quizzes</p>
                        <p className="text-4xl font-bold">{progress?.total_quizzes || 0}</p>
                    </div>
                    <div className="card bg-gradient-to-br from-green-500 to-green-600 text-white">
                        <p className="text-sm opacity-90 mb-1">Average Score</p>
                        <p className="text-4xl font-bold">{Math.round(progress?.average_score || 0)}%</p>
                    </div>
                    <div className="card bg-gradient-to-br from-purple-500 to-purple-600 text-white">
                        <p className="text-sm opacity-90 mb-1">Total PDFs</p>
                        <p className="text-4xl font-bold">{progress?.total_pdfs || 0}</p>
                    </div>
                    <div className="card bg-gradient-to-br from-amber-500 to-amber-600 text-white">
                        <p className="text-sm opacity-90 mb-1">Concepts Mastered</p>
                        <p className="text-4xl font-bold">{progress?.mastered_concepts_count || 0}</p>
                    </div>
                </div>

                {/* Concept Mastery Profile */}
                <div className="card mb-8">
                    <h3 className="text-2xl font-semibold mb-6">Concept Mastery</h3>

                    {mastery.length === 0 ? (
                        <div className="text-center py-8 text-neutral-600">
                            <p>No mastery data yet.</p>
                            <p className="text-sm">Take quizzes to build your learner profile</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {mastery.map((item, idx) => (
                                <div key={idx} className="flex items-center gap-4">
                                    <span className="w-48 text-sm font-medium truncate" title={item.concept}>
                                        {item.concept}
                                    </span>
                                    <div className="flex-1 bg-neutral-200 rounded-full h-3">
                                        <div
                                            className={`h-3 rounded-full transition-all ${
                                                item.mastery_score >= 0.8
                                                    ? 'bg-green-500'
                                                    : item.mastery_score >= 0.4
                                                    ? 'bg-yellow-500'
                                                    : 'bg-red-500'
                                            }`}
                                            style={{ width: `${Math.max(Math.round(item.mastery_score * 100), 4)}%` }}
                                        />
                                    </div>
                                    <span className="text-sm text-neutral-600 w-12 text-right">
                                        {Math.round(item.mastery_score * 100)}%
                                    </span>
                                    <span className="text-xs text-neutral-400 w-20 text-right">
                                        {item.correct}R / {item.incorrect}W
                                    </span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Weak Concepts (legacy) */}
                <div className="card mb-8">
                    <h3 className="text-2xl font-semibold mb-6">Concepts to Review</h3>

                    {weaknesses.length === 0 ? (
                        <div className="text-center py-8 text-neutral-600">
                            <p>No weak concepts identified yet!</p>
                            <p className="text-sm">Take some quizzes to get personalized recommendations</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {weaknesses.map((weakness, idx) => (
                                <div
                                    key={idx}
                                    className="flex items-center justify-between p-4 bg-neutral-50 rounded-lg"
                                >
                                    <div className="flex-1">
                                        <p className="font-semibold text-lg">{weakness.concept}</p>
                                        <p className="text-sm text-neutral-600">
                                            Last incorrect: {new Date(weakness.last_incorrect).toLocaleDateString()}
                                        </p>
                                    </div>
                                    <div className="text-right">
                                        <div className="inline-flex items-center gap-2 px-4 py-2 bg-error/10 rounded-full">
                                            <span className="text-error font-semibold">{weakness.frequency}</span>
                                            <span className="text-error text-sm">times wrong</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Study Recommendations */}
                {recommendations && (recommendations.priority_review?.length > 0 || recommendations.strong_concepts?.length > 0) && (
                    <div className="card bg-primary/5 border-2 border-primary">
                        <h4 className="font-semibold text-primary mb-3">Study Recommendations</h4>
                        <p className="text-neutral-700 mb-4">{recommendations.suggestion}</p>

                        {recommendations.priority_review?.length > 0 && (
                            <div className="mb-3">
                                <p className="text-sm font-semibold text-neutral-600 mb-1">Priority Review:</p>
                                <div className="flex flex-wrap gap-2">
                                    {recommendations.priority_review.map((c, i) => (
                                        <span key={i} className="px-3 py-1 rounded-full bg-red-100 text-red-700 text-sm">
                                            {c}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {recommendations.strong_concepts?.length > 0 && (
                            <div>
                                <p className="text-sm font-semibold text-neutral-600 mb-1">Strong Concepts:</p>
                                <div className="flex flex-wrap gap-2">
                                    {recommendations.strong_concepts.map((c, i) => (
                                        <span key={i} className="px-3 py-1 rounded-full bg-green-100 text-green-700 text-sm">
                                            {c}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </Layout>
    );
}

export default AnalyticsPage;
