// Srishti Care - Global App Utilities
const API_BASE = window.location.origin;

// Token helpers
function saveSession(token, role, name, email) {
  localStorage.setItem('sc_token', token);
  localStorage.setItem('sc_role', role);
  localStorage.setItem('sc_name', name);
  localStorage.setItem('sc_email', email);
}

function clearSession() {
  localStorage.removeItem('sc_token');
  localStorage.removeItem('sc_role');
  localStorage.removeItem('sc_name');
  localStorage.removeItem('sc_email');
}

function getSession() {
  return {
    token: localStorage.getItem('sc_token'),
    role: localStorage.getItem('sc_role'),
    name: localStorage.getItem('sc_name'),
    email: localStorage.getItem('sc_email')
  };
}

function isLoggedIn() {
  return !!localStorage.getItem('sc_token');
}

// Redirect if not logged in or role mismatch
function checkAuthGuard(requiredRole) {
  const session = getSession();
  if (!session.token) {
    window.location.href = '/login.html';
    return null;
  }
  if (requiredRole && session.role !== requiredRole) {
    showToast('Unauthorized', 'You do not have access to this dashboard.', 'danger');
    // Send user to their corresponding dashboard
    setTimeout(() => {
      if (session.role === 'patient') window.location.href = '/patient_dashboard.html';
      else if (session.role === 'doctor') window.location.href = '/doctor_dashboard.html';
      else if (session.role === 'admin') window.location.href = '/admin_dashboard.html';
      else window.location.href = '/index.html';
    }, 1500);
    return null;
  }
  return session;
}

// Toast alerts helper
function showToast(title, message, type = 'info') {
  // Create toast container if it doesn't exist
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  // Create toast element
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  // Set icons based on type
  let icon = 'fa-info-circle';
  if (type === 'success') icon = 'fa-check-circle';
  if (type === 'danger') icon = 'fa-exclamation-circle';
  if (type === 'warning') icon = 'fa-exclamation-triangle';

  toast.innerHTML = `
    <i class="fas ${icon}" style="color: var(--${type === 'info' ? 'primary' : type})"></i>
    <div class="toast-content">
      <div class="toast-title">${title}</div>
      <div class="toast-message">${message}</div>
    </div>
    <span class="toast-close">&times;</span>
  `;

  container.appendChild(toast);

  // Trigger animation reflow
  setTimeout(() => toast.classList.add('show'), 50);

  // Auto remove toast
  const autoRemove = setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 400);
  }, 4000);

  // Close button trigger
  toast.querySelector('.toast-close').addEventListener('click', () => {
    clearTimeout(autoRemove);
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 400);
  });
}

// Global API Request Wrapper
async function apiRequest(endpoint, options = {}) {
  const session = getSession();
  
  // Build headers
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  // Attach token if exists
  if (session.token) {
    headers['Authorization'] = `Bearer ${session.token}`;
  }

  const config = {
    ...options,
    headers
  };

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, config);
    
    // Check if empty content 204
    if (response.status === 204) {
      return null;
    }

    const data = await response.json();
    
    if (!response.ok) {
      // Handle session expiration
      if (response.status === 401) {
        clearSession();
        showToast('Session Expired', 'Please login again.', 'warning');
        setTimeout(() => { window.location.href = '/login.html'; }, 1500);
      }
      const errorMsg = typeof data.detail === 'object' ? JSON.stringify(data.detail) : (data.detail || 'Something went wrong');
throw new Error(errorMsg);
    }
    return data;
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  }
}

// Unified API Logout Trigger
async function apiLogout() {
  try {
    await apiRequest('/api/auth/logout', { method: 'POST' });
  } catch (e) {
    // Ignore error, clear locally anyway
  }
  clearSession();
  window.location.href = '/index.html';
}
