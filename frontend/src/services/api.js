const API_BASE = 'http://localhost:5000/api'

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'include',
      ...options,
    }

    if (config.body && typeof config.body !== 'string') {
      config.body = JSON.stringify(config.body)
    }

    try {
      const response = await fetch(url, config)
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Something went wrong')
      }

      return data
    } catch (error) {
      console.error('API Error:', error)
      throw error
    }
  }

  // Auth
  async register(userData) {
    return this.request('/register', {
      method: 'POST',
      body: userData,
    })
  }

  async login(credentials) {
    return this.request('/login', {
      method: 'POST',
      body: credentials,
    })
  }

  async logout() {
    return this.request('/logout', { method: 'POST' })
  }

  // Jobs
  async searchJobs(userId) {
    return this.request(`/jobs/search/${userId}`)
  }

  async getJobs(userId) {
    return this.request(`/jobs/${userId}`)
  }

  // Proposals
  async generateProposal(data) {
    return this.request('/proposals/generate', {
      method: 'POST',
      body: data,
    })
  }

  async getUserProposals(userId) {
    return this.request(`/proposals/${userId}`)
  }

  // Projects
  async createProject(projectData) {
    return this.request('/projects', {
      method: 'POST',
      body: projectData,
    })
  }

  async getUserProjects(userId) {
    return this.request(`/projects/${userId}`)
  }

  // Time tracking
  async logTime(timeData) {
    return this.request('/time-logs', {
      method: 'POST',
      body: timeData,
    })
  }

  // Analytics
  async getAnalytics(userId) {
    return this.request(`/analytics/${userId}`)
  }

  // Skill gaps
  async getSkillGaps(userId) {
    return this.request(`/skill-gaps/${userId}`)
  }

  // Communication
  async getSuggestion(data) {
    return this.request('/communication/suggest', {
      method: 'POST',
      body: data,
    })
  }

  async test() {
    return this.request('/test')
  }
}

export default new ApiService()
