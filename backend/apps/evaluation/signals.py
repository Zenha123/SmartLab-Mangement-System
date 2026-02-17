from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Task

@receiver(post_save, sender=Task)
def task_created(sender, instance, created, **kwargs):
    """
    Trigger WebSocket event when a new Task is created.
    """
    if created:
        channel_layer = get_channel_layer()
        batch_group_name = f'batch_{instance.batch.id}'
        
        async_to_sync(channel_layer.group_send)(
            batch_group_name,
            {
                'type': 'task_event',  # Will be handled by Consumer
                'event_type': 'task_created',
                'task': {
                    'id': instance.id,
                    'title': instance.title,
                    'description': instance.description,
                    'status': instance.status,
                    'batch_id': instance.batch.id,
                    'created_at': instance.created_at.isoformat(),
                    'faculty_name': instance.faculty.name,
                    'deadline': instance.deadline.isoformat() if instance.deadline else None,
                }
            }
        )
