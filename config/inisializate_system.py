import os
import random
from collections import OrderedDict
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from faker import Faker
from django.contrib.auth.models import Group, User
from app.models import (
    Person, ProfileUser, SystemRol, ProfileSystemRol,
    AccessGroup, ModuleCategory, Module, ModulePermission, AccessGroupModule, Level, Language, TopicCategory,
    LearningModule, LearningContent, Exercise, Question, Choice
)

fake = Faker()

def create_user_with_role(username, full_name, email, rol_key, is_superuser=False, is_staff=False):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'is_superuser': is_superuser,
            'is_staff': is_staff
        }
    )
    if created:
        user.set_password('demo1234')
        user.save()
        print(f"✅ User created: {username}/demo1234")
    else:
        print(f"ℹ️ User {username} already exists.")

    person, _ = Person.objects.get_or_create(user=user, defaults={
        'names': full_name.split()[0],
        'surname1': full_name.split()[1] if len(full_name.split()) > 1 else '',
        'surname2': '',
        'email': email
    })

    profile_user, _ = ProfileUser.objects.get_or_create(person=person)

    rol = SystemRol.objects.get(name_key=rol_key)
    ProfileSystemRol.objects.get_or_create(
        profile=profile_user,
        system_rol=rol,
        defaults={'is_active': True, 'is_main': True}
    )

    return profile_user


def run():
    # Create system roles
    roles = [
        ('System Administrator', 'admin_system'),
        ('System Manager', 'system_manager'),
        ('Student', 'student'),
        ('Teacher', 'teacher'),
        ('Content Reviewer', 'content_reviewer'),
    ]
    for name, key in roles:
        SystemRol.objects.get_or_create(
            name=name,
            name_key=key,
            defaults={'description': f'Role: {name}', 'is_active': True}
        )

    # Create access group only for administrators
    django_group, _ = Group.objects.get_or_create(name='System Administrators')
    access_group, _ = AccessGroup.objects.get_or_create(group=django_group, defaults={
        'description': 'Group with full system access',
        'is_super_admin': True
    })

    categories_with_modules = OrderedDict({
        'Administration': [
            ('module_category', 'Categories', 'fa-layer-group'),
            ('access_group', 'Access Groups', 'fa-users-cog'),
            ('module', 'Modules', 'fa-cubes'),
            ('system_rol', 'System Roles', 'fa-user-shield'),
            ('user_profile', 'User Profiles', 'fa-user-tag'),
            ('group_module', 'Module Groups', 'fa-object-group'),
        ],
        'Language Learning': [
            ('language', 'Languages', 'fa-language'),
            ('language_level', 'Language Levels', 'fa-signal'),
            ('topic_category', 'Topic Categories', 'fa-tags'),
            ('learning_module', 'Learning Modules', 'fa-graduation-cap'),
            ('learning_content', 'Learning Content', 'fa-book-open'),
            ('exercises', 'Exercises', 'fa-tasks'),
            ('exam_simulator', 'Exam Simulators', 'fa-clipboard-check'),
        ],
        'User Progress': [
            ('user_progress', 'User Progress', 'fa-chart-line'),
            ('achievements', 'Achievements', 'fa-trophy'),
            ('daily_goals', 'Daily Goals', 'fa-calendar-check'),
        ]
    })

    for cat_order, (category_name, modules) in enumerate(categories_with_modules.items(), start=1):
        category, _ = ModuleCategory.objects.get_or_create(
            name=category_name,
            defaults={
                'order': cat_order,
                'icon': 'fa-folder'  # Default folder icon for categories
            }
        )

        for mod_order, (code, label, icon) in enumerate(modules, start=1):
            module, _ = Module.objects.get_or_create(
                category=category,
                name=label,
                defaults={
                    'description': f'Module for managing {label.lower()}',
                    'url': f'/{code}/',
                    'icon': icon,
                    'order': mod_order,
                    'is_active': True,
                    'needs_permission': True
                }
            )

            # Create module permissions
            for codename, name in [
                ('view', f'Can view {label}'),
                ('edit', f'Can edit {label}'),
                ('delete', f'Can delete {label}'),
                ('manage', f'Can manage {label}')
            ]:
                ModulePermission.objects.get_or_create(
                    module=module,
                    code_name=codename,
                    defaults={'name': name, 'description': name}
                )

            # Create access group permissions
            agm, _ = AccessGroupModule.objects.get_or_create(
                access_group=access_group,
                module=module,
                defaults={
                    'can_view': True,
                    'can_edit': True,
                    'can_delete': True,
                    'can_manage': True
                }
            )

            # Associate module permissions with the group
            agm.permissions.set(module.permissions.all())

    # Create test users
    admin_profile = create_user_with_role('admin', 'Admin Root', 'admin@example.com', 'admin_system', True, True)
    admin_profile.access_groups.add(access_group)  # Only admin gets full access

    create_user_with_role('system', 'John System', 'system@example.com', 'system_manager')
    create_user_with_role('teacher', 'Anna Teacher', 'teacher@example.com', 'teacher')
    create_user_with_role('student', 'Peter Student', 'student@example.com', 'student')
    create_user_with_role('reviewer', 'Laura Reviewer', 'reviewer@example.com', 'content_reviewer')

    print("✅ Initialization complete with roles and test users.")


def create_cefr_levels(language):
    """Create CEFR levels (A1, A2, B1, B2, C1, C2) for a language"""
    levels = [
        ('A1', 'Beginner', 'Basic user'),
        ('A2', 'Elementary', 'Basic user'),
        ('B1', 'Intermediate', 'Independent user'),
        ('B2', 'Upper Intermediate', 'Independent user'),
        ('C1', 'Advanced', 'Proficient user'),
        ('C2', 'Proficiency', 'Proficient user'),
    ]

    created_levels = []
    for order, (short_name, name, description) in enumerate(levels, start=1):
        level, _ = Level.objects.get_or_create(
            language=language,
            short_name=short_name,
            defaults={
                'name': name,
                'description': f"{name} level ({description})",
                'order': order,
                'is_active': True
            }
        )
        created_levels.append(level)

    return created_levels


def create_english_topic_categories():
    print("🏷️ Creating English topic categories...")

    categories = [
        ('greetings', 'Greetings and Introductions', 'fa-handshake'),
        ('common_phrases', 'Common Phrases', 'fa-comment-dots'),
        ('numbers', 'Numbers and Dates', 'fa-sort-numeric-up'),
        ('food', 'Food and Drinks', 'fa-utensils'),
        ('travel', 'Travel and Directions', 'fa-map-marked-alt'),
        ('shopping', 'Shopping', 'fa-shopping-cart'),
        ('work', 'Work and Business', 'fa-briefcase'),
        ('hobbies', 'Hobbies and Interests', 'fa-gamepad'),
    ]

    english = Language.objects.get(code='en')

    for code, name, icon in categories:
        TopicCategory.objects.get_or_create(
            language=english,
            name=name,
            defaults={
                'icon': icon,
                'order': TopicCategory.objects.filter(language=english).count() + 1,
                'is_active': True
            }
        )
    print(f"  ✅ Created {len(categories)} topic categories")


def create_english_learning_modules():
    print("📚 Creating English learning modules...")

    english = Language.objects.get(code='en')
    a1_level = Level.objects.get(language=english, short_name='A1')

    # Módulos por nivel A1
    level_modules = [
        ('Basic Vocabulary A1', 'Essential A1 words and phrases'),
        ('Everyday Conversations A1', 'Common A1 dialogues'),
        ('Grammar Fundamentals A1', 'Basic A1 grammar'),
        ('Pronunciation Practice A1', 'A1 sounds and accent'),
    ]

    for title, desc in level_modules:
        LearningModule.objects.get_or_create(
            level=a1_level,
            title=title,
            defaults={
                'description': desc,
                'order': LearningModule.objects.filter(level=a1_level).count() + 1,
                'estimated_duration': 30,
                'is_active': True
            }
        )

    # Módulos por categoría temática
    for category in TopicCategory.objects.filter(language=english):
        LearningModule.objects.get_or_create(
            topic_category=category,
            title=f"{category.name} Practice",
            defaults={
                'description': f"Practice exercises for {category.name.lower()}",
                'order': 1,
                'estimated_duration': 30,
                'is_active': True
            }
        )

    print(f"  ✅ Created {LearningModule.objects.filter(level__language=english).count()} English modules")


def create_english_learning_contents():
    print("📝 Creating English learning contents...")

    english_modules = LearningModule.objects.filter(level__language__code='en')
    content_types = [ct[0] for ct in LearningContent.CONTENT_TYPES]

    for module in english_modules:
        for i in range(3):  # 3 contenidos por módulo
            LearningContent.objects.create(
                module=module,
                title=f"{module.title} - Part {i + 1}",
                content_type=random.choice(content_types),
                text_content='\n'.join(fake.paragraphs(nb=2)),
                order=i + 1,
                is_free=random.choice([True, False])
            )

    print(f"  ✅ Created {LearningContent.objects.filter(module__level__language__code='en').count()} English contents")


def create_english_exercises():
    print("💪 Creating English exercises with questions and choices...")

    english_contents = LearningContent.objects.filter(module__level__language__code='en')
    exercise_types = ['quiz', 'quiz', 'quiz', 'quiz']  # Solo tipo quiz como pediste

    for content in english_contents:
        for i in range(30):  # 2 ejercicios por contenido
            exercise = Exercise.objects.create(
                module=content.module,
                content=content,
                title=f"Exercise {i + 1}: {content.title}",
                description=fake.sentence(),
                max_score=100,
                order=i + 1,
                exercise_type=random.choice(exercise_types),
                difficulty=random.choice(['easy', 'medium', 'hard']),
                is_active=True
            )

            # Crear 5 preguntas por ejercicio
            for q_num in range(1, 6):
                question = Question.objects.create(
                    exercise=exercise,
                    question_type='mcq',
                    text=fake.sentence()[:-1] + "?",
                    explanation=fake.paragraph(),
                    order=q_num,
                    points=20
                )

                # Crear 4 opciones (1 correcta) por pregunta
                correct_answer = fake.word().capitalize()
                incorrect_answers = [fake.word().capitalize() for _ in range(3)]

                # Opción correcta
                Choice.objects.create(
                    question=question,
                    text=correct_answer,
                    is_correct=True,
                    feedback="Correct! " + fake.sentence()
                )

                # Opciones incorrectas
                for incorrect in incorrect_answers:
                    Choice.objects.create(
                        question=question,
                        text=incorrect,
                        is_correct=False,
                        feedback="Incorrect. " + fake.sentence()
                    )

    print(f"  ✅ Created:")
    print(f"     - {Exercise.objects.filter(module__level__language__code='en').count()} English exercises")
    print(f"     - {Question.objects.filter(exercise__module__level__language__code='en').count()} questions")
    print(f"     - {Choice.objects.filter(question__exercise__module__level__language__code='en').count()} choices")


def create_specialized_english_exercises():
    print("🎯 Creating specialized English exercises...")

    english = Language.objects.get(code='en')
    content_type_exercises = {
        'vocabulary': [
            ("Word Matching", "Match English words with their meanings"),
            ("Synonyms", "Find English words with similar meanings"),
            ("Antonyms", "Find English words with opposite meanings")
        ],
        'grammar': [
            ("Verb Conjugation", "Practice conjugating English verbs"),
            ("Sentence Structure", "Identify correct English sentence structures"),
            ("Tenses", "Practice different English verb tenses")
        ]
    }

    for content_type, exercises in content_type_exercises.items():
        contents = LearningContent.objects.filter(
            module__level__language=english,
            content_type=content_type
        )

        for content in contents:
            for title, desc in exercises:
                exercise = Exercise.objects.create(
                    module=content.module,
                    content=content,
                    title=f"{content.title}: {title}",
                    description=desc,
                    max_score=100,
                    order=Exercise.objects.filter(content=content).count() + 1,
                    exercise_type='quiz',
                    difficulty=random.choice(['easy', 'medium', 'hard']),
                    is_active=True
                )

                # Preguntas para ejercicios especializados
                for q_num in range(1, 6):
                    question = Question.objects.create(
                        exercise=exercise,
                        question_type='mcq',
                        text=f"What is the correct answer for this {content_type} question?",
                        explanation=fake.paragraph(),
                        order=q_num,
                        points=20
                    )

                    # Opciones más específicas para ejercicios especializados
                    if content_type == 'vocabulary':
                        correct = fake.word().capitalize()
                        incorrects = [fake.word().capitalize() for _ in range(3)]
                    else:  # grammar
                        correct = fake.sentence().capitalize()
                        incorrects = [fake.sentence().capitalize() for _ in range(3)]

                    Choice.objects.create(
                        question=question,
                        text=correct,
                        is_correct=True,
                        feedback="Correct! " + fake.sentence()
                    )

                    for incorrect in incorrects:
                        Choice.objects.create(
                            question=question,
                            text=incorrect,
                            is_correct=False,
                            feedback="Incorrect. " + fake.sentence()
                        )


def run_english_exercise_creation():
    print("\n" + "=" * 50)
    print("🇬🇧 Starting English-only exercise creation")
    print("=" * 50 + "\n")

    # 1. Configurar inglés
    english = Language.objects.filter(pk=1).first()

    # 2. Crear categorías temáticas en inglés
    # create_english_topic_categories()
    #
    # # 3. Crear módulos de aprendizaje en inglés
    # create_english_learning_modules()
    #
    # # 4. Crear contenidos en inglés
    # create_english_learning_contents()

    # 5. Crear ejercicios básicos en inglés
    create_english_exercises()

    # 6. Crear ejercicios especializados en inglés
    # create_specialized_english_exercises()

    # Resultados finales
    print("\n" + "=" * 50)
    print("🏆 English exercise creation complete!")
    print("=" * 50)
    print(f"  English Modules: {LearningModule.objects.filter(level__language=english).count()}")
    print(f"  English Contents: {LearningContent.objects.filter(module__level__language=english).count()}")
    print(f"  English Exercises: {Exercise.objects.filter(module__level__language=english).count()}")
    print(f"  English Questions: {Question.objects.filter(exercise__module__level__language=english).count()}")
    print(f"  English Choices: {Choice.objects.filter(question__exercise__module__level__language=english).count()}")
    print("=" * 50 + "\n")


# Ejecutar la creación
run_english_exercise_creation()
