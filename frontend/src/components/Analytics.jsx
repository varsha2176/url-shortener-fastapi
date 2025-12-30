import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { analyticsAPI } from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ArrowLeft, MousePointerClick, Users, TrendingUp, Calendar } from 'lucide-react';

function Analytics() {
  const { shortCode } = useParams();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, [shortCode]);

  const fetchAnalytics = async () => {
    try {
      const response = await analyticsAPI.getEnhanced(shortCode);
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="card text-center py-12">
          <p className="text-gray-500">Analytics not found</p>
          <Link to="/urls" className="btn-primary inline-block mt-4">
            Back to URLs
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <Link to="/urls" className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-4">
          <ArrowLeft className="h-5 w-5 mr-2" />
          Back to URLs
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">Analytics for /{shortCode}</h1>
        <p className="mt-2 text-gray-600">Detailed performance metrics</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Clicks</p>
              <p className="text-3xl font-bold text-gray-900">{analytics.total_clicks}</p>
            </div>
            <MousePointerClick className="h-12 w-12 text-primary-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Unique Visitors</p>
              <p className="text-3xl font-bold text-gray-900">{analytics.unique_visitors}</p>
            </div>
            <Users className="h-12 w-12 text-green-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Clicks Today</p>
              <p className="text-3xl font-bold text-gray-900">{analytics.clicks_today}</p>
            </div>
            <Calendar className="h-12 w-12 text-blue-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg/Day</p>
              <p className="text-3xl font-bold text-gray-900">{analytics.avg_clicks_per_day}</p>
            </div>
            <TrendingUp className="h-12 w-12 text-purple-600" />
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-bold mb-4">Clicks Over Time (30 Days)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={analytics.clicks_daily}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h2 className="text-xl font-bold mb-4">Top Referrers</h2>
          <div className="space-y-3">
            {analytics.top_referrers.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No referrer data available</p>
            ) : (
              analytics.top_referrers.map((ref, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                  <span className="text-sm text-gray-700 truncate">{ref.referrer || 'Direct'}</span>
                  <span className="text-sm font-medium text-gray-900">{ref.count} clicks</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Period Stats */}
      <div className="card mt-6">
        <h2 className="text-xl font-bold mb-4">Period Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-gray-600">This Week</p>
            <p className="text-2xl font-bold text-gray-900 mt-2">{analytics.clicks_this_week}</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-gray-600">This Month</p>
            <p className="text-2xl font-bold text-gray-900 mt-2">{analytics.clicks_this_month}</p>
</div>
<div className="text-center p-4 bg-gray-50 rounded-lg">
<p className="text-gray-600">All Time</p>
<p className="text-2xl font-bold text-gray-900 mt-2">{analytics.total_clicks}</p>
</div>
</div>
</div>
</div>
);
}export default Analytics;