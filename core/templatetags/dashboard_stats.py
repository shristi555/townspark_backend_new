from django import template
from django.apps import apps
from django.utils import timezone
import datetime

register = template.Library()

@register.simple_tag
def get_dashboard_stats():
    User = apps.get_model('accounts', 'User')
    Issue = apps.get_model('issues', 'Issue')
    Testimonial = apps.get_model('testimonial', 'Testimonial')

    return {
        'total_users': User.objects.count(),
        'open_issues': Issue.objects.filter(is_resolved=False).count(),
        'resolved_issues': Issue.objects.filter(is_resolved=True).count(),
        'total_testimonials': Testimonial.objects.count(),
    }

@register.simple_tag
def get_issue_trends():
    Issue = apps.get_model('issues', 'Issue')
    today = timezone.now()
    
    labels = []
    issue_data = []
    resolved_data = []
    
    for i in range(5, -1, -1):
        # Calculate month and year for i months ago
        # Simplified: just go back 30 days at a time
        date = today - datetime.timedelta(days=i*30)
        labels.append(date.strftime('%b'))
        
        # Get issues created in that calendar month
        issues_count = Issue.objects.filter(
            created_at__month=date.month,
            created_at__year=date.year
        ).count()
        
        # Get issues resolved in that calendar month
        resolved_count = Issue.objects.filter(
            is_resolved=True,
            resolved_at__month=date.month,
            resolved_at__year=date.year
        ).count()
        
        issue_data.append(issues_count)
        resolved_data.append(resolved_count)
        
    return {
        'labels': labels,
        'issue_data': issue_data,
        'resolved_data': resolved_data,
    }
