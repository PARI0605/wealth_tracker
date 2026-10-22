from django.conf import settings


def ai_feature_flag(request):
    """
    Context processor providing SHOW_AI_FEATURES flag to all templates.
    Controls the visibility of AI and machine learning UI elements site-wide.
    """
    return {
        'SHOW_AI_FEATURES': getattr(settings, 'SHOW_AI_FEATURES', False)
    }
