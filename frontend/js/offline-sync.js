/**
 * offline-sync.js — Synchronisation hors ligne
 * Réseau Académique Camerounais
 *
 * Stratégie :
 *  1. La progression vidéo est sauvegardée dans localStorage immédiatement.
 *  2. Une file d'attente (OfflineQueue) conserve les requêtes POST ratées.
 *  3. À la reconnexion (event 'online'), tout est synchronisé avec l'API.
 *  4. Les modules téléchargés sont stockés dans Cache API (via SW).
 */

// ── File d'attente des requêtes offline ───────────────────────────────────────

const OfflineQueue = {
  STORAGE_KEY: 'offline_queue',

  getAll() {
    try { return JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '[]'); }
    catch { return []; }
  },

  add(endpoint, options) {
    const queue = this.getAll();
    queue.push({
      endpoint,
      method:  options.method || 'GET',
      body:    typeof options.body === 'string' ? options.body : null,
      addedAt: new Date().toISOString(),
    });
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(queue));
    console.log(`[OfflineQueue] Requête mise en attente : ${options.method} ${endpoint}`);
  },

  clear() { localStorage.removeItem(this.STORAGE_KEY); },

  async flush() {
    if (!navigator.onLine) return;
    const queue = this.getAll();
    if (!queue.length) return;

    console.log(`[OfflineQueue] Synchronisation de ${queue.length} requête(s)...`);
    const failed = [];

    for (const item of queue) {
      try {
        const headers = { 'Content-Type': 'application/json' };
        const token = Auth.getAccessToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const res = await fetch(`/api/v1${item.endpoint}`, {
          method:  item.method,
          headers,
          body:    item.body || undefined,
        });
        if (!res.ok) failed.push(item);
      } catch {
        failed.push(item);
      }
    }

    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(failed));
    if (failed.length === 0) {
      console.log('[OfflineQueue] Toutes les requêtes ont été synchronisées.');
    } else {
      console.warn(`[OfflineQueue] ${failed.length} requête(s) ont échoué.`);
    }
  },
};

// ── Progression hors ligne ────────────────────────────────────────────────────

const OfflineProgress = {
  STORAGE_KEY: 'offline_progress',

  get() {
    try { return JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '{}'); }
    catch { return {}; }
  },

  save(moduleId, percentage, lastPositionSeconds) {
    const data = this.get();
    data[moduleId] = {
      percentage: Math.min(100, Math.max(0, percentage)),
      last_position_seconds: lastPositionSeconds,
      completed: percentage >= 100,
      updatedAt: new Date().toISOString(),
    };
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
  },

  getForModule(moduleId) {
    return this.get()[moduleId] || { percentage: 0, last_position_seconds: 0, completed: false };
  },

  async syncAll() {
    if (!navigator.onLine || !Auth.isLoggedIn()) return;
    const data = this.get();
    const entries = Object.entries(data);
    if (!entries.length) return;

    console.log(`[OfflineProgress] Synchronisation de ${entries.length} module(s)...`);
    for (const [moduleId, progress] of entries) {
      await API.updateProgress(
        moduleId,
        progress.percentage,
        progress.last_position_seconds
      );
    }
    localStorage.removeItem(this.STORAGE_KEY);
    console.log('[OfflineProgress] Synchronisation terminée.');
  },
};

// ── Cours téléchargés ─────────────────────────────────────────────────────────

const DownloadedCourses = {
  STORAGE_KEY: 'downloaded_modules',

  get() {
    try { return JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '{}'); }
    catch { return {}; }
  },

  isDownloaded(moduleId) {
    return !!this.get()[moduleId];
  },

  markDownloaded(moduleId, moduleData) {
    const data = this.get();
    data[moduleId] = {
      ...moduleData,
      downloadedAt: new Date().toISOString(),
    };
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
  },

  remove(moduleId) {
    const data = this.get();
    delete data[moduleId];
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
  },

  getAll() { return Object.values(this.get()); },

  async downloadModule(moduleId, videoUrl, pdfUrl, title) {
    if (!('caches' in window)) {
      showToast(
        'Le téléchargement hors ligne n\'est pas supporté par votre navigateur.',
        'warning'
      );
      return false;
    }

    try {
      const cache = await caches.open('cam-elearning-offline-v1');
      const toCache = [];
      if (videoUrl) toCache.push(videoUrl);
      if (pdfUrl)   toCache.push(pdfUrl);

      await Promise.all(toCache.map(url => cache.add(url).catch(() => null)));
      this.markDownloaded(moduleId, { title, videoUrl, pdfUrl });

      showToast(
        window.i18n?.lang === 'en'
          ? `Module "${title}" downloaded for offline use.`
          : `Module « ${title} » téléchargé pour une utilisation hors ligne.`,
        'success'
      );
      return true;
    } catch (err) {
      console.error('[Download]', err);
      showToast(window.i18n?.t('error.generic') || 'Erreur.', 'error');
      return false;
    }
  },
};

// ── Sync globale ──────────────────────────────────────────────────────────────

const OfflineSync = {
  async sync() {
    await OfflineQueue.flush();
    await OfflineProgress.syncAll();
  },
};

// ── Auto-sync au chargement si online ────────────────────────────────────────

window.addEventListener('load', () => {
  if (navigator.onLine) {
    setTimeout(() => OfflineSync.sync(), 2000);
  }
});

// ── Sauvegarde automatique de progression vidéo ───────────────────────────────

function attachProgressTracking(videoEl, moduleId) {
  if (!videoEl || !moduleId) return;

  const saved = OfflineProgress.getForModule(moduleId);
  if (saved.last_position_seconds > 0) {
    videoEl.currentTime = saved.last_position_seconds;
  }

  let saveTimer = null;

  videoEl.addEventListener('timeupdate', () => {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => {
      const duration = videoEl.duration || 1;
      const percentage = (videoEl.currentTime / duration) * 100;
      OfflineProgress.save(moduleId, percentage, Math.floor(videoEl.currentTime));

      // Envoi API si online
      if (navigator.onLine) {
        API.updateProgress(moduleId, percentage, Math.floor(videoEl.currentTime))
          .catch(() => {});
      }
    }, 5000); // Sauvegarde toutes les 5 secondes de lecture
  });

  videoEl.addEventListener('ended', () => {
    OfflineProgress.save(moduleId, 100, Math.floor(videoEl.duration));
    if (navigator.onLine) {
      API.updateProgress(moduleId, 100, Math.floor(videoEl.duration));
    }
  });
}

// ── Mode économie de données ──────────────────────────────────────────────────

const DataSaver = {
  STORAGE_KEY: 'data_saver_mode',

  isActive() {
    return localStorage.getItem(this.STORAGE_KEY) === 'true';
  },

  toggle() {
    const active = !this.isActive();
    localStorage.setItem(this.STORAGE_KEY, active);
    this.apply();
    return active;
  },

  apply() {
    if (this.isActive()) {
      document.body.classList.add('data-saver');
      const bar = document.querySelector('.data-saver-bar');
      if (bar) bar.classList.remove('hidden');
    } else {
      document.body.classList.remove('data-saver');
      const bar = document.querySelector('.data-saver-bar');
      if (bar) bar.classList.add('hidden');
    }
  },
};

document.addEventListener('DOMContentLoaded', () => DataSaver.apply());

window.OfflineQueue     = OfflineQueue;
window.OfflineProgress  = OfflineProgress;
window.OfflineSync      = OfflineSync;
window.DownloadedCourses = DownloadedCourses;
window.DataSaver        = DataSaver;
window.attachProgressTracking = attachProgressTracking;
