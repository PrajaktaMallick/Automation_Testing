import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  Play, 
  ExternalLink,
  Globe
} from 'lucide-react';
import { format, formatDistanceToNow } from 'date-fns';

const RecentTestsList = ({ tests = [] }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'running':
        return <Play className="h-4 w-4 text-blue-500 animate-pulse" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return 'badge-success';
      case 'failed':
        return 'badge-error';
      case 'running':
        return 'badge-info';
      default:
        return 'badge-gray';
    }
  };

  if (tests.length === 0) {
    return (
      <div className="text-center py-12">
        <Clock className="h-12 w-12 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No tests yet</h3>
        <p className="text-gray-600 mb-6">
          Create your first intelligent test to get started
        </p>
        <Link to="/create" className="btn-primary">
          Create Test
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {tests.map((test, index) => (
        <motion.div
          key={test.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-3 mb-2">
                {getStatusIcon(test.status)}
                <h3 className="text-sm font-medium text-gray-900 truncate">
                  {test.original_prompt}
                </h3>
                <span className={`badge ${getStatusBadge(test.status)}`}>
                  {test.status}
                </span>
              </div>
              
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <div className="flex items-center space-x-1">
                  <Globe className="h-3 w-3" />
                  <span className="truncate max-w-48">
                    {new URL(test.website_url).hostname}
                  </span>
                </div>
                
                <div className="flex items-center space-x-1">
                  <Clock className="h-3 w-3" />
                  <span>
                    {formatDistanceToNow(new Date(test.created_at), { addSuffix: true })}
                  </span>
                </div>
                
                {test.total_duration && (
                  <div>
                    Duration: {Math.round(test.total_duration / 60)}m
                  </div>
                )}
              </div>
              
              {test.status === 'completed' && (
                <div className="mt-2 flex items-center space-x-4 text-sm">
                  <span className="text-green-600">
                    ✓ {test.successful_actions} passed
                  </span>
                  {test.failed_actions > 0 && (
                    <span className="text-red-600">
                      ✗ {test.failed_actions} failed
                    </span>
                  )}
                </div>
              )}
            </div>
            
            <div className="flex items-center space-x-2 ml-4">
              <Link
                to={`/test/${test.id}`}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
                title="View details"
              >
                <ExternalLink className="h-4 w-4" />
              </Link>
            </div>
          </div>
          
          {test.status === 'running' && (
            <div className="mt-3">
              <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                <span>Progress</span>
                <span>{test.successful_actions + test.failed_actions}/{test.total_actions}</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ 
                    width: `${((test.successful_actions + test.failed_actions) / test.total_actions) * 100}%` 
                  }}
                />
              </div>
            </div>
          )}
        </motion.div>
      ))}
    </div>
  );
};

export default RecentTestsList;
