/* ══════════════════════════════════════════════════
   Auth Module — JWT login/register for dashboard
   ══════════════════════════════════════════════════ */

const API_BASE = window.location.origin;

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
  const registerSection = document.getElementById('registerSection');

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
      if (err.message.includes('Invalid')) {
        loginError.textContent = err.message;
        // Check if no admins exist — show register
        registerSection.style.display = 'block';
      } else {
        loginError.textContent = err.message;
      }
    } finally {
      btn.disabled = false;
      btn.textContent = 'Sign In';
    }
  });

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
});
