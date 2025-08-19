import React, { useState, useEffect } from 'react'
import { BarChart3, Database, FileText, Clock, TrendingUp, Search } from 'lucide-react'
import axios from 'axios'

const StatsPanel = () => {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [searching, setSearching] = useState(false)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/stats')
      setStats(response.data)
    } catch (err) {
      setError('Failed to fetch statistics')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!searchQuery.trim()) return

    setSearching(true)
    try {
      const response = await axios.get('/api/search', {
        params: {
          query: searchQuery,
          max_results: 10
        }
      })
      setSearchResults(response.data.results || [])
    } catch (err) {
      setError('Search failed')
    } finally {
      setSearching(false)
    }
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-pulse">
          <BarChart3 className="h-12 w-12 text-primary-500 mx-auto mb-4" />
          <p className="text-gray-400">Loading statistics...</p>
        </div>
      </div>
    )
  }

  if (error && !stats) {
    return (
      <div className="text-center py-12">
        <div className="card max-w-md mx-auto">
          <BarChart3 className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-white mb-2">Error Loading Stats</h3>
          <p className="text-gray-400 mb-4">{error}</p>
          <button onClick={fetchStats} className="btn-primary">
            Retry
          </button>
        </div>
      </div>
    )
  }

  const totalChunks = stats?.total_chunks || 0
  const uniqueDocs = stats?.unique_documents || 0
  const sources = stats?.sources || {}
  const years = stats?.years || {}

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-white">Knowledge Base Statistics</h2>
        <p className="text-gray-400">Overview of your research collection and search capabilities</p>
      </div>

      {/* Main Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card text-center">
          <div className="bg-primary-600 p-3 rounded-full w-fit mx-auto mb-4">
            <FileText className="h-6 w-6 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-white">{uniqueDocs}</h3>
          <p className="text-gray-400">Unique Documents</p>
        </div>

        <div className="card text-center">
          <div className="bg-primary-600 p-3 rounded-full w-fit mx-auto mb-4">
            <Database className="h-6 w-6 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-white">{totalChunks}</h3>
          <p className="text-gray-400">Text Chunks</p>
        </div>

        <div className="card text-center">
          <div className="bg-primary-600 p-3 rounded-full w-fit mx-auto mb-4">
            <TrendingUp className="h-6 w-6 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-white">{Object.keys(sources).length}</h3>
          <p className="text-gray-400">Data Sources</p>
        </div>

        <div className="card text-center">
          <div className="bg-primary-600 p-3 rounded-full w-fit mx-auto mb-4">
            <Clock className="h-6 w-6 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-white">{Object.keys(years).length}</h3>
          <p className="text-gray-400">Publication Years</p>
        </div>
      </div>

      {/* Sources Breakdown */}
      {Object.keys(sources).length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-4">Sources Breakdown</h3>
          <div className="space-y-3">
            {Object.entries(sources).map(([source, count]) => (
              <div key={source} className="flex items-center justify-between">
                <span className="text-gray-300">{source}</span>
                <div className="flex items-center space-x-3">
                  <div className="bg-dark-700 rounded-full h-2 w-32">
                    <div 
                      className="bg-primary-500 h-2 rounded-full"
                      style={{ width: `${(count / Math.max(...Object.values(sources))) * 100}%` }}
                    />
                  </div>
                  <span className="text-primary-400 font-semibold w-8 text-right">{count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Knowledge Base Search */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Search Knowledge Base</h3>
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex space-x-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search through processed documents..."
              className="input-field flex-1"
            />
            <button
              type="submit"
              disabled={searching || !searchQuery.trim()}
              className="btn-primary flex items-center space-x-2"
            >
              <Search className="h-4 w-4" />
              <span>{searching ? 'Searching...' : 'Search'}</span>
            </button>
          </div>
        </form>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="mt-6 space-y-4">
            <h4 className="font-medium text-white">Search Results ({searchResults.length})</h4>
            <div className="space-y-3">
              {searchResults.map((result, index) => (
                <div key={index} className="bg-dark-700 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h5 className="font-medium text-white text-sm">
                      {result.metadata?.title || 'Untitled Document'}
                    </h5>
                    <span className="text-xs text-gray-400">
                      {result.metadata?.source || 'Unknown'}
                    </span>
                  </div>
                  <p className="text-gray-300 text-sm mb-2">
                    {result.text?.substring(0, 200)}...
                  </p>
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>Similarity: {(1 - result.distance).toFixed(3)}</span>
                    {result.metadata?.year && (
                      <span>Year: {result.metadata.year}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {searchQuery && searchResults.length === 0 && !searching && (
          <div className="mt-4 text-center py-4">
            <p className="text-gray-400">No results found for "{searchQuery}"</p>
          </div>
        )}
      </div>

      {/* Recent Years */}
      {Object.keys(years).length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-4">Publication Years</h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {Object.entries(years)
              .sort(([a], [b]) => parseInt(b) - parseInt(a))
              .slice(0, 10)
              .map(([year, count]) => (
                <div key={year} className="bg-dark-700 rounded-lg p-3 text-center">
                  <div className="text-lg font-semibold text-white">{year}</div>
                  <div className="text-sm text-gray-400">{count} docs</div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {totalChunks === 0 && (
        <div className="card text-center py-8">
          <Database className="h-12 w-12 text-gray-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-white mb-2">No Data Yet</h3>
          <p className="text-gray-400">
            Generate your first research report to start building your knowledge base.
          </p>
        </div>
      )}
    </div>
  )
}

export default StatsPanel
