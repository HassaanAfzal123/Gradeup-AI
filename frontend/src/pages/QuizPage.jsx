/**
 * Quiz Page - Generate and take quizzes with adaptive weakness targeting
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { quiz as quizApi, pdf, models as modelsApi } from '../api/client';

function QuizPage() {
    const { pdfId } = useParams();
    const navigate = useNavigate();
    const [pdfs, setPdfs] = useState([]);
    const [selectedPdf, setSelectedPdf] = useState(pdfId || '');
    const [topic, setTopic] = useState('');
    const [numQuestions, setNumQuestions] = useState(5);
    const [difficulty, setDifficulty] = useState('medium');
    const [adaptive, setAdaptive] = useState(false);
    const [availableModels, setAvailableModels] = useState([]);
    const [selectedModel, setSelectedModel] = useState('');
    const [quiz, setQuiz] = useState(null);
    const [userAnswers, setUserAnswers] = useState({});
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    useEffect(() => {
        loadPdfs();
        loadModels();
    }, []);

    const loadPdfs = async () => {
        try {
            const response = await pdf.list();
            setPdfs(response.data);
        } catch (error) {
            console.error('Failed to load PDFs:', error);
        }
    };

    const loadModels = async () => {
        try {
            const res = await modelsApi.list();
            setAvailableModels(res.data.available || []);
            setSelectedModel(res.data.default || '');
        } catch (e) {
            console.error('Failed to load models:', e);
        }
    };

    const handleGenerate = async (e) => {
        e.preventDefault();
        setLoading(true);
        setResult(null);

        try {
            const response = await quizApi.generate(selectedPdf, topic, numQuestions, difficulty, adaptive, selectedModel);
            setQuiz(response.data);
            setUserAnswers({});
        } catch (error) {
            alert('Failed to generate quiz: ' + (error.response?.data?.detail || error.message));
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async () => {
        setLoading(true);
        try {
            const response = await quizApi.submit(quiz.quiz_id, userAnswers);
            setResult(response.data);
        } catch (error) {
            alert('Failed to submit quiz: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    const handleAnswerSelect = (questionId, answer) => {
        setUserAnswers((prev) => ({
            ...prev,
            [questionId]: answer,
        }));
    };

    return (
        <Layout>
            <div className="max-w-4xl mx-auto">
                <h2 className="text-3xl font-bold mb-6">Quiz Generator</h2>

                {!quiz ? (
                    /* Quiz Generation Form */
                    <div className="card">
                        <form onSubmit={handleGenerate} className="space-y-4">
                            <div>
                                <label className="block text-sm font-semibold mb-2">Select PDF</label>
                                <select
                                    value={selectedPdf}
                                    onChange={(e) => setSelectedPdf(e.target.value)}
                                    required
                                    className="input-field"
                                >
                                    <option value="">Choose a PDF...</option>
                                    {pdfs.map((p) => (
                                        <option key={p.id} value={p.id}>
                                            {p.filename}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-semibold mb-2">
                                    Topic (Optional)
                                </label>
                                <input
                                    type="text"
                                    value={topic}
                                    onChange={(e) => setTopic(e.target.value)}
                                    className="input-field"
                                    placeholder="Leave empty to quiz on entire PDF content"
                                />
                                <p className="text-xs text-neutral-500 mt-1">
                                    💡 Specify a topic for focused questions, or leave empty to generate from entire PDF
                                </p>
                            </div>

                            <div>
                                <label className="block text-sm font-semibold mb-2">Difficulty Level</label>
                                <div className="grid grid-cols-3 gap-3">
                                    {['easy', 'medium', 'hard'].map((level) => (
                                        <button
                                            key={level}
                                            type="button"
                                            onClick={() => setDifficulty(level)}
                                            className={`p-4 rounded-xl border-2 transition-all ${difficulty === level
                                                ? 'border-primary bg-primary/10 shadow-md'
                                                : 'border-neutral-200 hover:border-primary/50'
                                                }`}
                                        >
                                            <span className="block font-semibold capitalize mb-1">{level}</span>
                                            <span className="text-xs text-neutral-600">
                                                {level === 'easy'
                                                    ? 'Straight from text'
                                                    : level === 'medium'
                                                        ? 'Needs understanding'
                                                        : 'Fully conceptual'}
                                            </span>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Model Selector */}
                            {availableModels.length > 0 && (
                                <div>
                                    <label className="block text-sm font-semibold mb-2">LLM Model</label>
                                    <select
                                        value={selectedModel}
                                        onChange={(e) => setSelectedModel(e.target.value)}
                                        className="input-field"
                                    >
                                        {availableModels.map((m) => (
                                            <option key={m} value={m}>{m}</option>
                                        ))}
                                    </select>
                                    <p className="text-xs text-neutral-500 mt-1">
                                        Choose a model to generate quizzes with — useful for comparing model quality
                                    </p>
                                </div>
                            )}

                            {/* Adaptive Mode Toggle */}
                            <div className="flex items-center justify-between p-4 rounded-xl border-2 border-neutral-200">
                                <div>
                                    <p className="font-semibold">Target My Weak Concepts</p>
                                    <p className="text-xs text-neutral-500">
                                        Biases questions toward concepts you've struggled with previously
                                    </p>
                                </div>
                                <button
                                    type="button"
                                    onClick={() => setAdaptive(!adaptive)}
                                    className={`relative inline-flex h-7 w-12 items-center rounded-full transition-colors ${
                                        adaptive ? 'bg-primary' : 'bg-neutral-300'
                                    }`}
                                >
                                    <span
                                        className={`inline-block h-5 w-5 transform rounded-full bg-white shadow transition-transform ${
                                            adaptive ? 'translate-x-6' : 'translate-x-1'
                                        }`}
                                    />
                                </button>
                            </div>

                            <div>
                                <div>
                                    <label className="block text-sm font-semibold mb-2">Number of Questions</label>
                                    <input
                                        type="number"
                                        min="1"
                                        max="20"
                                        value={numQuestions}
                                        onChange={(e) => setNumQuestions(parseInt(e.target.value))}
                                        className="input-field"
                                    />
                                    <p className="text-xs text-neutral-500 mt-1">
                                        💡 Use 20 questions for comprehensive coverage of entire document
                                    </p>
                                </div>
                            </div>

                            <button type="submit" disabled={loading} className="btn-primary w-full">
                                {loading ? 'Generating...' : '🎯 Generate Quiz'}
                            </button>
                        </form>
                    </div>
                ) : !result ? (
                    /* Quiz Questions */
                    <div className="space-y-6">
                        <div className="card bg-primary text-white">
                            <h3 className="text-xl font-bold mb-2">{quiz.topic}</h3>
                            <p>
                                {quiz.questions.length} questions • Difficulty:{' '}
                                <span className="capitalize">{difficulty}</span>
                                {quiz.adaptive && (
                                    <span className="ml-2 px-2 py-0.5 bg-white/20 rounded-full text-xs">
                                        Adaptive
                                    </span>
                                )}
                            </p>
                        </div>

                        {quiz.questions.map((q, idx) => (
                            <div key={q.id} className="card">
                                <p className="font-semibold mb-4">
                                    {idx + 1}. {q.question}
                                </p>
                                {q.concept && (
                                    <p className="text-xs text-neutral-500 mb-3">
                                        📌 Concept: {q.concept}
                                    </p>
                                )}
                                <div className="space-y-2">
                                    {q.options.map((option, optIdx) => (
                                        <label
                                            key={optIdx}
                                            className={`block p-3 border-2 rounded-lg cursor-pointer transition-all ${userAnswers[q.id] === option
                                                ? 'border-primary bg-primary/10'
                                                : 'border-neutral-200 hover:border-primary/50'
                                                }`}
                                        >
                                            <input
                                                type="radio"
                                                name={`question-${q.id}`}
                                                value={option}
                                                checked={userAnswers[q.id] === option}
                                                onChange={() => handleAnswerSelect(q.id, option)}
                                                className="mr-3"
                                            />
                                            {option}
                                        </label>
                                    ))}
                                </div>
                            </div>
                        ))}

                        <div className="flex gap-4">
                            <button onClick={() => setQuiz(null)} className="btn-secondary flex-1">
                                Cancel
                            </button>
                            <button
                                onClick={handleSubmit}
                                disabled={Object.keys(userAnswers).length !== quiz.questions.length || loading}
                                className="btn-primary flex-1"
                            >
                                {loading ? 'Submitting...' : 'Submit Quiz'}
                            </button>
                        </div>
                    </div>
                ) : (
                    /* Quiz Results */
                    <div className="space-y-6">
                        <div className={`card text-white ${result.score >= 70 ? 'bg-success' : 'bg-error'}`}>
                            <h3 className="text-3xl font-bold mb-2">{Math.round(result.score)}%</h3>
                            <p>
                                {result.correct_answers} / {result.total_questions} correct
                            </p>
                        </div>

                        {result.weak_concepts && result.weak_concepts.length > 0 && (
                            <div className="card">
                                <h4 className="font-semibold mb-3">Concepts to Review:</h4>
                                <div className="flex flex-wrap gap-2">
                                    {result.weak_concepts.map((concept, idx) => (
                                        <span key={idx} className="badge-pill bg-error/10 text-error">
                                            {concept}
                                        </span>
                                    ))}
                                </div>
                                <p className="text-sm text-neutral-600 mt-4">
                                    These topics were identified from your incorrect answers. Use
                                    &quot;Target My Weak Concepts&quot; on your next quiz!
                                </p>
                            </div>
                        )}

                        {result.mastery_updates && result.mastery_updates.length > 0 && (
                            <div className="card">
                                <h4 className="font-semibold mb-3">Mastery Updates:</h4>
                                <div className="space-y-2">
                                    {result.mastery_updates.map((m, idx) => (
                                        <div key={idx} className="flex items-center justify-between">
                                            <span className="text-sm font-medium">{m.concept}</span>
                                            <div className="flex items-center gap-2">
                                                <div className="w-24 bg-neutral-200 rounded-full h-2">
                                                    <div
                                                        className={`h-2 rounded-full ${
                                                            m.mastery_score >= 0.7
                                                                ? 'bg-green-500'
                                                                : m.mastery_score >= 0.4
                                                                ? 'bg-yellow-500'
                                                                : 'bg-red-500'
                                                        }`}
                                                        style={{ width: `${Math.round(m.mastery_score * 100)}%` }}
                                                    />
                                                </div>
                                                <span className="text-xs text-neutral-500 w-10 text-right">
                                                    {Math.round(m.mastery_score * 100)}%
                                                </span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        <button
                            onClick={() => {
                                setQuiz(null);
                                setResult(null);
                                setUserAnswers({});
                            }}
                            className="btn-primary w-full"
                        >
                            Take Another Quiz
                        </button>
                    </div>
                )}
            </div>
        </Layout>
    );
}

export default QuizPage;
