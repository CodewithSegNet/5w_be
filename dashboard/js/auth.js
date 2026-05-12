/* ══════════════════════════════════════════════════
   Auth Module — JWT login/register for dashboard
   ══════════════════════════════════════════════════ */

// API_BASE points to the FastAPI backend (Render in production, localhost in dev)
const API_BASE = window.__API_BASE__ ||
  (window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://fivew-be.onrender.com');

const Auth = {
  token: localStorage.getItem('5wof_token'),
  admin: JSON.parse(localStorage.getItem('5wof_admin') || 'null'),

  isLoggedIn() { return !!this.token; },

  setSession(data) {
    this.token = data.access_token;
    this.admin = data.admin;
    localStorage.setItem('5wof_token', data.access_token);
    localStorage.setItem('5wof_admin', JSON.stringify(data.admin));
  },

  clearSession() {
    this.token = null;
    this.admin = null;
    localStorage.removeItem('5wof_token');
    localStorage.removeItem('5wof_admin');
  },

  headers() {
    const h = { 'Content-Type': 'application/json' };
    if (this.token) h['Authorization'] = `Bearer ${this.token}`;
    return h;
  },

  async api(path, opts = {}) {
    const url = `${API_BASE}${path}`;
    const config = { headers: this.headers(), ...opts };
    if (config.body && typeof config.body === 'object' && !(config.body instanceof FormData)) {
      config.body = JSON.stringify(config.body);
    }
    if (config.body instanceof FormData) {
      delete config.headers['Content-Type'];
    }
    const res = await fetch(url, config);
    if (res.status === 401) {
      this.clearSession();
      showLogin();
      throw new Error('Session expired');
    }
    return res;
  },

  async login(email, password) {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Login failed');
    }
    const data = await res.json();
    this.setSession(data);
    return data;
  },

  async register(fullName, email, password) {
    const res = await fetch(`${API_BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ full_name: fullName, email, password }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Registration failed');
    }
    return await res.json();
  },
};

function showLogin() {
  document.getElementById('loginScreen').style.display = 'flex';
  document.getElementById('dashboardShell').style.display = 'none';
  // Show login form, hide register
  document.getElementById('loginForm').style.display = '';
  document.getElementById('showRegisterToggle').style.display = '';
  document.getElementById('registerSection').style.display = 'none';
}

function showRegister() {
  // Hide login form, show register
  document.getElementById('loginForm').style.display = 'none';
  document.getElementById('showRegisterToggle').style.display = 'none';
  document.getElementById('registerSection').style.display = 'block';
}

function showDashboard() {
  document.getElementById('loginScreen').style.display = 'none';
  document.getElementById('dashboardShell').style.display = 'flex';
  const name = Auth.admin?.full_name || 'Admin';
  document.getElementById('adminName').textContent = name;
  document.getElementById('adminAvatar').textContent = name.charAt(0).toUpperCase();
}

document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');
  const loginError = document.getElementById('loginError');
  const registerError = document.getElementById('registerError');

  // Toggle between login and register
  document.getElementById('toggleToRegister')?.addEventListener('click', (e) => {
    e.preventDefault();
    loginError.textContent = '';
    showRegister();
  });

  document.getElementById('toggleToLogin')?.addEventListener('click', (e) => {
    e.preventDefault();
    registerError.textContent = '';
    showLogin();
  });

  // Login
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    loginError.textContent = '';
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const btn = document.getElementById('loginBtn');
    btn.disabled = true;
    btn.textContent = 'Signing in…';
    try {
      await Auth.login(email, password);
      showDashboard();
      if (typeof initDashboard === 'function') initDashboard();
    } catch (err) {
      loginError.textContent = err.message;
    } finally {
      btn.disabled = false;
      btn.textContent = 'Sign In';
    }
  });

  // Register
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    registerError.textContent = '';
    const name = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    try {
      await Auth.register(name, email, password);
      // Auto-login after registration
      await Auth.login(email, password);
      showDashboard();
      if (typeof initDashboard === 'function') initDashboard();
    } catch (err) {
      registerError.textContent = err.message;
    }
  });

  // Logout
  document.getElementById('logoutBtn').addEventListener('click', () => {
    Auth.clearSession();
    showLogin();
  });
  document.getElementById('mobileLogoutBtn').addEventListener('click', () => {
    Auth.clearSession();
    showLogin();
  });

  // Check session on load
  if (Auth.isLoggedIn()) {
    showDashboard();
  } else {
    showLogin();
  }

  // ── Password visibility toggle (event delegation) ──
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.pw-toggle');
    if (!btn) return;
    const targetId = btn.dataset.target;
    const input = document.getElementById(targetId);
    if (!input) return;
    const isPassword = input.type === 'password';
    input.type = isPassword ? 'text' : 'password';
    btn.querySelector('.eye-open').style.display = isPassword ? 'none' : '';
    btn.querySelector('.eye-closed').style.display = isPassword ? '' : 'none';
  });
});

// Helper: wraps a password input in a pw-wrap with eye toggle (for dynamic modals)
function pwWrapHtml(id, placeholder, extras = '') {
  return `<div class="pw-wrap">
    <input type="password" id="${id}" placeholder="${placeholder}" ${extras}>
    <button type="button" class="pw-toggle" data-target="${id}" aria-label="Toggle password">
      <svg class="eye-open" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
      <svg class="eye-closed" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:none"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/><path d="M14.12 14.12a3 3 0 1 1-4.24-4.24"/></svg>
    </button>
  </div>`;
}
