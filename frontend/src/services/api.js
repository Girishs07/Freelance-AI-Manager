// src/services/api.js - Updated for Flask backend
const API_BASE_URL = 'http://localhost:5000/api';

class ApiService {
  // Auth endpoints
  static async register(userData) {
    const response = await fetch(`${API_BASE_URL}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Include cookies for session management
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    return response.json();
  }

  static async login(credentials) {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Include cookies for session management
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    // Store the user data in localStorage (the token is just for frontend compatibility)
    if (data.access_token && data.user) {
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
    }
    return data;
  }

  static async logout() {
    try {
      await fetch(`${API_BASE_URL}/logout`, {
        method: 'POST',
        credentials: 'include',
      });
    } catch (error) {
      console.error('Logout request failed:', error);
    } finally {
      // Always clear local storage
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  }

  static getAuthToken() {
    return localStorage.getItem('token');
  }

  static getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  static isAuthenticated() {
    return !!this.getAuthToken() && !!this.getCurrentUser();
  }

  // Helper method to make authenticated requests
  static async authenticatedRequest(url, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const response = await fetch(`${API_BASE_URL}${url}`, {
      ...options,
      headers,
      credentials: 'include', // Include cookies for session
    });

    if (response.status === 401) {
      // Session expired or invalid
      this.logout();
      window.location.href = '/login';
      throw new Error('Authentication required');
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Request failed');
    }

    return response.json();
  }

  // Dashboard endpoints
  static async getAnalytics(userId) {
    return this.authenticatedRequest(`/analytics/${userId}`);
  }

  static async getJobs(userId) {
    return this.authenticatedRequest(`/jobs/${userId}`);
  }

  static async searchJobs(userId) {
    return this.authenticatedRequest(`/jobs/search/${userId}`, {
      method: 'POST',
    });
  }

  static async getUserProjects(userId) {
    return this.authenticatedRequest(`/projects/${userId}`);
  }

  static async getSkillGaps(userId) {
    return this.authenticatedRequest(`/skill-gaps/${userId}`);
  }

  static async generateProposal(data) {
    return this.authenticatedRequest('/proposals/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

export default ApiService;