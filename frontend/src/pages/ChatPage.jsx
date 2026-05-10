/**
 * Chat Page - Weakness-aware RAG Q&A with PDF
 */
import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { chat, pdf } from '../api/client';

function ChatPage() {
    const { pdfId } = useParams();
    const [messages, setMessages] = useState([]);
    const [question, setQuestion] = useState('');
    const [loading, setLoading] = useState(false);
    const [pdfInfo, setPdfInfo] = useState(null);
    const [adaptive, setAdaptive] = useState(false);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        loadChatHistory();
        loadPdfInfo();
    }, [pdfId]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const loadChatHistory = async () => {
        try {
            const response = await chat.getHistory(pdfId);
            setMessages(response.data || []);
        } catch (error) {
            console.error('Failed to load chat history:', error);
        }
    };

    const loadPdfInfo = async () => {
        try {
            const response = await pdf.list();
            const foundPdf = response.data.find((p) => p.id === pdfId);
            setPdfInfo(foundPdf);
        } catch (error) {
            console.error('Failed to load PDF info:', error);
        }
    };

    const handleAsk = async (e) => {
        e.preventDefault();
        if (!question.trim() || loading) return;

        const userMessage = { role: 'user', content: question, timestamp: new Date().toISOString() };
        setMessages((prev) => [...prev, userMessage]);
        setQuestion('');
        setLoading(true);

        try {
            const response = await chat.ask(pdfId, question, adaptive);
            const assistantMessage = {
                role: 'assistant',
                content: response.data.answer,
                sources: response.data.sources,
                timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, assistantMessage]);
        } catch (error) {
            const errorMessage = {
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.',
                timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Layout>
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="mb-6">
                    <Link to="/pdfs" className="text-primary hover:underline mb-2 inline-block">
                        &larr; Back to PDFs
                    </Link>
                    <div className="flex items-center justify-between">
                        <h2 className="text-2xl font-bold">Chat with {pdfInfo?.filename || 'PDF'}</h2>
                        <button
                            onClick={() => setAdaptive(!adaptive)}
                            className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                                adaptive
                                    ? 'bg-primary text-white'
                                    : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
                            }`}
                        >
                            <span className={`inline-block w-2 h-2 rounded-full ${adaptive ? 'bg-white' : 'bg-neutral-400'}`} />
                            {adaptive ? 'Adaptive On' : 'Adaptive Off'}
                        </button>
                    </div>
                    {adaptive && (
                        <p className="text-xs text-primary mt-1">
                            Answers will be tailored to your weak concepts
                        </p>
                    )}
                </div>

                {/* Chat Container */}
                <div className="card p-0 overflow-hidden" style={{ height: '600px' }}>
                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-6 space-y-4" style={{ height: 'calc(100% - 80px)' }}>
                        {messages.length === 0 ? (
                            <div className="text-center py-12 text-neutral-600">
                                <div className="text-4xl mb-4">💬</div>
                                <p>Ask a question about the PDF</p>
                            </div>
                        ) : (
                            messages.map((msg, idx) => (
                                <div
                                    key={idx}
                                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div
                                        className={`max-w-[70%] rounded-2xl px-4 py-3 ${msg.role === 'user'
                                                ? 'bg-primary text-white'
                                                : 'bg-neutral-100 text-neutral-800'
                                            }`}
                                    >
                                        <p className="whitespace-pre-wrap">{msg.content}</p>
                                        {msg.sources && msg.sources.length > 0 && (
                                            <div className="mt-2 pt-2 border-t border-neutral-300 text-xs opacity-75">
                                                📚 {msg.sources.length} source(s)
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))
                        )}
                        {loading && (
                            <div className="flex justify-start">
                                <div className="bg-neutral-100 rounded-2xl px-4 py-3">
                                    <div className="flex space-x-2">
                                        <div className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce"></div>
                                        <div className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                        <div className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <form onSubmit={handleAsk} className="p-4 border-t border-neutral-200">
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={question}
                                onChange={(e) => setQuestion(e.target.value)}
                                placeholder="Ask a question..."
                                className="flex-1 px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                                disabled={loading}
                            />
                            <button
                                type="submit"
                                disabled={loading || !question.trim()}
                                className="btn-primary px-6"
                            >
                                Send
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </Layout>
    );
}

export default ChatPage;
