/**
 * EvaluationPage — Research evaluation dashboard with charts and tables
 * Shows: model comparison, baseline vs adaptive, document stats, ablation results
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { evaluation, pdf as pdfApi } from '../api/client';

const COLORS = ['#6366f1', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#ec4899'];

function BarChart({ data, labelKey, valueKey, title, color = '#6366f1' }) {
    const max = Math.max(...data.map(d => d[valueKey]), 1);
    return (
        <div className="space-y-2">
            <h4 className="text-sm font-semibold text-gray-500 uppercase">{title}</h4>
            {data.map((d, i) => (
                <div key={i} className="flex items-center gap-3">
                    <span className="text-xs w-40 truncate text-right text-gray-600">{d[labelKey]}</span>
                    <div className="flex-1 bg-gray-100 rounded-full h-5 overflow-hidden">
                        <div
                            className="h-full rounded-full transition-all duration-500"
                            style={{
                                width: `${(d[valueKey] / max) * 100}%`,
                                backgroundColor: COLORS[i % COLORS.length],
                            }}
                        />
                    </div>
                    <span className="text-sm font-mono w-16 text-right">{d[valueKey]}</span>
                </div>
            ))}
        </div>
    );
}

function StatCard({ label, value, sub, color = 'indigo' }) {
    const colors = {
        indigo: 'bg-indigo-50 text-indigo-700',
        green: 'bg-green-50 text-green-700',
        amber: 'bg-amber-50 text-amber-700',
        red: 'bg-red-50 text-red-700',
        purple: 'bg-purple-50 text-purple-700',
    };
    return (
        <div className={`rounded-xl p-4 ${colors[color]}`}>
            <p className="text-xs font-medium opacity-70 uppercase">{label}</p>
            <p className="text-2xl font-bold mt-1">{value}</p>
            {sub && <p className="text-xs mt-1 opacity-60">{sub}</p>}
        </div>
    );
}

export default function EvaluationPage() {
    const navigate = useNavigate();
    const [summary, setSummary] = useState(null);
    const [modelComp, setModelComp] = useState([]);
    const [docStats, setDocStats] = useState([]);
    const [progression, setProgression] = useState(null);
    const [ablationResults, setAblationResults] = useState([]);
    const [pdfs, setPdfs] = useState([]);
    const [selectedPdf, setSelectedPdf] = useState('');
    const [ablationRunning, setAblationRunning] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadAll();
    }, []);

    async function loadAll() {
        setLoading(true);
        try {
            const [sumRes, modelRes, docRes, progRes, pdfRes] = await Promise.all([
                evaluation.getSummary().catch(() => ({ data: null })),
                evaluation.getModelComparison().catch(() => ({ data: [] })),
                evaluation.getDocumentStats().catch(() => ({ data: [] })),
                evaluation.getMasteryProgression().catch(() => ({ data: null })),
                pdfApi.list().catch(() => ({ data: [] })),
            ]);
            setSummary(sumRes.data);
            setModelComp(modelRes.data || []);
            setDocStats(docRes.data || []);
            setProgression(progRes.data);
            const pdfList = pdfRes.data?.pdfs || pdfRes.data || [];
            setPdfs(pdfList);
            if (pdfList.length > 0) setSelectedPdf(pdfList[0].id);
        } catch (e) {
            console.error('Failed to load evaluation data', e);
        }
        setLoading(false);
    }

    async function runAblation() {
        if (!selectedPdf) return;
        setAblationRunning(true);
        try {
            const res = await evaluation.runAblation(selectedPdf);
            setAblationResults(res.data || []);
        } catch (e) {
            console.error('Ablation failed', e);
            alert('Ablation study failed — check console for details.');
        }
        setAblationRunning(false);
    }

    if (loading) {
        return (
            <Layout>
                <div className="flex items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
                </div>
            </Layout>
        );
    }

    return (
        <Layout>
            <div className="max-w-7xl mx-auto space-y-8">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">Evaluation Dashboard</h1>
                        <p className="text-gray-500 mt-1">Research metrics, model comparison, and ablation analysis</p>
                    </div>
                    <button
                        onClick={() => navigate('/analytics')}
                        className="text-sm text-indigo-600 hover:text-indigo-800"
                    >
                        &larr; Analytics
                    </button>
                </div>

                {/* Summary Cards */}
                {summary && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <StatCard label="Total Quizzes" value={summary.total_quizzes} color="indigo" />
                        <StatCard
                            label="Baseline Avg"
                            value={`${summary.baseline_avg_score}%`}
                            sub={`${summary.baseline_count} quizzes`}
                            color="amber"
                        />
                        <StatCard
                            label="Adaptive Avg"
                            value={`${summary.adaptive_avg_score}%`}
                            sub={`${summary.adaptive_count} quizzes`}
                            color="green"
                        />
                        <StatCard
                            label="Improvement"
                            value={`${summary.improvement_delta > 0 ? '+' : ''}${summary.improvement_delta}%`}
                            sub={`${summary.mastery_coverage} concepts tracked`}
                            color={summary.improvement_delta >= 0 ? 'green' : 'red'}
                        />
                    </div>
                )}

                {/* Model Comparison */}
                {modelComp.length > 0 && (
                    <div className="bg-white rounded-xl shadow p-6">
                        <h3 className="text-lg font-semibold mb-4">Model Comparison — Quiz Scores</h3>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b text-left text-gray-500">
                                        <th className="py-2 pr-4">Model</th>
                                        <th className="py-2 pr-4">Quizzes</th>
                                        <th className="py-2 pr-4">Avg Score</th>
                                        <th className="py-2 pr-4">Min</th>
                                        <th className="py-2">Max</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {modelComp.map((m, i) => (
                                        <tr key={i} className="border-b last:border-0">
                                            <td className="py-2 pr-4 font-mono text-xs">{m.model}</td>
                                            <td className="py-2 pr-4">{m.quiz_count}</td>
                                            <td className="py-2 pr-4 font-semibold">{m.avg_score}%</td>
                                            <td className="py-2 pr-4">{m.min_score}%</td>
                                            <td className="py-2">{m.max_score}%</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        <div className="mt-4">
                            <BarChart
                                data={modelComp}
                                labelKey="model"
                                valueKey="avg_score"
                                title="Average Score by Model"
                            />
                        </div>
                    </div>
                )}

                {/* Mastery Progression */}
                {progression && (progression.baseline.length > 0 || progression.adaptive.length > 0) && (
                    <div className="bg-white rounded-xl shadow p-6">
                        <h3 className="text-lg font-semibold mb-4">Learning Curve — Score Progression</h3>
                        <div className="grid md:grid-cols-2 gap-6">
                            <div>
                                <h4 className="text-sm font-medium text-gray-500 mb-2">Baseline Mode</h4>
                                <div className="space-y-1">
                                    {progression.baseline.map((q, i) => (
                                        <div key={i} className="flex items-center gap-2">
                                            <span className="text-xs text-gray-400 w-8">#{i + 1}</span>
                                            <div className="flex-1 bg-gray-100 rounded-full h-4 overflow-hidden">
                                                <div
                                                    className="h-full bg-amber-400 rounded-full"
                                                    style={{ width: `${q.score}%` }}
                                                />
                                            </div>
                                            <span className="text-xs font-mono w-12 text-right">{q.score}%</span>
                                        </div>
                                    ))}
                                    {progression.baseline.length === 0 && (
                                        <p className="text-sm text-gray-400">No baseline quizzes yet</p>
                                    )}
                                </div>
                            </div>
                            <div>
                                <h4 className="text-sm font-medium text-gray-500 mb-2">Adaptive Mode</h4>
                                <div className="space-y-1">
                                    {progression.adaptive.map((q, i) => (
                                        <div key={i} className="flex items-center gap-2">
                                            <span className="text-xs text-gray-400 w-8">#{i + 1}</span>
                                            <div className="flex-1 bg-gray-100 rounded-full h-4 overflow-hidden">
                                                <div
                                                    className="h-full bg-green-500 rounded-full"
                                                    style={{ width: `${q.score}%` }}
                                                />
                                            </div>
                                            <span className="text-xs font-mono w-12 text-right">{q.score}%</span>
                                        </div>
                                    ))}
                                    {progression.adaptive.length === 0 && (
                                        <p className="text-sm text-gray-400">No adaptive quizzes yet</p>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Document Statistics */}
                {docStats.length > 0 && (
                    <div className="bg-white rounded-xl shadow p-6">
                        <h3 className="text-lg font-semibold mb-4">Document & Chunk Statistics</h3>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b text-left text-gray-500">
                                        <th className="py-2 pr-4">Document</th>
                                        <th className="py-2 pr-4">Size (KB)</th>
                                        <th className="py-2 pr-4">Chunks</th>
                                        <th className="py-2">Avg Chunk (words)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {docStats.map((d, i) => (
                                        <tr key={i} className="border-b last:border-0">
                                            <td className="py-2 pr-4 truncate max-w-[200px]">{d.filename}</td>
                                            <td className="py-2 pr-4">{d.file_size_kb}</td>
                                            <td className="py-2 pr-4">{d.total_chunks}</td>
                                            <td className="py-2">{d.avg_chunk_length ?? '—'}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        {docStats[0]?.chunk_lengths?.length > 0 && (
                            <div className="mt-4">
                                <h4 className="text-sm font-semibold text-gray-500 uppercase mb-2">
                                    Chunk Length Distribution — {docStats[0].filename}
                                </h4>
                                <div className="flex items-end gap-px h-32">
                                    {docStats[0].chunk_lengths.map((len, i) => {
                                        const maxLen = Math.max(...docStats[0].chunk_lengths);
                                        return (
                                            <div
                                                key={i}
                                                className="bg-indigo-400 hover:bg-indigo-600 rounded-t transition-colors"
                                                style={{
                                                    height: `${(len / maxLen) * 100}%`,
                                                    width: `${Math.max(100 / docStats[0].chunk_lengths.length, 3)}%`,
                                                    minWidth: '3px',
                                                }}
                                                title={`Chunk ${i + 1}: ${len} words`}
                                            />
                                        );
                                    })}
                                </div>
                                <div className="flex justify-between text-xs text-gray-400 mt-1">
                                    <span>Chunk 1</span>
                                    <span>Chunk {docStats[0].chunk_lengths.length}</span>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Ablation Study */}
                <div className="bg-white rounded-xl shadow p-6">
                    <h3 className="text-lg font-semibold mb-4">Ablation Study</h3>
                    <p className="text-sm text-gray-500 mb-4">
                        Test quiz generation across different models, temperatures, and difficulty levels.
                    </p>
                    <div className="flex items-end gap-4 mb-4">
                        <div>
                            <label className="block text-xs font-medium text-gray-500 mb-1">Select PDF</label>
                            <select
                                value={selectedPdf}
                                onChange={(e) => setSelectedPdf(e.target.value)}
                                className="border rounded-lg px-3 py-2 text-sm"
                            >
                                {pdfs.map((p) => (
                                    <option key={p.id} value={p.id}>{p.filename}</option>
                                ))}
                            </select>
                        </div>
                        <button
                            onClick={runAblation}
                            disabled={ablationRunning || !selectedPdf}
                            className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50"
                        >
                            {ablationRunning ? 'Running...' : 'Run Ablation'}
                        </button>
                    </div>
                    {ablationRunning && (
                        <div className="flex items-center gap-2 text-sm text-amber-600 mb-4">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-amber-600" />
                            Running experiments across models, temperatures, and difficulties...
                            This may take a few minutes due to API rate limits.
                        </div>
                    )}
                    {ablationResults.length > 0 && (
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b text-left text-gray-500">
                                        <th className="py-2 pr-3">Model</th>
                                        <th className="py-2 pr-3">Temp</th>
                                        <th className="py-2 pr-3">Difficulty</th>
                                        <th className="py-2 pr-3">Questions</th>
                                        <th className="py-2 pr-3">Avg Options</th>
                                        <th className="py-2 pr-3">Explanations</th>
                                        <th className="py-2">Time (ms)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {ablationResults.map((r, i) => (
                                        <tr key={i} className="border-b last:border-0">
                                            <td className="py-2 pr-3 font-mono text-xs">{r.model}</td>
                                            <td className="py-2 pr-3">{r.temperature}</td>
                                            <td className="py-2 pr-3 capitalize">{r.difficulty}</td>
                                            <td className="py-2 pr-3 font-semibold">{r.questions_generated}</td>
                                            <td className="py-2 pr-3">{r.avg_options}</td>
                                            <td className="py-2 pr-3">
                                                {r.has_explanations ? (
                                                    <span className="text-green-600">Yes</span>
                                                ) : (
                                                    <span className="text-red-500">No</span>
                                                )}
                                            </td>
                                            <td className="py-2 font-mono">{r.generation_time_ms}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </Layout>
    );
}
