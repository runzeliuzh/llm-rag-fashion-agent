// Simplified API service for Fashion RAG without authentication
import { getDomain } from './getDomain';

class ApiService {
  constructor() {
    this.initializeUsageTracking();
  }

  // Get API base URL dynamically
  getApiBaseUrl() {
    return getDomain().backendDomain;
  }

  // Initialize usage tracking for anonymous users
  initializeUsageTracking() {
    const now = Date.now();
    const stored = localStorage.getItem('fashionAgent_usage');
    
    if (stored) {
      const usage = JSON.parse(stored);
      // Check if 5 hours have passed (5 * 60 * 60 * 1000 = 18,000,000 ms)
      if (now - usage.timestamp > 18000000) {
        // Reset usage after 5 hours
        this.resetUsage();
      }
    } else {
      // First time user
      this.resetUsage();
    }
  }

  // Reset usage tracking
  resetUsage() {
    const usage = {
      count: 0,
      timestamp: Date.now(),
      limit: 20
    };
    localStorage.setItem('fashionAgent_usage', JSON.stringify(usage));
  }

  // Get current usage (synchronous - for initial state)
  getUsageSync() {
    const stored = localStorage.getItem('fashionAgent_usage');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        // Validate the parsed data
        return {
          count: isNaN(parsed.count) ? 0 : parsed.count,
          timestamp: isNaN(parsed.timestamp) ? Date.now() : parsed.timestamp,
          limit: isNaN(parsed.limit) ? 20 : parsed.limit,
          serverSync: parsed.serverSync || false,
          serverResetTime: parsed.serverResetTime || null
        };
      } catch (error) {
        console.log('Error parsing stored usage data:', error);
      }
    }
    return { count: 0, timestamp: Date.now(), limit: 20, serverSync: false };
  }

  // Get current usage - always check server first if available (async - for updates)
  async getUsage() {
    try {
      // Try to get server status first
      const serverStatus = await this.getRateLimitStatus();
      if (serverStatus) {
        // Calculate max_queries from queries_used + queries_remaining
        const maxQueries = (serverStatus.queries_used || 0) + (serverStatus.queries_remaining || 20);
        // Update local storage with server data
        const serverUsage = {
          count: serverStatus.queries_used || 0,
          timestamp: Date.now(),
          limit: maxQueries,
          serverResetTime: serverStatus.reset_time,
          serverSync: true
        };
        localStorage.setItem('fashionAgent_usage', JSON.stringify(serverUsage));
        return serverUsage;
      } else {
        // Server is not responding - mark as disconnected
        console.log('🔌 Server not responding, marking as disconnected');
        const offlineUsage = this.getUsageSync();
        offlineUsage.serverSync = false;
        offlineUsage.serverResetTime = null;
        localStorage.setItem('fashionAgent_usage', JSON.stringify(offlineUsage));
        return offlineUsage;
      }
    } catch (error) {
      console.log('🔌 Server unavailable, using local tracking');
      // Fallback to local storage when server is unavailable
      const offlineUsage = this.getUsageSync();
      offlineUsage.serverSync = false;
      offlineUsage.serverResetTime = null;
      localStorage.setItem('fashionAgent_usage', JSON.stringify(offlineUsage));
      return offlineUsage;
    }
  }

  // Get server rate limit status
  async getRateLimitStatus() {
    try {
      const response = await fetch(`${this.getApiBaseUrl()}/api/v1/rate-limit-status`);
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      // Server unavailable
    }
    return null;
  }

  // Check if user has reached limit (synchronous)
  hasReachedLimitSync() {
    const usage = this.getUsageSync();
    return usage.count >= usage.limit;
  }

  // Check if user has reached limit (async - with server check)
  async hasReachedLimit() {
    const usage = await this.getUsage();
    return usage.count >= usage.limit;
  }

  // Increment usage count (async - with server sync)
  async incrementUsage() {
    const usage = await this.getUsage();
    usage.count += 1;
    localStorage.setItem('fashionAgent_usage', JSON.stringify(usage));
    return usage;
  }

  // Get time until reset (synchronous)
  getTimeUntilResetSync() {
    const usage = this.getUsageSync();
    
    // If we have server data and valid reset time, use server reset time
    if (usage.serverResetTime && usage.serverSync && usage.serverResetTime !== "N/A" && usage.serverResetTime !== "Window expired - resets on next query") {
      try {
        const resetTime = new Date(usage.serverResetTime);
        if (!isNaN(resetTime.getTime())) {
          const timeRemaining = resetTime.getTime() - Date.now();
          return Math.max(0, timeRemaining);
        }
      } catch (error) {
        console.log('Error parsing server reset time:', error);
      }
    }
    
    // Fallback to local calculation
    const fiveHours = 5 * 60 * 60 * 1000; // 5 hours in milliseconds
    const timeElapsed = Date.now() - usage.timestamp;
    const timeRemaining = fiveHours - timeElapsed;
    
    if (timeRemaining <= 0) {
      this.resetUsage();
      return 0;
    }
    
    return timeRemaining;
  }

    // Get time until reset (async - with server sync)
  async getTimeUntilReset() {
    const usage = await this.getUsage();
    
    // If we have server data and valid reset time, use server reset time
    if (usage.serverResetTime && usage.serverSync && usage.serverResetTime !== "N/A" && usage.serverResetTime !== "Window expired - resets on next query") {
      try {
        const resetTime = new Date(usage.serverResetTime);
        if (!isNaN(resetTime.getTime())) {
          const timeRemaining = resetTime.getTime() - Date.now();
          return Math.max(0, timeRemaining);
        }
      } catch (error) {
        console.log('Error parsing server reset time:', error);
      }
    }
    
    // Fallback to local calculation
    const fiveHours = 5 * 60 * 60 * 1000; // 5 hours in milliseconds
    const timeElapsed = Date.now() - usage.timestamp;
    const timeRemaining = fiveHours - timeElapsed;
    
    if (timeRemaining <= 0) {
      this.resetUsage();
      return 0;
    }
    
    return timeRemaining;
  }

  // Format time until reset (synchronous)
  formatTimeUntilResetSync() {
    const timeRemaining = this.getTimeUntilResetSync();
    if (timeRemaining === 0 || isNaN(timeRemaining)) return "Available now";
    
    const hours = Math.floor(timeRemaining / (60 * 60 * 1000));
    const minutes = Math.floor((timeRemaining % (60 * 60 * 1000)) / (60 * 1000));
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else {
      return `${minutes}m`;
    }
  }

  // Format time until reset (async - with server sync)
  async formatTimeUntilReset() {
    const timeRemaining = await this.getTimeUntilReset();
    if (timeRemaining === 0 || isNaN(timeRemaining)) return "Available now";
    
    const hours = Math.floor(timeRemaining / (60 * 60 * 1000));
    const minutes = Math.floor((timeRemaining % (60 * 60 * 1000)) / (60 * 1000));
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else {
      return `${minutes}m`;
    }
  }

  // Make API request
  async apiRequest(endpoint, options = {}) {
    const url = `${this.getApiBaseUrl()}${endpoint}`;
    console.log(`🌐 SimpleApiService: Making API request to ${url}`);
    
    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    // Stringify body if it's an object
    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    try {
      const response = await fetch(url, config);
      const data = await response.json();
      
      // Handle rate limiting response
      if (response.status === 429) {
        console.warn('⚠️ Rate limit exceeded:', data.detail);
        throw new Error(data.detail?.message || 'Rate limit exceeded. Please try again later.');
      }
      
      if (!response.ok) {
        console.error(`❌ API Error ${response.status}:`, data);
        throw new Error(data.detail || `HTTP error! status: ${response.status}`);
      }
      
      // Update local usage tracking with server response
      if (data.rate_limit) {
        this.updateUsageFromServer(data.rate_limit);
      }
      
      console.log('✅ SimpleApiService: API request successful');
      return data;
      
    } catch (error) {
      console.error('❌ SimpleApiService: API request failed:', error);
      throw error;
    }
  }

  // Update local usage tracking with server data
  async updateUsageFromServer(rateLimitInfo) {
    const usage = await this.getUsage();
    const queriesUsed = usage.limit - rateLimitInfo.remaining;
    
    // Update local tracking with server data
    const updatedUsage = {
      ...usage,
      count: queriesUsed,
      serverResetTime: rateLimitInfo.reset_time
    };
    
    localStorage.setItem('fashionAgent_usage', JSON.stringify(updatedUsage));
  }

  // Send fashion query
  async query(message) {
    // Check rate limit before making request
    if (await this.hasReachedLimit()) {
      const resetTime = await this.formatTimeUntilReset();
      throw new Error(`Rate limit reached. You can make 20 queries every 5 hours. Next reset: ${resetTime}`);
    }

    try {
      const response = await this.apiRequest('/api/v1/query', {
        method: 'POST',
        body: { query: message }
      });
      
      // Increment usage on successful request
      const usage = await this.incrementUsage();
      
      // Add usage info to response
      response.usage = {
        count: usage.count,
        limit: usage.limit,
        remaining: usage.limit - usage.count,
        resetTime: await this.formatTimeUntilReset()
      };
      
      return response;
    } catch (error) {
      throw error;
    }
  }
}

// Export singleton instance
export const apiService = new ApiService();
