import React, { useState, useEffect } from 'react'
import ApiService from '../services/api.js'

function Dashboard({ user, onLogout }) {
  const [activeTab, setActiveTab] = useState('overview')
  const [analytics, setAnalytics] = useState(null)
  const [jobs, setJobs] = useState([])
  const [projects, setProjects] = useState([])
  const [skillGaps, setSkillGaps] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchingJobs, setSearchingJobs] = useState(false)

  useEffect(() => {
    loadDashboardData()
  }, [user.id])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const [analyticsRes, jobsRes, projectsRes, skillGapsRes] = await Promise.all([
        ApiService.getAnalytics(user.id),
        ApiService.getJobs(user.id),
        ApiService.getUserProjects(user.id),
        ApiService.getSkillGaps(user.id)
      ])

      setAnalytics(analyticsRes)
      setJobs(jobsRes.jobs || [])
      setProjects(projectsRes.projects || [])
      setSkillGaps(skillGapsRes.skill_gaps || [])
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const searchNewJobs = async () => {
    try {
      setSearchingJobs(true)
      const response = await ApiService.searchJobs(user.id)
      setJobs(response.jobs || [])
      alert(`Found ${response.high_match_jobs} high-match jobs from ${response.total_found} total jobs!`)
    } catch (error) {
      console.error('Job search failed:', error)
    } finally {
      setSearchingJobs(false)
    }
  }

  const generateProposal = async (jobId) => {
    try {
      const response = await ApiService.generateProposal({
        user_id: user.id,
        job_id: jobId
      })
      alert('Proposal generated successfully!')
      // You could show the proposal in a modal here
    } catch (error) {
      console.error('Proposal generation failed:', error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading dashboard...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Freelance AI Manager
              </h1>
              <p className="text-gray-600">Welcome back, {user.full_name || user.email}!</p>
            </div>
            <button
              onClick={onLogout}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Tab Navigation */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', name: 'Overview' },
              { id: 'jobs', name: 'Job Opportunities' },
              { id: 'projects', name: 'Projects' },
              { id: 'skills', name: 'Skill Development' },
              { id: 'communication', name: 'AI Communication' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && analytics && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                        <span className="text-white font-semibold">$</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Total Earnings
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          ${analytics.summary.total_earnings.toFixed(2)}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                        <span className="text-white font-semibold">H</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Total Hours
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {analytics.summary.total_hours}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                        <span className="text-white font-semibold">R</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Avg Hourly Rate
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          ${analytics.summary.average_hourly_rate}/hr
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-indigo-500 rounded-md flex items-center justify-center">
                        <span className="text-white font-semibold">P</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Active Projects
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {analytics.summary.active_projects}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* AI Pricing Suggestion */}
            {analytics.pricing_suggestion && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-blue-900 mb-2">
                  💡 AI Pricing Suggestion
                </h3>
                <p className="text-blue-800 mb-2">
                  {analytics.pricing_suggestion.recommendation}
                </p>
                {analytics.pricing_suggestion.target_rate && (
                  <p className="text-blue-700">
                    <strong>Suggested Rate:</strong> ${analytics.pricing_suggestion.target_rate}/hour
                  </p>
                )}
                {analytics.pricing_suggestion.tip && (
                  <p className="text-blue-600 text-sm mt-2">
                    <strong>Tip:</strong> {analytics.pricing_suggestion.tip}
                  </p>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'jobs' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Smart Job Opportunities</h2>
              <button
                onClick={searchNewJobs}
                disabled={searchingJobs}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md font-medium disabled:opacity-50"
              >
                {searchingJobs ? 'Searching...' : 'Find New Jobs'}
              </button>
            </div>

            <div className="grid gap-6">
              {jobs.map((job) => (
                <div key={job.id} className="bg-white shadow rounded-lg p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{job.title}</h3>
                      <p className="text-gray-600">{job.client_name} • {job.source}</p>
                      <div className="mt-2">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          job.match_score >= 80 ? 'bg-green-100 text-green-800' :
                          job.match_score >= 60 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {job.match_score}% Match
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      {job.budget && <p className="text-lg font-bold text-green-600">${job.budget}</p>}
                      <button
                        onClick={() => generateProposal(job.id)}
                        className="mt-2 bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1 rounded text-sm"
                      >
                        Generate Proposal
                      </button>
                    </div>
                  </div>
                  <p className="text-gray-700 mb-3">{job.description}</p>
                  <div className="flex flex-wrap gap-2">
                    {job.required_skills.split(',').map((skill, index) => (
                      <span key={index} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm">
                        {skill.trim()}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
              
              {jobs.length === 0 && (
                <div className="text-center py-12">
                  <p className="text-gray-500">No job opportunities found. Click "Find New Jobs" to search!</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'skills' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Skill Development Recommendations</h2>
            
            <div className="grid gap-4">
              {skillGaps.map((gap) => (
                <div key={gap.id} className="bg-white shadow rounded-lg p-6">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{gap.missing_skill}</h3>
                      <p className="text-gray-600">
                        Missed {gap.job_missed_count} opportunities • Priority: {gap.priority_score}/10
                      </p>
                      {gap.learning_resource && (
                        <p className="text-blue-600 text-sm mt-2">
                          📚 {gap.learning_resource}
                        </p>
                      )}
                    </div>
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                      gap.status === 'identified' ? 'bg-red-100 text-red-800' :
                      gap.status === 'learning' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {gap.status}
                    </span>
                  </div>
                </div>
              ))}
              
              {skillGaps.length === 0 && (
                <div className="text-center py-12">
                  <p className="text-gray-500">No skill gaps identified yet. Keep applying to jobs to get AI-powered recommendations!</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Add more tab content as needed */}
      </div>
    </div>
  )
}

export default Dashboard
