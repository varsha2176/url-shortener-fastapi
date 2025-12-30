import React, { useState } from 'react';
import { urlAPI } from '../services/api';

function UrlShortener({ onUrlCreated }) {
  const [formData, setFormData] = useState({
    original_url: '',
    custom_short_code: '',
    title: '',
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);
    setLoading(true);

    try {
      const data = {
        original_url: formData.original_url,
        title: formData.title || null,
        custom_short_code: formData.custom_short_code || null,
      };
      
      const response = await urlAPI.create(data);
      setResult(response.data);
      setFormData({ original_url: '', custom_short_code: '', title: '' });
      
      if (onUrlCreated) {
        onUrlCreated(response.data);
      }
    } catch (err) {
      console.error('Error creating URL:', err);
      setError(err.response?.data?.detail || 'Failed to create short URL');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(result.short_url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Shorten a URL</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <div>
          <label htmlFor="original_url" className="block text-sm font-medium text-gray-700">
            Long URL *
          </label>
          <input
            type="url"
            id="original_url"
            name="original_url"
            required
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
            placeholder="https://example.com/very/long/url"
            value={formData.original_url}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700">
            Title (optional)
          </label>
          <input
            type="text"
            id="title"
            name="title"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
            placeholder="My Website"
            value={formData.title}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="custom_short_code" className="block text-sm font-medium text-gray-700">
            Custom Short Code (optional)
          </label>
          <input
            type="text"
            id="custom_short_code"
            name="custom_short_code"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
            placeholder="my-link"
            value={formData.custom_short_code}
            onChange={handleChange}
          />
          <p className="mt-1 text-xs text-gray-500">
            Leave blank for auto-generated code
          </p>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Creating...' : 'Shorten URL'}
        </button>
      </form>

      {result && (
        <div className="mt-6 p-4 bg-green-50 rounded-lg">
          <h3 className="text-lg font-medium text-green-900 mb-2">Success!</h3>
          <div className="flex items-center space-x-2">
            <input
              type="text"
              readOnly
              value={result.short_url}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-white"
            />
            <button
              onClick={copyToClipboard}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
            >
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default UrlShortener;