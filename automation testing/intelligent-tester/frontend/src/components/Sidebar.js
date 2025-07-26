import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Home, 
  Plus, 
  History, 
  BarChart3, 
  FileText, 
  Settings,
  HelpCircle,
  Sparkles
} from 'lucide-react';

const Sidebar = () => {
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Create Test', href: '/create', icon: Plus },
    { name: 'Test History', href: '/history', icon: History },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  ];

  const secondaryNavigation = [
    { name: 'Documentation', href: '/docs', icon: FileText },
    { name: 'Settings', href: '/settings', icon: Settings },
    { name: 'Help & Support', href: '/help', icon: HelpCircle },
  ];

  const isActive = (href) => {
    return location.pathname === href;
  };

  return (
    <motion.div
      initial={{ x: -300 }}
      animate={{ x: 0 }}
      className="fixed left-0 top-16 bottom-0 w-64 bg-white border-r border-gray-200 overflow-y-auto"
    >
      <div className="p-6">
        {/* AI Features Banner */}
        <div className="mb-8 p-4 bg-gradient-to-r from-primary-50 to-purple-50 rounded-lg border border-primary-100">
          <div className="flex items-center space-x-2 mb-2">
            <Sparkles className="h-4 w-4 text-primary-600" />
            <span className="text-sm font-medium text-primary-900">AI-Powered</span>
          </div>
          <p className="text-xs text-primary-700">
            Natural language test creation with intelligent element detection
          </p>
        </div>

        {/* Main Navigation */}
        <nav className="space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors
                  ${active 
                    ? 'bg-primary-50 text-primary-700 border border-primary-200' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }
                `}
              >
                <Icon className={`h-5 w-5 ${active ? 'text-primary-600' : 'text-gray-400'}`} />
                <span>{item.name}</span>
                {active && (
                  <motion.div
                    layoutId="activeTab"
                    className="ml-auto w-2 h-2 bg-primary-600 rounded-full"
                  />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Divider */}
        <div className="my-8 border-t border-gray-200"></div>

        {/* Secondary Navigation */}
        <nav className="space-y-2">
          <h3 className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
            Resources
          </h3>
          {secondaryNavigation.map((item) => {
            const Icon = item.icon;
            
            return (
              <Link
                key={item.name}
                to={item.href}
                className="flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition-colors"
              >
                <Icon className="h-5 w-5 text-gray-400" />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Stats Summary */}
        <div className="mt-8 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-sm font-medium text-gray-900 mb-3">Quick Stats</h3>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Tests Today</span>
              <span className="font-medium">12</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Success Rate</span>
              <span className="font-medium text-success-600">94%</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Avg Duration</span>
              <span className="font-medium">2.3m</span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Sidebar;
