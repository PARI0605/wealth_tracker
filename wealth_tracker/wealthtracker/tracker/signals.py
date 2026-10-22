from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from tracker.models import Category

DEFAULT_CATEGORIES = [
    {'name': 'Food & Dining', 'icon': 'bi-cup-hot', 'color': '#f59e0b'},
    {'name': 'Transportation', 'icon': 'bi-car-front', 'color': '#06b6d4'},
    {'name': 'Groceries', 'icon': 'bi-cart3', 'color': '#10b981'},
    {'name': 'Rent & Housing', 'icon': 'bi-house-door', 'color': '#6366f1'},
    {'name': 'Utilities & Bills', 'icon': 'bi-lightning-charge', 'color': '#eab308'},
    {'name': 'Entertainment', 'icon': 'bi-film', 'color': '#8b5cf6'},
    {'name': 'Healthcare', 'icon': 'bi-heart-pulse', 'color': '#ef4444'},
    {'name': 'Shopping', 'icon': 'bi-bag', 'color': '#ec4899'},
    {'name': 'Salary & Income', 'icon': 'bi-cash-coin', 'color': '#059669'},
    {'name': 'Investments', 'icon': 'bi-graph-up-arrow', 'color': '#3b82f6'},
]


@receiver(post_save, sender=User)
def create_default_categories(sender, instance, created, **kwargs):
    """
    Automatically seeds default financial categories for newly registered users,
    ensuring they never start with a blank state.
    """
    if created:
        for cat in DEFAULT_CATEGORIES:
            Category.objects.get_or_create(
                user=instance,
                name=cat['name'],
                defaults={
                    'icon': cat['icon'],
                    'color': cat['color']
                }
            )


def seed_categories_for_existing_user(user):
    """Utility helper to seed default categories for existing users if empty."""
    for cat in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(
            user=user,
            name=cat['name'],
            defaults={
                'icon': cat['icon'],
                'color': cat['color']
            }
        )
