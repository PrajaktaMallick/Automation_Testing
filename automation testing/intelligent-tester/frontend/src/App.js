import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { motion } from 'framer-motion';

// Components
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';

// Pages
import Dashboard from './pages/Dashboard';
import CreateTest from './pages/CreateTest';
import TestResults from './pages/TestResults';
import TestHistory from './pages/TestHistory';
import Analytics from './pages/Analytics';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="flex">
        <Sidebar />
        
        <main className="flex-1 ml-64 p-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/create" element={<CreateTest />} />
              <Route path="/test/:sessionId" element={<TestResults />} />
              <Route path="/history" element={<TestHistory />} />
              <Route path="/analytics" element={<Analytics />} />
            </Routes>
          </motion.div>
        </main>
      </div>
    </div>
  );
}

export default App;
