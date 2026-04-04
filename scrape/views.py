from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from celery.result import AsyncResult

from .tasks import get_ebay_homepage_results

# Create your views here.
class EbayScraperViewSet(viewsets.ViewSet):
    permission_classes = []

    @action(detail=False, methods=['post'], url_path='homepage')
    def homepage(self, request):

        # Trigger async task
        celery_task = get_ebay_homepage_results.delay()
        
        return Response(
            {
                "task_id": celery_task.id,
                "status": "pending",
                "message": "Homepage scraping task queued successfully"
            },
            status=status.HTTP_202_ACCEPTED
        )

    @action(detail=False, methods=['get'], url_path='task-status/(?P<task_id>[^/.]+)')
    def task_status(self, request, task_id=None):
        if not task_id:
            return Response(
                {"error": "task_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the Celery task result
        celery_task = AsyncResult(task_id)
        
        response_data = {
            "task_id": task_id,
            "status": celery_task.status.lower(),
        }
        
        if celery_task.successful():
            response_data["result"] = celery_task.result
        
        elif celery_task.failed():
            response_data["error"] = str(celery_task.info)
        
        elif celery_task.status == 'PROGRESS':
            response_data["progress"] = celery_task.info.get('current', 0)
        
        return Response(response_data)