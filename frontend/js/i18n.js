/**
 * i18n.js — Gestion bilingue FR / EN
 * Réseau Académique Camerounais
 */

const TRANSLATIONS = {
  fr: {
    // Navigation
    'nav.home': 'Accueil',
    'nav.courses': 'Cours',
    'nav.feed': 'Fil d\'actualité',
    'nav.profile': 'Profil',
    'nav.login': 'Connexion',
    'nav.register': 'Inscription',
    'nav.logout': 'Déconnexion',
    'nav.create_course': 'Créer un cours',
    'nav.moderation': 'Modération',

    // Catalogue
    'catalog.title': 'Catalogue des Cours',
    'catalog.search': 'Rechercher un cours...',
    'catalog.filter.all': 'Tous',
    'catalog.filter.low_bw': '📡 Faible bande passante',
    'catalog.filter.offline': '📴 Hors ligne',
    'catalog.empty': 'Aucun cours trouvé.',
    'catalog.load_more': 'Charger plus',
    'catalog.enrolled': 'inscrits',
    'catalog.rating': 'Note',
    'catalog.level.beginner': 'Débutant',
    'catalog.level.intermediate': 'Intermédiaire',
    'catalog.level.expert': 'Expert',
    'catalog.size': 'Mo',
    'catalog.free': 'Gratuit',
    'catalog.enroll': 'S\'inscrire',
    'catalog.view': 'Voir le cours',

    // Auth
    'auth.email': 'Email',
    'auth.password': 'Mot de passe',
    'auth.confirm_password': 'Confirmer le mot de passe',
    'auth.first_name': 'Prénom',
    'auth.last_name': 'Nom',
    'auth.username': 'Nom d\'utilisateur',
    'auth.phone': 'Téléphone (optionnel)',
    'auth.lang': 'Langue préférée',
    'auth.login_btn': 'Se connecter',
    'auth.register_btn': 'S\'inscrire',
    'auth.no_account': 'Pas encore de compte ?',
    'auth.have_account': 'Déjà un compte ?',
    'auth.forgot': 'Mot de passe oublié ?',
    'auth.role': 'Je suis',
    'auth.role.student': 'Étudiant(e)',
    'auth.role.instructor': 'Formateur/Formatrice',

    // Cours
    'course.by': 'par',
    'course.level': 'Niveau',
    'course.language': 'Langue',
    'course.modules': 'modules',
    'course.enroll': 'S\'inscrire gratuitement',
    'course.enrolled': 'Inscrit ✓',
    'course.progress': 'Ma progression',
    'course.download': 'Télécharger pour hors ligne',
    'course.report': 'Signaler ce cours',
    'course.rate': 'Noter ce cours',
    'course.rating_label': 'Votre note',
    'course.comment': 'Votre commentaire (optionnel)',
    'course.submit_rating': 'Envoyer la note',
    'course.rating_needed': 'Vous devez compléter 80% du cours pour noter.',
    'course.status.pending': 'En attente de validation',
    'course.status.approved': 'Approuvé',
    'course.status.rejected': 'Rejeté',
    'course.status.quarantine': 'Quarantaine',

    // Création cours
    'create.title': 'Créer un nouveau cours',
    'create.course_title': 'Titre du cours',
    'create.description': 'Description',
    'create.category': 'Catégorie',
    'create.level': 'Niveau',
    'create.language': 'Langue du cours',
    'create.thumbnail': 'Image de couverture',
    'create.add_module': '+ Ajouter un module',
    'create.submit': 'Soumettre pour validation',
    'create.module_title': 'Titre du module',
    'create.module_video': 'Vidéo (MP4, max 300 Mo)',
    'create.module_pdf': 'Document PDF (max 20 Mo)',
    'create.module_duration': 'Durée (minutes)',
    'create.downloadable': 'Disponible hors ligne',

    // Profil
    'profile.followers': 'Abonnés',
    'profile.following': 'Abonnements',
    'profile.courses': 'Cours créés',
    'profile.score': 'Score de réputation',
    'profile.badges': 'Badges',
    'profile.follow': 'Suivre',
    'profile.unfollow': 'Ne plus suivre',
    'profile.edit': 'Modifier le profil',
    'profile.skills': 'Compétences',
    'profile.verified': 'Compte vérifié ✓',
    'profile.not_verified': 'Email non vérifié',

    // Modération
    'mod.title': 'Tableau de bord — Modération',
    'mod.queue': 'File d\'attente',
    'mod.pending': 'En attente',
    'mod.quarantine': 'Quarantaine',
    'mod.approve': 'Approuver',
    'mod.reject': 'Rejeter',
    'mod.reason': 'Motif de rejet',
    'mod.reports': 'signalements',
    'mod.empty': 'Aucun cours à modérer. ✅',

    // Signalement
    'report.title': 'Signaler ce cours',
    'report.reason': 'Motif',
    'report.details': 'Détails (optionnel)',
    'report.submit': 'Envoyer le signalement',
    'report.reason.spam': 'Spam',
    'report.reason.low_quality': 'Faible qualité',
    'report.reason.factual_error': 'Erreur factuelle',
    'report.reason.inappropriate': 'Contenu inapproprié',

    // Réseau / Fil
    'feed.title': 'Fil d\'actualité',
    'feed.empty': 'Abonnez-vous à des formateurs pour voir leur actualité.',
    'feed.like': 'J\'aime',
    'feed.liked': 'Aimé ❤️',

    // Offline
    'offline.title': 'Vous êtes hors ligne',
    'offline.msg': 'Pas d\'inquiétude — vos cours téléchargés restent accessibles.',
    'offline.go_home': 'Revenir à l\'accueil',
    'offline.alert': '📴 Hors ligne — progression sauvegardée localement',
    'online.alert': '✅ Reconnecté — synchronisation en cours...',

    // Général
    'btn.save': 'Enregistrer',
    'btn.cancel': 'Annuler',
    'btn.close': 'Fermer',
    'btn.loading': 'Chargement...',
    'error.network': 'Erreur réseau. Vérifiez votre connexion.',
    'error.generic': 'Une erreur est survenue. Réessayez.',
    'success.saved': 'Enregistré avec succès.',
  },

  en: {
    'nav.home': 'Home',
    'nav.courses': 'Courses',
    'nav.feed': 'Feed',
    'nav.profile': 'Profile',
    'nav.login': 'Login',
    'nav.register': 'Sign up',
    'nav.logout': 'Logout',
    'nav.create_course': 'Create a course',
    'nav.moderation': 'Moderation',

    'catalog.title': 'Course Catalog',
    'catalog.search': 'Search courses...',
    'catalog.filter.all': 'All',
    'catalog.filter.low_bw': '📡 Low bandwidth',
    'catalog.filter.offline': '📴 Offline',
    'catalog.empty': 'No courses found.',
    'catalog.load_more': 'Load more',
    'catalog.enrolled': 'enrolled',
    'catalog.rating': 'Rating',
    'catalog.level.beginner': 'Beginner',
    'catalog.level.intermediate': 'Intermediate',
    'catalog.level.expert': 'Expert',
    'catalog.size': 'MB',
    'catalog.free': 'Free',
    'catalog.enroll': 'Enroll',
    'catalog.view': 'View course',

    'auth.email': 'Email',
    'auth.password': 'Password',
    'auth.confirm_password': 'Confirm password',
    'auth.first_name': 'First name',
    'auth.last_name': 'Last name',
    'auth.username': 'Username',
    'auth.phone': 'Phone (optional)',
    'auth.lang': 'Preferred language',
    'auth.login_btn': 'Sign in',
    'auth.register_btn': 'Create account',
    'auth.no_account': 'No account yet?',
    'auth.have_account': 'Already have an account?',
    'auth.forgot': 'Forgot password?',
    'auth.role': 'I am a',
    'auth.role.student': 'Student',
    'auth.role.instructor': 'Instructor',

    'course.by': 'by',
    'course.level': 'Level',
    'course.language': 'Language',
    'course.modules': 'modules',
    'course.enroll': 'Enroll for free',
    'course.enrolled': 'Enrolled ✓',
    'course.progress': 'My progress',
    'course.download': 'Download for offline',
    'course.report': 'Report this course',
    'course.rate': 'Rate this course',
    'course.rating_label': 'Your rating',
    'course.comment': 'Your comment (optional)',
    'course.submit_rating': 'Submit rating',
    'course.rating_needed': 'You must complete 80% of the course to rate it.',
    'course.status.pending': 'Pending validation',
    'course.status.approved': 'Approved',
    'course.status.rejected': 'Rejected',
    'course.status.quarantine': 'Quarantine',

    'create.title': 'Create a new course',
    'create.course_title': 'Course title',
    'create.description': 'Description',
    'create.category': 'Category',
    'create.level': 'Level',
    'create.language': 'Course language',
    'create.thumbnail': 'Cover image',
    'create.add_module': '+ Add a module',
    'create.submit': 'Submit for review',
    'create.module_title': 'Module title',
    'create.module_video': 'Video (MP4, max 300 MB)',
    'create.module_pdf': 'PDF document (max 20 MB)',
    'create.module_duration': 'Duration (minutes)',
    'create.downloadable': 'Available offline',

    'profile.followers': 'Followers',
    'profile.following': 'Following',
    'profile.courses': 'Courses created',
    'profile.score': 'Reputation score',
    'profile.badges': 'Badges',
    'profile.follow': 'Follow',
    'profile.unfollow': 'Unfollow',
    'profile.edit': 'Edit profile',
    'profile.skills': 'Skills',
    'profile.verified': 'Verified account ✓',
    'profile.not_verified': 'Email not verified',

    'mod.title': 'Moderation Dashboard',
    'mod.queue': 'Queue',
    'mod.pending': 'Pending',
    'mod.quarantine': 'Quarantine',
    'mod.approve': 'Approve',
    'mod.reject': 'Reject',
    'mod.reason': 'Rejection reason',
    'mod.reports': 'reports',
    'mod.empty': 'No courses to moderate. ✅',

    'report.title': 'Report this course',
    'report.reason': 'Reason',
    'report.details': 'Details (optional)',
    'report.submit': 'Submit report',
    'report.reason.spam': 'Spam',
    'report.reason.low_quality': 'Low quality',
    'report.reason.factual_error': 'Factual error',
    'report.reason.inappropriate': 'Inappropriate content',

    'feed.title': 'Activity Feed',
    'feed.empty': 'Follow instructors to see their activity.',
    'feed.like': 'Like',
    'feed.liked': 'Liked ❤️',

    'offline.title': 'You are offline',
    'offline.msg': 'Don\'t worry — your downloaded courses remain accessible.',
    'offline.go_home': 'Back to home',
    'offline.alert': '📴 Offline — progress saved locally',
    'online.alert': '✅ Reconnected — syncing...',

    'btn.save': 'Save',
    'btn.cancel': 'Cancel',
    'btn.close': 'Close',
    'btn.loading': 'Loading...',
    'error.network': 'Network error. Check your connection.',
    'error.generic': 'An error occurred. Please try again.',
    'success.saved': 'Saved successfully.',
  },
};

class I18n {
  constructor() {
    this.lang = localStorage.getItem('preferred_lang') || 'fr';
  }

  t(key) {
    return (TRANSLATIONS[this.lang] && TRANSLATIONS[this.lang][key])
      || (TRANSLATIONS['fr'][key])
      || key;
  }

  setLang(lang) {
    if (['fr', 'en'].includes(lang)) {
      this.lang = lang;
      localStorage.setItem('preferred_lang', lang);
      this.applyAll();
    }
  }

  toggle() {
    this.setLang(this.lang === 'fr' ? 'en' : 'fr');
  }

  applyAll() {
    // Applique les traductions aux éléments avec data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      el.textContent = this.t(key);
    });
    // Placeholders
    document.querySelectorAll('[data-i18n-ph]').forEach(el => {
      const key = el.getAttribute('data-i18n-ph');
      el.placeholder = this.t(key);
    });
    // Titles
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
      const key = el.getAttribute('data-i18n-title');
      el.title = this.t(key);
    });
    // Langue toggle button
    const btn = document.getElementById('lang-toggle-btn');
    if (btn) btn.textContent = this.lang === 'fr' ? '🇬🇧 EN' : '🇫🇷 FR';

    document.documentElement.lang = this.lang;
  }
}

window.i18n = new I18n();
document.addEventListener('DOMContentLoaded', () => {
  window.i18n.applyAll();
  const btn = document.getElementById('lang-toggle-btn');
  if (btn) btn.addEventListener('click', () => window.i18n.toggle());
});
