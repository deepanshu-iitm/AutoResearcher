import React, { useState } from 'react'
import { Search, FileText, Brain, Database, BarChart3, Loader2 } from 'lucide-react'
import ResearchForm from './components/ResearchForm'
import ReportViewer from './components/ReportViewer'
import StatsPanel from './components/StatsPanel'

function App() {
  const [activeTab, setActiveTab] = useState('research')
  const [currentReport, setCurrentReport] = useState(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [showNotification, setShowNotification] = useState(false)
  const [progressStep, setProgressStep] = useState(0)

  const handleReportGenerated = (report) => {
    setCurrentReport(report)
    setActiveTab('report') // Auto-switch to Report tab
    setShowNotification(true)
    
    // Hide notification after 3 seconds
    setTimeout(() => {
      setShowNotification(false)
    }, 3000)
  }

  const tabs = [
    { id: 'research', label: 'Research', icon: Search },
    { id: 'report', label: 'Report', icon: FileText },
    // { id: 'stats', label: 'Statistics', icon: BarChart3 }, // Temporarily disabled
  ]

  return (
    <div className="min-h-screen bg-dark-900">
      {/* Navigation Tabs - Centered */}
      <nav className="bg-gradient-to-r from-dark-850 to-dark-800 border-b border-dark-700/30 pt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-center space-x-1">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-8 rounded-t-xl font-medium text-sm transition-all duration-300 ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-b from-primary-600/20 to-transparent border-b-2 border-primary-500 text-primary-300 shadow-lg'
                      : 'text-gray-400 hover:text-gray-300 hover:bg-dark-700/50'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'research' && (
          <ResearchForm 
            onReportGenerated={handleReportGenerated}
            isGenerating={isGenerating}
            setIsGenerating={setIsGenerating}
          />
        )}
        

        
        {activeTab === 'report' && (
          <ReportViewer 
            report={currentReport}
            isGenerating={isGenerating}
          />
        )}
        
        {activeTab === 'stats' && (
          <StatsPanel />
        )}
      </main>

      {/* Enhanced Loading Overlay with Progress Steps */}
      {isGenerating && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-dark-800 rounded-lg p-8 max-w-md w-full mx-4">
            <div className="text-center space-y-4">
              <div className="flex justify-center">
                <Loader2 className="h-8 w-8 text-primary-500 animate-spin" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">
                  Generating Research Report
                </h3>
                <p className="text-sm text-gray-400 mb-4">
                  Please wait while we conduct your research...
                </p>
              </div>
              
              <div className="space-y-2 text-left">
                <div className="flex items-center space-x-3 text-sm text-gray-300">
                  <div className="h-4 w-4 bg-green-500 rounded-full flex items-center justify-center">
                    <div className="h-2 w-2 bg-white rounded-full"></div>
                  </div>
                  <span>Planning research approach</span>
                </div>
                <div className="flex items-center space-x-3 text-sm text-gray-300">
                  <div className="h-4 w-4 bg-green-500 rounded-full flex items-center justify-center">
                    <div className="h-2 w-2 bg-white rounded-full"></div>
                  </div>
                  <span>Collecting documents from multiple sources</span>
                </div>
                <div className="flex items-center space-x-3 text-sm text-gray-300">
                  <Loader2 className="h-4 w-4 animate-spin text-primary-500" />
                  <span>Processing and analyzing content</span>
                </div>
                <div className="flex items-center space-x-3 text-sm text-gray-400">
                  <div className="h-4 w-4 border border-gray-600 rounded-full"></div>
                  <span>Generating comprehensive report</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Success Notification */}
      {showNotification && (
        <div className="fixed top-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 flex items-center space-x-2">
          <FileText className="h-5 w-5" />
          <span>Report generated successfully!</span>
        </div>
      )}
    </div>
  )
}

export default App
