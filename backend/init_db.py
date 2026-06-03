"""
Script d'initialisation de la base de données.
Crée : superadmin, modérateur, formateur + 3 cours de démonstration.

Usage : python init_db.py  (depuis le dossier backend/)
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from apps.courses.models import Category, Course, Module
from apps.reputation.models import Badge, UserBadge
from apps.reputation.services import grant_reputation

User = get_user_model()


def create_users():
    print("📦 Création des utilisateurs...")

    admin, created = User.objects.get_or_create(
        email='admin@elearning.cm',
        defaults={
            'username': 'admin_cameroun',
            'first_name': 'Admin',
            'last_name': 'Système',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
            'is_verified': True,
            'preferred_language': 'fr',
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print(f"  ✅ Superadmin créé : admin@elearning.cm / admin123")
    else:
        print(f"  ℹ️  Superadmin déjà existant")

    moderator, created = User.objects.get_or_create(
        email='moderateur@elearning.cm',
        defaults={
            'username': 'moderateur_cm',
            'first_name': 'Marie',
            'last_name': 'Modératrice',
            'role': 'moderator',
            'is_staff': True,
            'is_verified': True,
            'reputation_score': 150,
            'preferred_language': 'fr',
        }
    )
    if created:
        moderator.set_password('mod123456')
        moderator.save()
        print(f"  ✅ Modérateur créé : moderateur@elearning.cm / mod123456")

    instructor, created = User.objects.get_or_create(
        email='formateur@elearning.cm',
        defaults={
            'username': 'prof_cameroun',
            'first_name': 'Jean-Paul',
            'last_name': 'Formateur',
            'role': 'instructor',
            'is_verified': True,
            'reputation_score': 50,
            'bio': 'Expert en développement logiciel et entrepreneuriat numérique au Cameroun.',
            'skills': 'Python, Django, JavaScript, Entrepreneuriat',
            'preferred_language': 'fr',
        }
    )
    if created:
        instructor.set_password('form123456')
        instructor.save()
        print(f"  ✅ Formateur créé : formateur@elearning.cm / form123456")

    student, created = User.objects.get_or_create(
        email='etudiant@elearning.cm',
        defaults={
            'username': 'etudiant_cm',
            'first_name': 'Amina',
            'last_name': 'Étudiante',
            'role': 'student',
            'is_verified': True,
            'preferred_language': 'fr',
        }
    )
    if created:
        student.set_password('etud123456')
        student.save()
        print(f"  ✅ Étudiant créé : etudiant@elearning.cm / etud123456")

    return admin, moderator, instructor, student


def create_categories():
    print("\n📂 Création des catégories...")
    categories_data = [
        ('Agriculture & Élevage', 'Agriculture & Livestock', 'agriculture-elevage', '🌾'),
        ('NTIC & Informatique', 'ICT & Computing', 'ntic-informatique', '💻'),
        ('Santé & Médecine', 'Health & Medicine', 'sante-medecine', '🏥'),
        ('Éducation & Pédagogie', 'Education & Pedagogy', 'education-pedagogie', '📚'),
        ('Entrepreneuriat', 'Entrepreneurship', 'entrepreneuriat', '🚀'),
        ('Langues', 'Languages', 'langues', '🗣️'),
        ('Droit & Gouvernance', 'Law & Governance', 'droit-gouvernance', '⚖️'),
        ('Art & Culture', 'Art & Culture', 'art-culture', '🎨'),
        ('Environnement', 'Environment', 'environnement', '🌿'),
        ('Finance & Comptabilité', 'Finance & Accounting', 'finance-comptabilite', '💰'),
    ]
    categories = {}
    for name_fr, name_en, slug, icon in categories_data:
        cat, created = Category.objects.get_or_create(
            slug=slug,
            defaults={'name_fr': name_fr, 'name_en': name_en, 'icon': icon}
        )
        categories[slug] = cat
        if created:
            print(f"  ✅ {icon} {name_fr}")
    return categories


def create_badges():
    print("\n🏆 Création des badges...")
    badges_data = [
        ('premier-pas', 'Premier Pas', 'First Step', '🌱', 10, False,
         'A obtenu 10 points de réputation.', 'Reached 10 reputation points.'),
        ('contributeur', 'Contributeur', 'Contributor', '⭐', 50, False,
         'A obtenu 50 points de réputation.', 'Reached 50 reputation points.'),
        ('expert', 'Expert', 'Expert', '🏅', 100, False,
         'A obtenu 100 points de réputation.', 'Reached 100 reputation points.'),
        ('mentor', 'Mentor Académique', 'Academic Mentor', '🎓', 200, False,
         'A obtenu 200 points de réputation.', 'Reached 200 reputation points.'),
        ('champion-data', 'Champion de la Data', 'Data Champion', '📡', 0, True,
         'Publie uniquement des cours optimisés pour la faible bande passante.',
         'Publishes only courses optimized for low bandwidth.'),
        ('prof-hors-ligne', 'Prof Hors Ligne', 'Offline Teacher', '📴', 0, True,
         'Met ses cours à disposition pour une consultation hors connexion.',
         'Makes courses available for offline consultation.'),
        ('mentor-bilangue', 'Mentor Bilangue', 'Bilingual Mentor', '🇨🇲', 0, True,
         'Crée des cours en français et en anglais (bilingues).',
         'Creates courses in both French and English (bilingual).'),
        ('signaleur-vigilant', 'Signaleur Vigilant', 'Vigilant Reporter', '🔍', 0, True,
         'A signalé du contenu inapproprié avec succès.',
         'Successfully reported inappropriate content.'),
    ]
    for slug, name_fr, name_en, icon, score, special, desc_fr, desc_en in badges_data:
        badge, created = Badge.objects.get_or_create(
            slug=slug,
            defaults={
                'name_fr': name_fr, 'name_en': name_en,
                'icon': icon, 'required_score': score,
                'is_special': special,
                'description_fr': desc_fr, 'description_en': desc_en,
            }
        )
        if created:
            print(f"  ✅ {icon} {name_fr}")


def create_demo_courses(instructor, categories):
    print("\n📖 Création des cours de démonstration...")

    course1, created = Course.objects.get_or_create(
        title='Introduction à Python pour l\'Afrique',
        defaults={
            'instructor': instructor,
            'description': (
                'Apprenez Python de zéro avec des exemples adaptés au contexte africain '
                'et camerounais. Gestion de stocks, calculs agricoles, mobile money.'
            ),
            'category': categories.get('ntic-informatique'),
            'level': 'beginner',
            'language': 'fr',
            'status': 'approved',
            'is_low_bandwidth': True,
            'total_size_mb': 35.5,
            'enrollment_count': 142,
            'average_rating': 4.7,
            'rating_count': 38,
        }
    )
    if created:
        Module.objects.create(
            course=course1, title='Variables et Types de données', order=1,
            description='Comprendre les fondamentaux de Python.',
            duration_minutes=20, file_size_mb=8.5, is_downloadable=True,
        )
        Module.objects.create(
            course=course1, title='Fonctions et Modules', order=2,
            description='Organiser votre code avec des fonctions.',
            duration_minutes=25, file_size_mb=12.0, is_downloadable=True,
        )
        Module.objects.create(
            course=course1, title='Projet : Gestion de stocks agricoles', order=3,
            description='Application pratique : gérer les stocks d\'une ferme.',
            duration_minutes=30, file_size_mb=15.0, is_downloadable=True,
        )
        print(f"  ✅ Cours 1 : {course1.title}")

    course2, created = Course.objects.get_or_create(
        title='Entrepreneuriat Numérique au Cameroun / Digital Entrepreneurship',
        defaults={
            'instructor': instructor,
            'description': (
                'Lancez votre startup numérique au Cameroun. Business plan, Mobile Money, '
                'marketing digital, réseaux sociaux. Cours bilingue FR/EN.'
                '\nLaunch your digital startup in Cameroon. Business plan, Mobile Money, '
                'digital marketing, social networks. Bilingual FR/EN course.'
            ),
            'category': categories.get('entrepreneuriat'),
            'level': 'intermediate',
            'language': 'both',
            'status': 'approved',
            'is_low_bandwidth': False,
            'total_size_mb': 85.0,
            'enrollment_count': 87,
            'average_rating': 4.4,
            'rating_count': 21,
        }
    )
    if created:
        Module.objects.create(
            course=course2, title='L\'écosystème startup camerounais / Cameroonian startup ecosystem',
            order=1, duration_minutes=35, file_size_mb=25.0, is_downloadable=True,
        )
        Module.objects.create(
            course=course2, title='Mobile Money & FinTech', order=2,
            duration_minutes=40, file_size_mb=30.0, is_downloadable=False,
        )
        Module.objects.create(
            course=course2, title='Marketing Digital Africa / Digital Marketing Africa',
            order=3, duration_minutes=45, file_size_mb=30.0, is_downloadable=False,
        )
        print(f"  ✅ Cours 2 : {course2.title}")

    course3, created = Course.objects.get_or_create(
        title='Agriculture Durable et Smart Farming',
        defaults={
            'instructor': instructor,
            'description': (
                'Techniques agricoles modernes adaptées aux régions camerounaises : '
                'Adamaoua, Littoral, Sud-Ouest. Irrigation, permaculture, drones agricoles.'
            ),
            'category': categories.get('agriculture-elevage'),
            'level': 'beginner',
            'language': 'fr',
            'status': 'approved',
            'is_low_bandwidth': True,
            'total_size_mb': 42.0,
            'enrollment_count': 203,
            'average_rating': 4.9,
            'rating_count': 54,
        }
    )
    if created:
        Module.objects.create(
            course=course3, title='Sols et Cultures du Cameroun', order=1,
            duration_minutes=30, file_size_mb=14.0, is_downloadable=True,
        )
        Module.objects.create(
            course=course3, title='Techniques d\'Irrigation Économique', order=2,
            duration_minutes=25, file_size_mb=14.0, is_downloadable=True,
        )
        Module.objects.create(
            course=course3, title='Introduction aux Drones Agricoles', order=3,
            duration_minutes=20, file_size_mb=14.0, is_downloadable=True,
        )
        print(f"  ✅ Cours 3 : {course3.title}")

    return course1, course2, course3


def main():
    print("=" * 60)
    print("🇨🇲  Réseau Académique Camerounais — Initialisation DB")
    print("=" * 60)

    admin, moderator, instructor, student = create_users()
    categories = create_categories()
    create_badges()
    courses = create_demo_courses(instructor, categories)

    # Donner le badge "Premier Pas" à l'instructeur
    from apps.reputation.models import Badge, UserBadge
    try:
        badge = Badge.objects.get(slug='premier-pas')
        UserBadge.objects.get_or_create(user=instructor, badge=badge)
    except Badge.DoesNotExist:
        pass

    print("\n" + "=" * 60)
    print("✅ Initialisation terminée !")
    print("\nComptes créés :")
    print("  👤 Admin    : admin@elearning.cm       / admin123")
    print("  🛡️  Modérat. : moderateur@elearning.cm  / mod123456")
    print("  🎓 Formateur: formateur@elearning.cm   / form123456")
    print("  📚 Étudiant : etudiant@elearning.cm    / etud123456")
    print("\nLancez le serveur : python manage.py runserver")
    print("=" * 60)


if __name__ == '__main__':
    main()
