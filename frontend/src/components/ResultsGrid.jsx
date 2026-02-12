import React from 'react';

const ResultCard = ({ item, type }) => (
    <div className="card group">
        <div className="relative aspect-square overflow-hidden bg-gray-100">
            <img
                src={item.thumbnail || item.image || "https://via.placeholder.com/300"}
                alt={item.title || item.name}
                className="object-cover w-full h-full group-hover:scale-105 transition-transform duration-300"
            />
            {type === 'local' && (
                <div className="absolute top-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded-full backdrop-blur-sm">
                    Match {(item.score * 100).toFixed(0)}%
                </div>
            )}
        </div>
        <div className="p-4">
            <h3 className="font-medium text-gray-900 line-clamp-1 mb-1" title={item.title || item.name}>
                {item.title || item.name}
            </h3>
            <div className="flex justify-between items-center mt-2">
                <span className="font-bold text-indigo-600">{item.price}</span>
                <a
                    href={item.link || "#"}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-gray-500 hover:text-indigo-600 font-medium"
                >
                    View Source →
                </a>
            </div>
        </div>
    </div>
);

const ResultsGrid = ({ results }) => {
    if (!results) return null;

    const { visual_matches, local_matches, latency } = results;

    return (
        <div className="space-y-12 animate-fade-in">
            {/* Metrics Bar */}
            {latency && (
                <div className="flex gap-4 mb-8">
                    <div className="bg-white px-4 py-2 rounded-lg shadow-sm border border-gray-100 flex items-center gap-2">
                        <span className="text-gray-500 text-sm">Search Latency:</span>
                        <span className="font-mono font-medium text-green-600">{latency}</span>
                    </div>
                </div>
            )}

            {/* Web Matches Section - Full Width */}
            <section>
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                        <span className="bg-blue-100 text-blue-700 p-2 rounded-lg">🌐</span>
                        Web Visual Matches
                    </h2>
                    <span className="bg-gray-100 text-gray-600 px-3 py-1 rounded-full text-sm font-medium">
                        {visual_matches?.length || 0} found
                    </span>
                </div>

                {visual_matches && visual_matches.length > 0 ? (
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
                        {visual_matches.map((item, idx) => (
                            <ResultCard key={`web-${idx}`} item={item} type="web" />
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-20 bg-gray-50 rounded-xl border border-dashed border-gray-200">
                        <p className="text-gray-500 text-lg">No web matches found.</p>
                        <p className="text-gray-400 text-sm mt-2">Try uploading a clear image of a product or object.</p>
                    </div>
                )}
            </section>
        </div>
    );
};

export default ResultsGrid;
