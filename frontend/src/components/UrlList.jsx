import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { urlAPI } from '../services/api';
import { ExternalLink, BarChart2, Trash2, Copy, CheckCircle, AlertCircle } from 'lucide-react';

function UrlList() {
  const [urls, setUrls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copiedId, setCopiedId] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    fetchUrls();
  }, []);

  const fetchUrls = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await urlAPI.getAll();
      
      // ✅ Ensure it's an array
      if (Array.isArray(response.data)) {
        setUrls(response.data);
      } else {
        console.error('URLs response is not an array:', response.data);
        setUrls([]);
        setError('Invalid response format');
      }
    } catch (err) {
      console.error('Error fetching URLs:', err);
      setError(err.response?.data?.detail || 'Failed to load URLs');
      setUrls([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (shortCode) => {
    if (!window.confirm('Are you sure you want to delete this URL? This action cannot be undone.')) {
      return;
    }

    try {
      setDeletingId(shortCode);
      await urlAPI.delete(shortCode);
      setUrls(urls.filter(url => url.short_code !== shortCode));
    } catch (err) {
      console.error('Error deleting URL:', err);
      alert(err.response?.data?.detail || 'Failed to delete URL');
    } finally {
      setDeletingId(null);
    }
  };

  const copyToClipboard = (shortUrl, id) => {
    navigator.clipboard.writeText(shortUrl);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
            <p className="text-red-800">{error}</p>
          </div>
          <button 
            onClick={fetchUrls}
            className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My URLs</h1>
          <p className="mt-2 text-gray-600">Manage all your shortened links</p>
        </div>
        <Link 
          to="/shorten" 
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Create New URL
        </Link>
      </div>

      {urls.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="max-w-md mx-auto">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <h3 className="mt-4 text-lg font-medium text-gray-900">No URLs yet</h3>
            <p className="mt-2 text-gray-500">Get started by creating your first shortened URL</p>
            <Link 
              to="/shorten" 
              className="mt-6 inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Create Your First URL
            </Link>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {urls.map((url) => (
            <div key={url.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  {/* Title */}
                  <h3 className="text-lg font-medium text-gray-900 truncate">
                    {url.title || 'Untitled'}
                  </h3>
                  
                  {/* Original URL */}
                  <p className="text-sm text-gray-500 truncate mt-1">{url.original_url}</p>
                  
                  {/* Short URL and Stats */}
                  <div className="mt-3 flex items-center gap-4 flex-wrap">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-blue-600">{url.short_url}</span>
                      <button
                        onClick={() => copyToClipboard(url.short_url, url.id)}
                        className="text-gray-400 hover:text-gray-600 transition-colors"
                        title="Copy to clipboard"
                      >
                        {copiedId === url.id ? (
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        ) : (
                          <Copy className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                    
                    <span className="text-sm text-gray-500">
                      {url.click_count || 0} {url.click_count === 1 ? 'click' : 'clicks'}
                    </span>
                    
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                      url.is_active 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {url.is_active ? 'Active' : 'Inactive'}
                    </span>
                    
                    <span className="text-sm text-gray-500">
                      Created: {new Date(url.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center gap-2 ml-4">
                  <a
                    href={url.short_url} // ✅ already correct, uses backend URL
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                    title="Visit URL"
                  >
                    <ExternalLink className="h-5 w-5" />
                  </a>
                  
                  <Link
                    to={`/analytics/${url.short_code}`}
                    className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                    title="View Analytics"
                  >
                    <BarChart2 className="h-5 w-5" />
                  </Link>
                  
                  <button
                    onClick={() => handleDelete(url.short_code)}
                    disabled={deletingId === url.short_code}
                    className="p-2 text-gray-400 hover:text-red-600 transition-colors disabled:opacity-50"
                    title="Delete URL"
                  >
                    {deletingId === url.short_code ? (
                      <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                    ) : (
                      <Trash2 className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default UrlList;