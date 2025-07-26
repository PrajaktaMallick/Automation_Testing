import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';
import { 
  Plus, 
  Play, 
  CheckCircle, 
  XCircle, 
  Clock, 
  TrendingUp,
  Globe,
  Zap,
  Target,
  Activity
} from 'lucide-react';
import { format } from 'date-fns';

import { api } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import StatCard from '../components/StatCard';
import RecentTestsList from '../components/RecentTestsList';

const Dashboard = () => {
  // Fetch dashboard data
  const { data: stats, isLoading: statsLoading } = useQuery(
    'stats',
    api.getStats,
    { refetchInterval: 30000 }
  );

  const { data: recentTests, isLoading: testsLoading } = useQuery(
    'recentTests',
    () => api.getTests({ page: 1, per_page: 5 }),
    { refetchInterval: 10000 }
  );

  if (statsLoading) {
    return <LoadingSpinner />;
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5
      }
    }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-8"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Welcome back! Here's what's happening with your tests.
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <Link
            to="/create"
            className="btn-primary flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>New Test</span>
          </Link>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Tests"
          value={stats?.total_tests || 0}
          icon={Target}
          color="blue"
          trend={+12}
        />
        <StatCard
          title="Success Rate"
          value={`${Math.round((stats?.success_rate || 0) * 100)}%`}
          icon={CheckCircle}
          color="green"
          trend={+5}
        />
        <StatCard
          title="Avg Duration"
          value={`${Math.round((stats?.average_duration || 0) / 60)}m`}
          icon={Clock}
          color="purple"
          trend={-8}
        />
        <StatCard
          title="Running Tests"
          value={stats?.running_tests || 0}
          icon={Activity}
          color="orange"
          isLive={true}
        />
      </motion.div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Tests */}
        <motion.div variants={itemVariants} className="lg:col-span-2">
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Recent Tests</h2>
              <Link
                to="/history"
                className="text-primary-600 hover:text-primary-700 text-sm font-medium"
              >
                View all
              </Link>
            </div>
            
            {testsLoading ? (
              <div className="flex justify-center py-8">
                <LoadingSpinner size="sm" />
              </div>
            ) : (
              <RecentTestsList tests={recentTests?.sessions || []} />
            )}
          </div>
        </motion.div>

        {/* Quick Actions & Stats */}
        <motion.div variants={itemVariants} className="space-y-6">
          {/* Quick Actions */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <Link
                to="/create"
                className="flex items-center space-x-3 p-3 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors group"
              >
                <div className="p-2 bg-primary-100 rounded-lg group-hover:bg-primary-200">
                  <Plus className="h-4 w-4 text-primary-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">Create Test</p>
                  <p className="text-sm text-gray-600">Start a new intelligent test</p>
                </div>
              </Link>

              <button className="flex items-center space-x-3 p-3 rounded-lg border border-gray-200 hover:border-success-300 hover:bg-success-50 transition-colors group w-full">
                <div className="p-2 bg-success-100 rounded-lg group-hover:bg-success-200">
                  <Globe className="h-4 w-4 text-success-600" />
                </div>
                <div className="text-left">
                  <p className="font-medium text-gray-900">Analyze Website</p>
                  <p className="text-sm text-gray-600">Quick site analysis</p>
                </div>
              </button>

              <Link
                to="/analytics"
                className="flex items-center space-x-3 p-3 rounded-lg border border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-colors group"
              >
                <div className="p-2 bg-purple-100 rounded-lg group-hover:bg-purple-200">
                  <TrendingUp className="h-4 w-4 text-purple-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">View Analytics</p>
                  <p className="text-sm text-gray-600">Performance insights</p>
                </div>
              </Link>
            </div>
          </div>

          {/* Most Tested Sites */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Most Tested Sites</h3>
            <div className="space-y-3">
              {stats?.most_tested_sites?.slice(0, 5).map((site, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                      <Globe className="h-4 w-4 text-gray-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900 truncate max-w-32">
                        {new URL(site.url).hostname}
                      </p>
                      <p className="text-xs text-gray-600">{site.count} tests</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-primary-600 h-2 rounded-full"
                        style={{ width: `${(site.count / (stats?.most_tested_sites?.[0]?.count || 1)) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              )) || (
                <p className="text-sm text-gray-500 text-center py-4">
                  No test data yet
                </p>
              )}
            </div>
          </div>

          {/* System Status */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">System Status</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">API Server</span>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-success-500 rounded-full"></div>
                  <span className="text-sm text-success-600 font-medium">Online</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Browser Engine</span>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-success-500 rounded-full"></div>
                  <span className="text-sm text-success-600 font-medium">Ready</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">AI Service</span>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-warning-500 rounded-full"></div>
                  <span className="text-sm text-warning-600 font-medium">Limited</span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default Dashboard;
