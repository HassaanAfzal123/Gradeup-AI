/**
 * PDF Library Page - Upload, view, and manage PDFs
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { pdf } from '../api/client';

function PDFLibrary() {
    const [pdfs, setPdfs] = useState([]);
    const [uploading, setUploading] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadPdfs();
    }, []);

    const loadPdfs = async () => {
        try {
            const response = await pdf.list();
            setPdfs(response.data);
        } catch (error) {
            console.error('Failed to load PDFs:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        if (!file.name.endsWith('.pdf')) {
            alert('Only PDF files are allowed');
            return;
        }

        setUploading(true);
        try {
            await pdf.upload(file);
            await loadPdfs();
            alert('PDF uploaded and indexed successfully!');
        } catch (error) {
            alert('Upload failed: ' + (error.response?.data?.detail || error.message));
        } finally {
            setUploading(false);
            e.target.value = '';
        }
    };

    const handleDelete = async (pdfId, filename) => {
        if (!confirm(`Delete "${filename}"?`)) return;

        try {
            await pdf.delete(pdfId);
            await loadPdfs();
        } catch (error) {
            alert('Delete failed: ' + error.message);
        }
    };

    return (
        <Layout>
            <div className="animate-fadeIn">
                {/* Header */}
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h2 className="text-3xl font-bold text-neutral-800 mb-2">My PDFs</h2>
                        <p className="text-neutral-600">Manage your study materials</p>
                    </div>

                    {/* Upload Button */}
                    <label className={`btn-primary cursor-pointer ${uploading ? 'opacity-50' : ''}`}>
                        <input
                            type="file"
                            accept=".pdf"
                            onChange={handleUpload}
                            disabled={uploading}
                            className="hidden"
                        />
                        {uploading ? 'Uploading...' : '📄 Upload PDF'}
                    </label>
                </div>

                {/* PDF Grid */}
                {loading ? (
                    <div className="text-center py-12">
                        <div className="text-4xl mb-4">⏳</div>
                        <p className="text-neutral-600">Loading PDFs...</p>
                    </div>
                ) : pdfs.length === 0 ? (
                    <div className="text-center py-12 card">
                        <div className="text-6xl mb-4">📚</div>
                        <h3 className="text-xl font-semibold mb-2">No PDFs yet</h3>
                        <p className="text-neutral-600 mb-4">Upload your first PDF to get started</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {pdfs.map((pdfItem) => (
                            <div key={pdfItem.id} className="card hover:shadow-lg transition-all">
                                <div className="text-4xl mb-4">📄</div>
                                <h3 className="font-semibold text-lg mb-2 truncate">{pdfItem.filename}</h3>
                                <p className="text-sm text-neutral-600 mb-1">
                                    {pdfItem.total_chunks} chunks
                                </p>
                                <p className="text-sm text-neutral-600 mb-4">
                                    {new Date(pdfItem.upload_date).toLocaleDateString()}
                                </p>

                                <div className="flex gap-2">
                                    <Link
                                        to={`/chat/${pdfItem.id}`}
                                        className="btn-primary flex-1 text-center text-sm py-2"
                                    >
                                        💬 Chat
                                    </Link>
                                    <Link
                                        to={`/quiz/${pdfItem.id}`}
                                        className="btn-secondary flex-1 text-center text-sm py-2"
                                    >
                                        📝 Quiz
                                    </Link>
                                </div>

                                <button
                                    onClick={() => handleDelete(pdfItem.id, pdfItem.filename)}
                                    className="mt-2 w-full text-error text-sm py-2 hover:bg-error/10 rounded-lg transition-colors"
                                >
                                    🗑️ Delete
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </Layout>
    );
}

export default PDFLibrary;
