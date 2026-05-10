import React, { useState } from 'react';

const FileUpload = ({ onUploadSuccess }) => {
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [fileName, setFileName] = useState('');

    const handleDragEnter = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);

        const files = e.dataTransfer.files;
        if (files && files[0]) {
            handleFileUpload(files[0]);
        }
    };

    const handleFileInput = (e) => {
        const files = e.target.files;
        if (files && files[0]) {
            handleFileUpload(files[0]);
        }
    };

    const handleFileUpload = async (file) => {
        // Validate file type
        if (!file.name.endsWith('.pdf')) {
            alert('Please upload a PDF file');
            return;
        }

        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert('File size must be less than 10MB');
            return;
        }

        setFileName(file.name);
        setIsUploading(true);
        setUploadProgress(0);

        try {
            const formData = new FormData();
            formData.append('file', file);

            // Simulate progress (in production, use axios onUploadProgress)
            const progressInterval = setInterval(() => {
                setUploadProgress(prev => {
                    if (prev >= 90) {
                        clearInterval(progressInterval);
                        return 90;
                    }
                    return prev + 10;
                });
            }, 200);

            const response = await fetch('http://localhost:8000/api/upload', {
                method: 'POST',
                body: formData,
            });

            clearInterval(progressInterval);
            setUploadProgress(100);

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            const data = await response.json();

            // Wait a bit to show 100% progress
            setTimeout(() => {
                onUploadSuccess(data.file_id, file.name);
                setIsUploading(false);
                setUploadProgress(0);
            }, 500);

        } catch (error) {
            console.error('Upload error:', error);
            alert('Failed to upload file. Please try again.');
            setIsUploading(false);
            setUploadProgress(0);
        }
    };

    return (
        <div className="w-full max-w-2xl mx-auto animate-slideUp">
            <div
                className={`
          card border-2 border-dashed transition-all duration-200 cursor-pointer
          ${isDragging ? 'border-primary bg-primary/5 scale-105' : 'border-neutral-300'}
          ${isUploading ? 'pointer-events-none opacity-75' : 'hover:border-primary hover:bg-primary/5'}
        `}
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileInput}
                    className="hidden"
                    id="file-upload"
                    disabled={isUploading}
                />

                <label htmlFor="file-upload" className="cursor-pointer block text-center py-8">
                    {!isUploading ? (
                        <>
                            <div className="mb-4">
                                <svg
                                    className="mx-auto h-16 w-16 text-primary"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                                    />
                                </svg>
                            </div>
                            <h3 className="text-xl font-semibold text-neutral-800 mb-2">
                                Upload Your PDF
                            </h3>
                            <p className="text-neutral-600 mb-4">
                                Drag and drop your study material here, or click to browse
                            </p>
                            <p className="text-sm text-neutral-500">
                                PDF files only, max 10MB
                            </p>
                        </>
                    ) : (
                        <div className="py-4">
                            <div className="mb-4">
                                <svg
                                    className="mx-auto h-16 w-16 text-primary animate-pulse"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                                    />
                                </svg>
                            </div>
                            <h3 className="text-xl font-semibold text-neutral-800 mb-2">
                                Uploading {fileName}...
                            </h3>
                            <div className="w-full max-w-md mx-auto mt-4">
                                <div className="bg-neutral-200 rounded-full h-3 overflow-hidden">
                                    <div
                                        className="bg-gradient-to-r from-primary to-primary-light h-full rounded-full transition-all duration-300 ease-out"
                                        style={{ width: `${uploadProgress}%` }}
                                    />
                                </div>
                                <p className="text-sm text-neutral-600 mt-2">
                                    {uploadProgress}% complete
                                </p>
                            </div>
                        </div>
                    )}
                </label>
            </div>
        </div>
    );
};

export default FileUpload;
