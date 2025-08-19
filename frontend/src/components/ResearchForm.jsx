import React, { useState } from 'react'
import { Search, Sparkles, FileText, Clock } from 'lucide-react'
import axios from 'axios'

const ResearchForm = ({ onReportGenerated, isGenerating, setIsGenerating }) => {
  const [goal, setGoal] = useState('')
  const [maxResults, setMaxResults] = useState(10)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (goal.trim().length < 8) {
      setError('Research goal must be at least 8 characters long')
      return
    }

    setError('')
    setIsGenerating(true)

    try {
      const response = await axios.post('/api/generate-report', {
        goal: goal.trim(),
        max_results: maxResults
      })

      onReportGenerated(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate report')
    } finally {
      setIsGenerating(false)
    }
  }

  const exampleGoals = [
    "machine learning algorithms for healthcare",
    "quantum computing applications",
    "sustainable energy storage solutions",
    "neural network optimization techniques",
    "climate change mitigation strategies"
  ]

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4">
        <div className="flex justify-center">
          <div className="bg-primary-600 p-4 rounded-full">
            <Sparkles className="h-8 w-8 text-white" />
          </div>
        </div>
        <h2 className="text-3xl font-bold text-white">Start Your Research</h2>
        <p className="text-lg text-gray-400 max-w-2xl mx-auto">
          Enter your research goal and let our AI assistant collect, analyze, and synthesize 
          information from multiple academic sources to create a comprehensive report.
        </p>
      </div>

      {/* Research Form */}
      <div className="max-w-2xl mx-auto">
        <form onSubmit={handleSubmit} className="card space-y-6">
          <div>
            <label htmlFor="goal" className="block text-sm font-medium text-gray-300 mb-2">
              Research Goal
            </label>
            <textarea
              id="goal"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="Enter your research topic or question..."
              rows={3}
              className="textarea-field"
              disabled={isGenerating}
            />
            <p className="mt-2 text-sm text-gray-500">
              Be specific about what you want to research. Minimum 8 characters.
            </p>
          </div>

          <div>
            <label htmlFor="maxResults" className="block text-sm font-medium text-gray-300 mb-2">
              Documents per Source
            </label>
            <select
              id="maxResults"
              value={maxResults}
              onChange={(e) => setMaxResults(parseInt(e.target.value))}
              className="input-field"
              disabled={isGenerating}
            >
              <option value={5}>5 documents</option>
              <option value={10}>10 documents</option>
              <option value={15}>15 documents</option>
              <option value={20}>20 documents</option>
            </select>
          </div>

          {error && (
            <div className="bg-red-900/20 border border-red-800 rounded-lg p-4">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={isGenerating || goal.trim().length < 8}
            className="btn-primary w-full flex items-center justify-center space-x-2"
          >
            <Search className="h-5 w-5" />
            <span>{isGenerating ? 'Generating Report...' : 'Generate Research Report'}</span>
          </button>
        </form>
      </div>

      {/* Example Goals */}
      <div className="max-w-4xl mx-auto">
        <h3 className="text-lg font-semibold text-white mb-4 text-center">Example Research Goals</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {exampleGoals.map((example, index) => (
            <button
              key={index}
              onClick={() => setGoal(example)}
              disabled={isGenerating}
              className="card hover:bg-dark-700 transition-colors duration-200 text-left p-4"
            >
              <div className="flex items-start space-x-3">
                <FileText className="h-5 w-5 text-primary-400 mt-0.5 flex-shrink-0" />
                <p className="text-gray-300 text-sm">{example}</p>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Features */}
      <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card text-center">
          <div className="bg-primary-600 p-3 rounded-full w-fit mx-auto mb-4">
            <Search className="h-6 w-6 text-white" />
          </div>
          <h4 className="font-semibold text-white mb-2">Multi-Source Collection</h4>
          <p className="text-gray-400 text-sm">
            Searches arXiv, Semantic Scholar, and Wikipedia simultaneously
          </p>
        </div>

        <div className="card text-center">
          <div className="bg-primary-600 p-3 rounded-full w-fit mx-auto mb-4">
            <Sparkles className="h-6 w-6 text-white" />
          </div>
          <h4 className="font-semibold text-white mb-2">AI-Powered Analysis</h4>
          <p className="text-gray-400 text-sm">
            Uses machine learning to rank and analyze research documents
          </p>
        </div>

        <div className="card text-center">
          <div className="bg-primary-600 p-3 rounded-full w-fit mx-auto mb-4">
            <Clock className="h-6 w-6 text-white" />
          </div>
          <h4 className="font-semibold text-white mb-2">Comprehensive Reports</h4>
          <p className="text-gray-400 text-sm">
            Generates structured reports with citations and analysis
          </p>
        </div>
      </div>
    </div>
  )
}

export default ResearchForm
