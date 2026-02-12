import React, { useState, useRef, useReducer } from 'react';
import ResultsGrid from './components/ResultsGrid';

// State Management Definition
const initialState = {
    status: 'idle', // idle, uploading, searching, success, error
    file: null,
    preview: null,
    results: null,
    latency: null,
    statusMessages: [],
    error: null,
};

function reducer(state, action) {
    switch (action.type) {
        case 'FILE_SELECTED':
            return {
                ...initialState,
                status: 'idle',
                file: action.payload.file,
                preview: action.payload.preview
            };
        case 'UPLOAD_START':
            // Keep preview and file, just update status
            return { ...state, status: 'searching', error: null, statusMessages: [] };
        case 'SEARCH_SUCCESS':
            return {
                ...state,
                status: 'success',
                results: {
                    visual_matches: action.payload.visual_matches
                    // Local matches removed
                },
                latency: action.payload.latency,
                statusMessages: action.payload.status_messages || []
            };
        case 'SEARCH_ERROR':
            return { ...state, status: 'error', error: action.payload };
        case 'RESET':
            return initialState;
        default:
            return state;
    }
}

function App() {
    const [state, dispatch] = useReducer(reducer, initialState);
    const fileInputRef = useRef(null);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            processFile(selectedFile);
        }
    };

    const processFile = (selectedFile) => {
        const previewUrl = URL.createObjectURL(selectedFile);
        dispatch({ type: 'FILE_SELECTED', payload: { file: selectedFile, preview: previewUrl } });
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        e.currentTarget.classList.add('active');
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        e.currentTarget.classList.remove('active');
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.currentTarget.classList.remove('active');
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile && droppedFile.type.startsWith('image/')) {
            processFile(droppedFile);
        } else {
            dispatch({ type: 'SEARCH_ERROR', payload: "Please upload a valid image file." });
        }
    };

    const handleSearch = async () => {
        if (!state.file) return;

        dispatch({ type: 'UPLOAD_START' });

        const formData = new FormData();
        formData.append('file', state.file);

        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.statusText}`);
            }

            const data = await response.json();
            dispatch({ type: 'SEARCH_SUCCESS', payload: data });
        } catch (err) {
            console.error(err);
            dispatch({ type: 'SEARCH_ERROR', payload: "Failed to fetch results. Ensure backend is running." });
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 pb-20 font-sans">
            {/* Header */}
            <header className="bg-white shadow-sm sticky top-0 z-50 backdrop-blur-md bg-opacity-90">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-lg shadow-indigo-200 shadow-md">
                            V
                        </div>
                        <h1 className="text-xl font-bold text-gray-900 tracking-tight">VisualSearch<span className="text-indigo-600">Pro</span></h1>
                    </div>
                    <nav className="flex gap-6 text-sm font-medium text-gray-500">
                        <div className="text-gray-500">
                            {state.latency && <span className="text-green-600 font-mono text-xs bg-green-50 px-2 py-1 rounded-md border border-green-100">Latency: {state.latency}</span>}
                        </div>
                    </nav>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 transition-all duration-500 ease-in-out">

                {/* Intro / Hero */}
                {state.status === 'idle' && !state.preview && (
                    <div className="text-center mb-16 animate-fade-in-up">
                        <h2 className="text-4xl font-extrabold text-gray-900 mb-4 tracking-tight">Find similar items in seconds</h2>
                        <p className="text-lg text-gray-600 max-w-2xl mx-auto leading-relaxed">Upload an image to search across our local inventory and the entire web simultaneously using AI-powered visual recognition.</p>
                    </div>
                )}

                {/* Upload Section */}
                <div className={`max-w-3xl mx-auto transition-all duration-500 transform ${state.results ? 'scale-95 opacity-80 mb-8' : 'scale-100 mb-16'}`}>
                    <div
                        className={`upload-zone bg-white shadow-sm hover:shadow-md transition-all duration-300 ${state.status === 'searching' ? 'pointer-events-none opacity-50' : ''}`}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                        onClick={() => fileInputRef.current.click()}
                    >
                        <input
                            type="file"
                            ref={fileInputRef}
                            className="hidden"
                            accept="image/*"
                            onChange={handleFileChange}
                        />

                        {state.preview ? (
                            <div className="relative inline-block group">
                                <img src={state.preview} alt="Preview" className="h-64 rounded-lg shadow-lg object-cover mx-auto ring-4 ring-white" />
                                <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity rounded-lg cursor-pointer backdrop-blur-sm">
                                    <span className="text-white font-bold tracking-wide">Click to change</span>
                                </div>
                            </div>
                        ) : (
                            <div className="space-y-4 py-8">
                                <div className="w-20 h-20 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4 animate-bounce-slow">
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                    </svg>
                                </div>
                                <div>
                                    <p className="text-xl font-semibold text-gray-900">Drop an image here, or click to upload</p>
                                    <p className="text-sm text-gray-500 mt-2">Supports JPG, PNG, WEBP</p>
                                </div>
                            </div>
                        )}
                    </div>

                    {state.preview && state.status !== 'searching' && (
                        <div className="mt-8 text-center animate-fade-in">
                            <button
                                onClick={(e) => { e.stopPropagation(); handleSearch(); }}
                                className="btn-primary w-full sm:w-auto text-lg py-3 px-12 shadow-xl shadow-indigo-200 hover:shadow-indigo-300 transform hover:-translate-y-0.5 transition-all"
                            >
                                Search Now
                            </button>
                        </div>
                    )}

                    {state.status === 'searching' && (
                        <div className="mt-8 text-center">
                            <div className="inline-flex items-center gap-3 px-6 py-3 bg-white rounded-full shadow-lg border border-indigo-100">
                                <svg className="animate-spin h-5 w-5 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                <span className="font-medium text-gray-700">Analyzing visual features...</span>
                            </div>
                        </div>
                    )}

                    {state.error && (
                        <div className="mt-6 p-4 bg-red-50 text-red-700 rounded-xl text-center border border-red-100 shadow-sm animate-shake">
                            <span className="font-bold">Error:</span> {state.error}
                        </div>
                    )}

                    {state.statusMessages && state.statusMessages.length > 0 && (
                        <div className="mt-6 space-y-2">
                            {state.statusMessages.map((msg, idx) => (
                                <div key={idx} className="p-3 bg-yellow-50 text-yellow-800 rounded-lg border border-yellow-200 text-sm flex items-center justify-center gap-2">
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                    </svg>
                                    {msg}
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Results Area */}
                <div id="results" className="scroll-mt-20">
                    {state.results && <ResultsGrid results={state.results} />}
                </div>
            </main>
        </div>
    );
}

export default App;
