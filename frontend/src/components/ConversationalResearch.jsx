import React, { useState } from 'react'
import { MessageCircle, Send, Brain, Loader2, CheckCircle, AlertCircle, Lightbulb } from 'lucide-react'

const ConversationalResearch = ({ onReportGenerated }) => {
  const [goal, setGoal] = useState('')
  const [currentStep, setCurrentStep] = useState('input') // input, questions, answers, generating, complete
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState({})
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [researchData, setResearchData] = useState(null)

  const handleStartConversation = async () => {
    if (!goal.trim()) return

    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetch('http://127.0.0.1:8000/research-questions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal })
      })

      if (!response.ok) {
        throw new Error(`Failed to generate questions: ${response.status}`)
      }

      const data = await response.json()
      setQuestions(data.questions || [])
      setCurrentStep('questions')
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleAnswerChange = (questionIndex, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionIndex]: answer
    }))
  }

  const handleGenerateRefinedReport = async () => {
    setIsLoading(true)
    setError(null)
    setCurrentStep('generating')

    try {
      // Convert answers to the format expected by the API
      const formattedAnswers = questions.map((question, index) => ({
        question,
        answer: answers[index] || ''
      }))

      const response = await fetch('http://127.0.0.1:8000/refined-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          original_goal: goal,
          answers: formattedAnswers
        })
      })

      if (!response.ok) {
        throw new Error(`Failed to generate refined report: ${response.status}`)
      }

      const data = await response.json()
      setResearchData(data)
      setCurrentStep('complete')
      
      // Pass the report to parent component
      if (onReportGenerated) {
        onReportGenerated({
          report: data.report,
          goal: data.refined_goal || goal,
          stats: {
            documents: data.document_count,
            refinements: data.refinements
          }
        })
      }
    } catch (err) {
      setError(err.message)
      setCurrentStep('questions')
    } finally {
      setIsLoading(false)
    }
  }

  const handleStartOver = () => {
    setGoal('')
    setCurrentStep('input')
    setQuestions([])
    setAnswers({})
    setError(null)
    setResearchData(null)
  }

  const renderInputStep = () => (
    <div className="space-y-6">
      <div className="text-center">
        <MessageCircle className="h-16 w-16 text-primary-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-100 mb-2">
          Conversational Research
        </h2>
        <p className="text-gray-400 max-w-md mx-auto">
          Let's have a conversation to refine your research goal and generate a comprehensive report.
        </p>
      </div>

      <div className="max-w-2xl mx-auto">
        <label className="block text-sm font-medium text-gray-300 mb-2">
          What would you like to research?
        </label>
        <div className="flex space-x-3">
          <input
            type="text"
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="e.g., quantum computing applications in cryptography"
            className="flex-1 px-4 py-3 bg-dark-700 border border-dark-600 rounded-lg text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            onKeyPress={(e) => e.key === 'Enter' && handleStartConversation()}
          />
          <button
            onClick={handleStartConversation}
            disabled={!goal.trim() || isLoading}
            className="px-6 py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors duration-200 flex items-center space-x-2"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
            <span>{isLoading ? 'Generating...' : 'Start'}</span>
          </button>
        </div>
      </div>
    </div>
  )

  const renderQuestionsStep = () => (
    <div className="space-y-6">
      <div className="text-center">
        <Brain className="h-12 w-12 text-primary-500 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-gray-100 mb-2">
          Let's refine your research focus
        </h2>
        <p className="text-gray-400">
          Please answer these questions to help me generate a more targeted research report.
        </p>
      </div>

      <div className="max-w-3xl mx-auto space-y-6">
        {questions.map((question, index) => (
          <div key={index} className="bg-dark-800 rounded-lg p-6 border border-dark-700">
            <label className="block text-sm font-medium text-gray-300 mb-3">
              {index + 1}. {question}
            </label>
            <textarea
              value={answers[index] || ''}
              onChange={(e) => handleAnswerChange(index, e.target.value)}
              placeholder="Your answer..."
              rows={3}
              className="w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-lg text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
            />
          </div>
        ))}

        <div className="flex justify-between items-center pt-4">
          <button
            onClick={handleStartOver}
            className="px-4 py-2 text-gray-400 hover:text-gray-300 transition-colors"
          >
            ← Start Over
          </button>
          
          <button
            onClick={handleGenerateRefinedReport}
            disabled={isLoading}
            className="px-8 py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors duration-200 flex items-center space-x-2"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Brain className="h-4 w-4" />
            )}
            <span>{isLoading ? 'Generating Report...' : 'Generate Refined Report'}</span>
          </button>
        </div>
      </div>
    </div>
  )

  const renderGeneratingStep = () => (
    <div className="text-center space-y-6">
      <div className="flex justify-center">
        <div className="relative">
          <Loader2 className="h-16 w-16 text-primary-500 animate-spin" />
          <div className="absolute inset-0 bg-primary-500/20 rounded-full animate-ping"></div>
        </div>
      </div>
      <div>
        <h2 className="text-xl font-bold text-gray-100 mb-2">
          Generating Your Refined Research Report
        </h2>
        <p className="text-gray-400">
          Analyzing your answers and collecting the most relevant research...
        </p>
      </div>
      <div className="max-w-md mx-auto bg-dark-800 rounded-lg p-4">
        <div className="flex items-center space-x-3 text-sm text-gray-300">
          <CheckCircle className="h-4 w-4 text-green-500" />
          <span>Research plan generated</span>
        </div>
        <div className="flex items-center space-x-3 text-sm text-gray-300 mt-2">
          <CheckCircle className="h-4 w-4 text-green-500" />
          <span>Documents collected and filtered</span>
        </div>
        <div className="flex items-center space-x-3 text-sm text-gray-300 mt-2">
          <Loader2 className="h-4 w-4 animate-spin text-primary-500" />
          <span>Generating comprehensive report...</span>
        </div>
      </div>
    </div>
  )

  const renderCompleteStep = () => (
    <div className="text-center space-y-6">
      <div className="flex justify-center">
        <CheckCircle className="h-16 w-16 text-green-500" />
      </div>
      <div>
        <h2 className="text-xl font-bold text-gray-100 mb-2">
          Research Report Generated Successfully!
        </h2>
        <p className="text-gray-400">
          Your refined research report is ready. Check the Report tab to view it.
        </p>
      </div>
      
      {researchData && (
        <div className="max-w-md mx-auto bg-dark-800 rounded-lg p-4 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">Documents analyzed:</span>
            <span className="text-gray-100">{researchData.document_count}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">Refined goal:</span>
            <span className="text-gray-100 text-right max-w-48 truncate">
              {researchData.refined_goal || goal}
            </span>
          </div>
        </div>
      )}

      <button
        onClick={handleStartOver}
        className="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors duration-200"
      >
        Start New Research
      </button>
    </div>
  )

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {error && (
        <div className="mb-6 bg-red-900/20 border border-red-700 rounded-lg p-4 flex items-center space-x-3">
          <AlertCircle className="h-5 w-5 text-red-400" />
          <span className="text-red-300">{error}</span>
        </div>
      )}

      {currentStep === 'input' && renderInputStep()}
      {currentStep === 'questions' && renderQuestionsStep()}
      {currentStep === 'generating' && renderGeneratingStep()}
      {currentStep === 'complete' && renderCompleteStep()}
    </div>
  )
}

export default ConversationalResearch
