/**
 * api.js — Client API JWT + gestion offline
 * Réseau Académique Camerounais
 */

// Auto-détecte l'URL de base : même domaine en prod (Railway), localhost en dev
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://127.0.0.1:8000/api/v1'
  : '/api/v1';

// ── Gestion des tokens JWT ─────────────────────────────────────────────────────

const Auth = {
  getAccessToken()  { return localStorage.getItem('access_token'); },
  getRefreshToken() { return localStorage.getItem('refresh_token'); },

  setTokens({ access, refresh }) {
    localStorage.setItem('access_token',  access);
    if (refresh) localStorage.setItem('refresh_token', refresh);
  },

  clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },

  isLoggedIn() { return !!this.getAccessToken(); },

  getUser() {
    try { return JSON.parse(localStorage.getItem('user') || 'null'); }
    catch { return null; }
  },

  setUser(user) { localStorage.setItem('user', JSON.stringify(user)); },

  async refreshToken() {
    const refresh = this.getRefreshToken();
    if (!refresh) return false;
    try {
      const res = await fetch(`${API_BASE}/auth/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
      });
      if (res.ok) {
        const data = await res.json();
        this.setTokens({ access: data.access, refresh: data.refresh });
        return true;
      }
      this.clearTokens();
      return false;
    } catch {
      return false;
    }
  },
};

// ── Requêtes HTTP avec retry JWT ──────────────────────────────────────────────

async function apiFetch(endpoint, options = {}) {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
  const isFormData = options.body instanceof FormData;

  const headers = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...options.headers,
  };

  const token = Auth.getAccessToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const config = { ...options, headers };

  try {
    let res = await fetch(url, config);

    // Tentative de refresh si 401
    if (res.status === 401 && Auth.getRefreshToken()) {
      const refreshed = await Auth.refreshToken();
      if (refreshed) {
        headers['Authorization'] = `Bearer ${Auth.getAccessToken()}`;
        res = await fetch(url, { ...config, headers });
      } else {
        Auth.clearTokens();
        window.location.href = '/login.html';
        return null;
      }
    }

    const contentType = res.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      const data = await res.json();
      return { ok: res.ok, status: res.status, data };
    }
    return { ok: res.ok, status: res.status, data: null };

  } catch (err) {
    // Hors ligne → mise en file d'attente
    if (!navigator.onLine) {
      OfflineQueue.add(endpoint, options);
      showOfflineAlert();
    }
    return { ok: false, status: 0, data: { message: window.i18n?.t('error.network') || 'Erreur réseau.' } };
  }
}

// ── Raccourcis API ────────────────────────────────────────────────────────────

const API = {
  // Auth
  async login(email, password) {
    const res = await apiFetch('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    if (res?.ok && res.data?.access) {
      Auth.setTokens({ access: res.data.access, refresh: res.data.refresh });
      await API.fetchMe();
    }
    return res;
  },

  async register(data) {
    const res = await apiFetch('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    if (res?.ok && res.data?.data?.tokens) {
      Auth.setTokens(res.data.data.tokens);
      Auth.setUser(res.data.data.user);
    }
    return res;
  },

  async logout() {
    const refresh = Auth.getRefreshToken();
    if (refresh) {
      await apiFetch('/auth/logout/', {
        method: 'POST',
        body: JSON.stringify({ refresh }),
      });
    }
    Auth.clearTokens();
    window.location.href = '/login.html';
  },

  async fetchMe() {
    const res = await apiFetch('/users/me/');
    if (res?.ok) Auth.setUser(res.data.data);
    return res;
  },

  // Cours
  getCourses(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return apiFetch(`/courses/?${qs}`);
  },

  getCourse(id)      { return apiFetch(`/courses/${id}/`); },
  getCategories()    { return apiFetch('/courses/categories/'); },
  getMyCourses()     { return apiFetch('/courses/my/'); },
  getEnrolledCourses() { return apiFetch('/courses/enrolled/'); },

  enrollCourse(id) {
    return apiFetch(`/courses/${id}/enroll/`, { method: 'POST' });
  },

  createCourse(formData) {
    return apiFetch('/courses/create/', { method: 'POST', body: formData });
  },

  addModule(courseId, formData) {
    return apiFetch(`/courses/${courseId}/modules/`, { method: 'POST', body: formData });
  },

  updateProgress(moduleId, percentage, lastPos) {
    return apiFetch(`/courses/modules/${moduleId}/progress/`, {
      method: 'POST',
      body: JSON.stringify({ percentage, last_position_seconds: lastPos }),
    });
  },

  rateCourse(courseId, stars, comment) {
    return apiFetch(`/courses/${courseId}/rate/`, {
      method: 'POST',
      body: JSON.stringify({ stars, comment }),
    });
  },

  // Social
  getFeed()       { return apiFetch('/social/feed/'); },
  likeFeedItem(id) {
    return apiFetch(`/social/feed/${id}/like/`, { method: 'POST' });
  },
  followUser(id) {
    return apiFetch(`/users/${id}/follow/`, { method: 'POST' });
  },
  unfollowUser(id) {
    return apiFetch(`/users/${id}/unfollow/`, { method: 'DELETE' });
  },
  getProfile(id) { return apiFetch(`/users/${id}/`); },

  // Modération
  getModerationQueue() { return apiFetch('/moderation/queue/'); },
  reviewCourse(courseId, decision, comment) {
    return apiFetch(`/moderation/courses/${courseId}/review/`, {
      method: 'POST',
      body: JSON.stringify({ decision, comment }),
    });
  },
  reportCourse(courseId, reason, details) {
    return apiFetch(`/moderation/courses/${courseId}/report/`, {
      method: 'POST',
      body: JSON.stringify({ course: courseId, reason, details }),
    });
  },

  // Réputation
  getBadges()      { return apiFetch('/reputation/badges/'); },
  getLeaderboard() { return apiFetch('/reputation/leaderboard/'); },
  getMyHistory()   { return apiFetch('/reputation/my-history/'); },
};

// ── Alertes offline / online ──────────────────────────────────────────────────

function showOfflineAlert() {
  let el = document.querySelector('.offline-alert');
  if (!el) {
    el = document.createElement('div');
    el.className = 'offline-alert';
    document.body.appendChild(el);
  }
  el.textContent = window.i18n?.t('offline.alert') || '📴 Hors ligne';
  el.classList.add('visible');
}

function showOnlineAlert() {
  let el = document.querySelector('.offline-alert');
  if (el) {
    el.textContent = window.i18n?.t('online.alert') || '✅ Reconnecté';
    el.classList.add('online-alert');
    setTimeout(() => {
      el.classList.remove('visible', 'online-alert');
    }, 3000);
  }
}

window.addEventListener('offline', showOfflineAlert);
window.addEventListener('online', () => {
  showOnlineAlert();
  OfflineQueue.flush();
  OfflineSync.sync();
});

// ── Notifications Toast ───────────────────────────────────────────────────────

function showToast(message, type = 'success', duration = 4000) {
  let container = document.querySelector('.toast-container-cam');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container-cam';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast-cam ${type === 'error' ? 'error' : type === 'warning' ? 'warning' : ''}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity .3s';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ── Helpers UI ────────────────────────────────────────────────────────────────

function updateNavAuth() {
  const user = Auth.getUser();
  const guestLinks  = document.querySelectorAll('.nav-guest');
  const authLinks   = document.querySelectorAll('.nav-auth');
  const modLinks    = document.querySelectorAll('.nav-mod');
  const instrLinks  = document.querySelectorAll('.nav-instructor');
  const userDisplay = document.getElementById('nav-user-name');

  if (user) {
    guestLinks.forEach(el => el.classList.add('d-none'));
    authLinks.forEach(el  => el.classList.remove('d-none'));
    if (userDisplay) userDisplay.textContent = user.first_name || user.username;
    if (['moderator','admin'].includes(user.role)) {
      modLinks.forEach(el => el.classList.remove('d-none'));
    }
    if (['instructor','admin'].includes(user.role)) {
      instrLinks.forEach(el => el.classList.remove('d-none'));
    }
  } else {
    guestLinks.forEach(el => el.classList.remove('d-none'));
    authLinks.forEach(el  => el.classList.add('d-none'));
  }
}

function renderStars(avg, max = 5) {
  let html = '';
  for (let i = 1; i <= max; i++) {
    if (i <= Math.round(avg)) html += '★';
    else html += '☆';
  }
  return `<span class="trust-stars">${html}</span>`;
}

function formatSize(mb) {
  if (mb >= 1000) return (mb / 1000).toFixed(1) + ' Go';
  return mb.toFixed(1) + ' Mo';
}

function formatDate(isoString) {
  const d = new Date(isoString);
  return d.toLocaleDateString(window.i18n?.lang === 'en' ? 'en-CM' : 'fr-CM');
}

document.addEventListener('DOMContentLoaded', updateNavAuth);

window.API   = API;
window.Auth  = Auth;
window.showToast = showToast;
window.renderStars = renderStars;
window.formatSize = formatSize;
window.formatDate = formatDate;
