from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_date

from accounts.models import User
from issues.models import Issue, IssueCategory
from .serializers import UserSearchSerializer, IssueSearchSerializer, SuggestionSerializer

class UniversalSearchView(APIView):
    """
    Search for issues and people with various filters.
    
    Filters:
    - q: Search string (title, description, name, email)
    - type: 'all', 'issue', 'person'
    - category: Category name
    - start_date: YYYY-MM-DD
    - end_date: YYYY-MM-DD
    - status: 'resolved', 'pending', 'archived'
    """
    def get(self, request):
        query = request.query_params.get('q', '')
        search_type = request.query_params.get('type', 'all')
        category = request.query_params.get('category')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        issue_status = request.query_params.get('status')

        results = {
            'issues': [],
            'people': []
        }

        # Search Issues
        if search_type in ['all', 'issue']:
            issues = Issue.objects.all().select_related('reported_by').prefetch_related('images', 'likes', 'comments')
            
            if query:
                issues = issues.filter(
                    Q(title__icontains=query) | 
                    Q(description__icontains=query) |
                    Q(address__icontains=query) |
                    Q(city__icontains=query) |
                    Q(reported_by__email__icontains=query) |
                    Q(reported_by__first_name__icontains=query) |
                    Q(reported_by__last_name__icontains=query)
                )

            if category and category != 'all':
                issues = issues.filter(category__icontains=category)
            
            if start_date:
                parsed_start = parse_date(start_date)
                if parsed_start:
                    issues = issues.filter(created_at__date__gte=parsed_start)
            
            if end_date:
                parsed_end = parse_date(end_date)
                if parsed_end:
                    issues = issues.filter(created_at__date__lte=parsed_end)
            
            if issue_status:
                if issue_status == 'resolved':
                    issues = issues.filter(is_resolved=True)
                elif issue_status == 'pending':
                    issues = issues.filter(is_resolved=False, is_archived=False)
                elif issue_status == 'archived':
                    issues = issues.filter(is_archived=True)

            results['issues'] = IssueSearchSerializer(issues[:50], many=True).data

        # Search People
        if search_type in ['all', 'person']:
            users = User.objects.all()
            if query:
                users = users.filter(
                    Q(email__icontains=query) |
                    Q(first_name__icontains=query) |
                    Q(last_name__icontains=query)
                )
            
            if start_date:
                parsed_start = parse_date(start_date)
                if parsed_start:
                    users = users.filter(created_at__date__gte=parsed_start)

            results['people'] = UserSearchSerializer(users[:50], many=True).data

        return Response(results)

class SuggestionView(APIView):
    """
    Provide autocomplete suggestions for search.
    """
    def get(self, request):
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response([])

        suggestions = []

        # Issue title and place suggestions
        issues = Issue.objects.filter(
            Q(title__icontains=query) | 
            Q(address__icontains=query) | 
            Q(city__icontains=query)
        ).distinct()[:3]
        
        for issue in issues:
            suggestions.append({
                'text': issue.title,
                'type': 'issue',
                'id': issue.id,
                'extra': issue.address.split(',')[0] if issue.address else None
            })

        # Person name suggestions
        users = User.objects.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )[:3]
        for user in users:
            suggestions.append({
                'text': user.get_full_name() or user.email,
                'type': 'person',
                'id': user.id
            })

        # Category suggestions
        from issues.models import IssueCategory
        categories = IssueCategory.objects.filter(name__icontains=query)[:3]
        for cat in categories:
            suggestions.append({
                'text': cat.name,
                'type': 'category',
                'id': cat.id
            })

        return Response(suggestions)
