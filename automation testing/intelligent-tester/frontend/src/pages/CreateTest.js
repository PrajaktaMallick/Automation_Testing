import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useMutation } from 'react-query';
import { 
  Globe, 
  MessageSquare, 
  Play, 
  Sparkles, 
  AlertCircle,
  CheckCircle,
  Clock,
  Zap
} from 'lucide-react';
import toast from 'react-hot-toast';

import { api } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

const CreateTest = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    website_url: '',
    prompt: '',
    context: {}
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [websiteAnalysis, setWebsiteAnalysis] = useState(null);

  // Mutations
  const createTestMutation = useMutation(api.createTest, {
    onSuccess: (data) => {
      toast.success('Test created successfully!');
      // Auto-execute the test
      executeTestMutation.mutate(data.session_id);
    },
    onError: (error) => {
      toast.error('Failed to create test');
    }
  });

  const executeTestMutation = useMutation(api.executeTest, {
    onSuccess: (data) => {
      toast.success('Test execution started!');
      navigate(`/test/${data.session_id}`);
    },
    onError: (error) => {
      toast.error('Failed to start test execution');
    }
  });

  const analyzeWebsiteMutation = useMutation(api.analyzeWebsite, {
    onSuccess: (data) => {
      setWebsiteAnalysis(data.analysis);
      toast.success('Website analyzed successfully!');
    },
    onError: (error) => {
      toast.error('Failed to analyze website');
    }
  });

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleAnalyzeWebsite = async () => {
    if (!formData.website_url) {
      toast.error('Please enter a website URL first');
      return;
    }

    try {
      new URL(formData.website_url);
    } catch {
      toast.error('Please enter a valid URL');
      return;
    }

    analyzeWebsiteMutation.mutate(formData.website_url);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.website_url || !formData.prompt) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      new URL(formData.website_url);
    } catch {
      toast.error('Please enter a valid URL');
      return;
    }

    const testData = {
      ...formData,
      context: {
        ...formData.context,
        website_analysis: websiteAnalysis
      }
    };

    createTestMutation.mutate(testData);
  };

  const examplePrompts = [
    "Go to the login page and login with jyoti@test.com / 123456",
    "Search for a red hoodie and add to cart",
    "Click the third image on the homepage and proceed to checkout",
    "Test if logging out works after adding an item",
    "Fill out the contact form with test data and submit",
    "Navigate to the pricing page and click on the premium plan"
  ];

  const isLoading = createTestMutation.isLoading || executeTestMutation.isLoading;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-4xl mx-auto space-y-8"
    >
      {/* Header */}
      <div className="text-center">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2 }}
          className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-primary-500 to-purple-600 rounded-full mb-4"
        >
          <Sparkles className="h-8 w-8 text-white" />
        </motion.div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Create Intelligent Test</h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Describe what you want to test in plain English. Our AI will understand your intent 
          and create a comprehensive test plan automatically.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Form */}
        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Website URL */}
            <div className="card">
              <div className="flex items-center space-x-3 mb-4">
                <Globe className="h-5 w-5 text-primary-600" />
                <h2 className="text-lg font-semibold text-gray-900">Target Website</h2>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="label">Website URL *</label>
                  <div className="flex space-x-2">
                    <input
                      type="url"
                      className="input flex-1"
                      placeholder="https://example.com"
                      value={formData.website_url}
                      onChange={(e) => handleInputChange('website_url', e.target.value)}
                      required
                    />
                    <button
                      type="button"
                      onClick={handleAnalyzeWebsite}
                      disabled={analyzeWebsiteMutation.isLoading}
                      className="btn-outline flex items-center space-x-2"
                    >
                      {analyzeWebsiteMutation.isLoading ? (
                        <div className="w-4 h-4 spinner" />
                      ) : (
                        <Zap className="h-4 w-4" />
                      )}
                      <span>Analyze</span>
                    </button>
                  </div>
                  <p className="text-sm text-gray-500 mt-1">
                    Enter the website you want to test. We'll analyze it to better understand the structure.
                  </p>
                </div>

                {/* Website Analysis Results */}
                {websiteAnalysis && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="bg-green-50 border border-green-200 rounded-lg p-4"
                  >
                    <div className="flex items-center space-x-2 mb-3">
                      <CheckCircle className="h-4 w-4 text-green-600" />
                      <span className="text-sm font-medium text-green-800">Website Analysis Complete</span>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Title:</span>
                        <span className="ml-2 font-medium">{websiteAnalysis.title}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Has Login:</span>
                        <span className="ml-2">{websiteAnalysis.has_login ? '✅' : '❌'}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Has Search:</span>
                        <span className="ml-2">{websiteAnalysis.has_search ? '✅' : '❌'}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Has Cart:</span>
                        <span className="ml-2">{websiteAnalysis.has_cart ? '✅' : '❌'}</span>
                      </div>
                    </div>
                    {websiteAnalysis.detected_frameworks?.length > 0 && (
                      <div className="mt-2">
                        <span className="text-gray-600 text-sm">Frameworks:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {websiteAnalysis.detected_frameworks.map((framework, index) => (
                            <span key={index} className="badge-info text-xs">
                              {framework}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </motion.div>
                )}
              </div>
            </div>

            {/* Test Description */}
            <div className="card">
              <div className="flex items-center space-x-3 mb-4">
                <MessageSquare className="h-5 w-5 text-primary-600" />
                <h2 className="text-lg font-semibold text-gray-900">Test Description</h2>
              </div>
              
              <div>
                <label className="label">What do you want to test? *</label>
                <textarea
                  className="textarea h-32"
                  placeholder="Describe your test in plain English. For example: 'Login with my email and password, then search for headphones and add the first result to cart'"
                  value={formData.prompt}
                  onChange={(e) => handleInputChange('prompt', e.target.value)}
                  required
                />
                <p className="text-sm text-gray-500 mt-1">
                  Be as specific as possible. Include login credentials, search terms, and expected outcomes.
                </p>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex justify-center">
              <button
                type="submit"
                disabled={isLoading}
                className="btn-primary flex items-center space-x-3 px-8 py-3 text-lg"
              >
                {isLoading ? (
                  <>
                    <div className="w-5 h-5 spinner" />
                    <span>Creating Test...</span>
                  </>
                ) : (
                  <>
                    <Play className="h-5 w-5" />
                    <span>Create & Run Test</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Example Prompts */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Example Prompts</h3>
            <div className="space-y-3">
              {examplePrompts.map((prompt, index) => (
                <button
                  key={index}
                  onClick={() => handleInputChange('prompt', prompt)}
                  className="w-full text-left p-3 text-sm bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
                >
                  "{prompt}"
                </button>
              ))}
            </div>
          </div>

          {/* Tips */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Tips for Better Tests</h3>
            <div className="space-y-3 text-sm text-gray-600">
              <div className="flex items-start space-x-2">
                <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                <span>Include specific credentials and test data</span>
              </div>
              <div className="flex items-start space-x-2">
                <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                <span>Describe the expected outcome</span>
              </div>
              <div className="flex items-start space-x-2">
                <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                <span>Break complex flows into steps</span>
              </div>
              <div className="flex items-start space-x-2">
                <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                <span>Use specific element descriptions</span>
              </div>
            </div>
          </div>

          {/* AI Features */}
          <div className="card bg-gradient-to-r from-primary-50 to-purple-50 border-primary-200">
            <div className="flex items-center space-x-2 mb-3">
              <Sparkles className="h-5 w-5 text-primary-600" />
              <h3 className="text-lg font-semibold text-primary-900">AI-Powered Features</h3>
            </div>
            <div className="space-y-2 text-sm text-primary-700">
              <div>✨ Intelligent element detection</div>
              <div>🧠 Context-aware action planning</div>
              <div>🔍 Automatic error recovery</div>
              <div>📸 Smart screenshot capture</div>
              <div>⚡ Real-time execution monitoring</div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default CreateTest;
