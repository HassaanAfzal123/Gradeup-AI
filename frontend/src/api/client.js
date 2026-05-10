/**
 * API Client with Axios - Handles all backend communication
 */
import axios from 'axios';

// Dev: vite .env.development → http://localhost:8000/api
// Docker prod build: /api (proxied by nginx to backend)
const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Create axios instance
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Handle 401 errors (redirect to login)
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Auth API
export const auth = {
    register: (email, password) =>
        apiClient.post('/auth/register', { email, password }),

    login: (email, password) =>
        apiClient.post('/auth/login', { email, password }),

    getMe: () =>
        apiClient.get('/auth/me'),
};

// PDF API
export const pdf = {
    upload: (file) => {
        const formData = new FormData();
        formData.append('file', file);
        return apiClient.post('/pdf/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
    },

    list: () =>
        apiClient.get('/pdf/list'),

    summarize: (pdfId) =>
        apiClient.post(`/pdf/summarize/${pdfId}`),

    delete: (pdfId) =>
        apiClient.delete(`/pdf/${pdfId}`),
};

// Chat API
export const chat = {
    ask: (pdfId, question, adaptive = false) =>
        apiClient.post('/chat/ask', { pdf_id: pdfId, question, adaptive }),

    getHistory: (pdfId) =>
        apiClient.get(`/chat/history/${pdfId}`),

    clearChat: (chatId) =>
        apiClient.delete(`/chat/${chatId}`),
};

// Quiz API
export const quiz = {
    generate: (pdfId, topic, numQuestions = 5, difficulty = 'medium', adaptive = false, modelName = null) =>
        apiClient.post('/quiz/generate', {
            pdf_id: pdfId,
            topic,
            num_questions: numQuestions,
            difficulty,
            adaptive,
            model_name: modelName || undefined,
        }),

    submit: (quizId, userAnswers) =>
        apiClient.post('/quiz/submit', {
            quiz_id: quizId,
            user_answers: userAnswers,
        }),

    getHistory: () =>
        apiClient.get('/quiz/history'),
};

// Analytics API
export const analytics = {
    getWeaknesses: () =>
        apiClient.get('/analytics/weaknesses'),

    getProgress: () =>
        apiClient.get('/analytics/progress'),

    getMastery: () =>
        apiClient.get('/analytics/mastery'),

    getRecommendations: () =>
        apiClient.get('/analytics/recommendations'),
};

// Evaluation API (research paper metrics)
export const evaluation = {
    getSummary: () =>
        apiClient.get('/evaluation/summary'),

    getQuizScores: () =>
        apiClient.get('/evaluation/quiz-scores'),

    getModelComparison: () =>
        apiClient.get('/evaluation/model-comparison'),

    getDocumentStats: () =>
        apiClient.get('/evaluation/document-stats'),

    getMasteryProgression: () =>
        apiClient.get('/evaluation/mastery-progression'),

    runAblation: (pdfId, topic = '', models = [], temperatures = [0.3, 0.5, 0.7, 0.9]) =>
        apiClient.post('/evaluation/ablation', {
            pdf_id: pdfId,
            topic,
            num_questions: 5,
            models,
            temperatures,
            difficulties: ['easy', 'medium', 'hard'],
        }),
};

// Models API
export const models = {
    list: () => apiClient.get('/models'),
};

export default apiClient;
