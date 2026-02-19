from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import LabSession

@receiver(post_save, sender=LabSession)
def session_status_update(sender, instance, created, **kwargs):
    """
    Trigger WebSocket event when LabSession status changes.
    """
    channel_layer = get_channel_layer()
    batch_group_name = f'batch_{instance.batch.id}'
    
    event_type = None
    if created and instance.status == 'active':
        event_type = 'session_started'
    elif not created:
        # Check if status changed (simplified logic for now)
        if instance.status == 'active':
            event_type = 'session_started'
        elif instance.status == 'ended':
            event_type = 'session_ended'
        elif instance.status == 'paused':
            event_type = 'session_paused'
            
    if event_type:
        async_to_sync(channel_layer.group_send)(
            batch_group_name,
            {
                'type': 'session_status',  # Matches consumer method
                'status': event_type,
                'session_id': instance.id,
                'session_type': instance.session_type,
                'faculty_name': instance.faculty.name,
                'start_time': instance.start_time.isoformat() if instance.start_time else None,
                'end_time': instance.end_time.isoformat() if instance.end_time else None,
            }
        )
