import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { urlAPI, analyticsAPI } from '../services/api';
import { Link2, TrendingUp, MousePointerClick, Calendar } from 'lucide-react';

function Dashboard() {
  const [urls, setUrls] = useState([]);
  const [stats, setStats] = useState({
    totalUrls: 0,
    totalClicks: 0,
    activeUrls: 0
  });
  const [topUrls, setTopUrls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch all URLs
      const urlsResponse = await urlAPI.getAll();
      
      // ✅ Ensure it's an array
      const urlsData = Array.isArray(urlsResponse.data) ? urlsResponse.data : [];
      setUrls(urlsData);

      // Calculate stats
      const totalClicks = urlsData.reduce((sum, url) => sum + (url.click_count || 0), 0);
      const activeUrls = urlsData.filter(url => url.is_active).length;

      setStats({
        totalUrls: urlsData.length,
        totalClicks: totalClicks,
        activeUrls: activeUrls
      });

      // Get top 5 URLs by clicks
      const sortedUrls = [...urlsData]
        .sort((a, b) => (b.click_count || 0) - (a.click_count || 0))
        .slice(0, 5);
      setTopUrls(sortedUrls);

    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err.response?.data?.detail || 'Failed to load dashboard data');
      setUrls([]);
      setTopUrls([]);
    } finally {
      setLoading(false);
    }
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
          <p className="text-red-800">{error}</p>
          <button 
            onClick={fetchDashboardData}
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
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">Welcome back! Here's your URL shortener overview.</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Total URLs */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total URLs</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{stats.totalUrls}</p>
            </div>
            <div className="bg-blue-100 rounded-full p-3">
              <Link2 className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        {/* Total Clicks */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Clicks</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{stats.totalClicks}</p>
            </div>
            <div className="bg-green-100 rounded-full p-3">
              <MousePointerClick className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        {/* Active URLs */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active URLs</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{stats.activeUrls}</p>
            </div>
            <div className="bg-purple-100 rounded-full p-3">
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="flex flex-wrap gap-4">
          <Link 
            to="/shorten" 
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Create New URL
          </Link>
          <Link 
            to="/urls" 
            className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            View All URLs
          </Link>
        </div>
      </div>

      {/* Top URLs */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Top Performing URLs</h2>
        </div>
        <div className="p-6">
          {topUrls.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500">No URLs created yet</p>
              <Link 
                to="/shorten" 
                className="inline-block mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Create Your First URL
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Title
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Short Code
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Clicks
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {topUrls.map((url) => (
                    <tr key={url.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-gray-900">
                          {url.title || 'Untitled'}
                        </div>
                        <div className="text-sm text-gray-500 truncate max-w-xs">
                          {url.original_url}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <a 
                          href={url.short_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-blue-600 hover:text-blue-800"
                        >
                          {url.short_code}
                        </a>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <MousePointerClick className="h-4 w-4 text-gray-400 mr-2" />
                          <span className="text-sm text-gray-900">{url.click_count || 0}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          url.is_active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {url.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <Link 
                          to={`/analytics/${url.short_code}`}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          View Analytics
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      {urls.length > 0 && (
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent URLs</h2>
          <div className="space-y-4">
            {urls.slice(0, 5).map((url) => (
              <div key={url.id} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {url.title || 'Untitled'}
                  </p>
                  <p className="text-sm text-gray-500 truncate">
                    {url.short_url}
                  </p>
                </div>
                <div className="flex items-center gap-4 ml-4">
                  <div className="flex items-center text-sm text-gray-500">
                    <Calendar className="h-4 w-4 mr-1" />
                    {new Date(url.created_at).toLocaleDateString()}
                  </div>
                  <span className="text-sm text-gray-500">
                    {url.click_count || 0} clicks
                  </span>
                </div>
              </div>
            ))}
          </div>
          {urls.length > 5 && (
            <div className="mt-4 text-center">
              <Link 
                to="/urls" 
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                View All URLs →
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Dashboard;