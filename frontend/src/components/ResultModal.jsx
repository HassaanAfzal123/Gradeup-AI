import React from 'react';

const ResultModal = ({ isOpen, result, onClose }) => {
    if (!isOpen || !result) return null;

    const { correct, citation, explanation, correct_answer } = result;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fadeIn">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/50 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="relative bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto animate-slideUp">
                {/* Header */}
                <div
                    className={`
            px-6 py-4 rounded-t-2xl
            ${correct ? 'bg-gradient-to-r from-success to-success-dark' : 'bg-gradient-to-r from-error to-error-dark'}
          `}
                >
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            {correct ? (
                                <svg
                                    className="w-8 h-8 text-white"
                                    fill="currentColor"
                                    viewBox="0 0 20 20"
                                >
                                    <path
                                        fillRule="evenodd"
                                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                        clipRule="evenodd"
                                    />
                                </svg>
                            ) : (
                                <svg
                                    className="w-8 h-8 text-white"
                                    fill="currentColor"
                                    viewBox="0 0 20 20"
                                >
                                    <path
                                        fillRule="evenodd"
                                        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                                        clipRule="evenodd"
                                    />
                                </svg>
                            )}
                            <h2 className="text-2xl font-bold text-white">
                                {correct ? '🎉 Correct!' : '❌ Incorrect'}
                            </h2>
                        </div>
                        <button
                            onClick={onClose}
                            className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
                        >
                            <svg
                                className="w-6 h-6"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M6 18L18 6M6 6l12 12"
                                />
                            </svg>
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {/* Explanation */}
                    <div>
                        <h3 className="text-sm font-semibold text-neutral-500 uppercase tracking-wide mb-2">
                            Explanation
                        </h3>
                        <p className="text-neutral-800 text-lg leading-relaxed">
                            {explanation}
                        </p>
                    </div>

                    {!correct && (
                        <div className="bg-neutral-50 rounded-xl p-4">
                            <h3 className="text-sm font-semibold text-neutral-500 uppercase tracking-wide mb-2">
                                Correct Answer
                            </h3>
                            <p className="text-neutral-800 font-medium">
                                {correct_answer}
                            </p>
                        </div>
                    )}

                    {/* Citation */}
                    {citation && (
                        <div className="bg-primary/5 border-l-4 border-primary rounded-r-xl p-4">
                            <h3 className="text-sm font-semibold text-primary uppercase tracking-wide mb-2 flex items-center">
                                <svg
                                    className="w-4 h-4 mr-2"
                                    fill="currentColor"
                                    viewBox="0 0 20 20"
                                >
                                    <path
                                        fillRule="evenodd"
                                        d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                                        clipRule="evenodd"
                                    />
                                </svg>
                                Citation from your document
                            </h3>
                            <p className="text-neutral-700 italic leading-relaxed">
                                "{citation}"
                            </p>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="px-6 py-4 bg-neutral-50 rounded-b-2xl">
                    <button
                        onClick={onClose}
                        className="btn-primary w-full"
                    >
                        Continue
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ResultModal;
