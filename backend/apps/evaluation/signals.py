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

@receiver(post_save, sender='evaluation.TaskSubmission')
def submission_event(sender, instance, created, **kwargs):
    """
    Trigger WebSocket events for task submissions.
    - created: submission_received (to faculty)
    - evaluated: evaluation_done (to student)
    """
    from apps.evaluation.models import TaskSubmission
    
    channel_layer = get_channel_layer()
    
    if created and instance.status == 'submitted':
        # Broadcast to faculty monitoring this batch
        batch_id = instance.task.batch.id
        faculty_group = f'monitor_batch_{batch_id}'
        
        async_to_sync(channel_layer.group_send)(
            faculty_group,
            {
                'type': 'submission_event',
                'event_type': 'submission_received',
                'submission': {
                    'id': instance.id,
                    'task_id': instance.task.id,
                    'task_title': instance.task.title,
                    'student_id': instance.student.id,
                    'student_name': instance.student.name,
                    'file_path': instance.file_path,
                    'submitted_at': instance.submitted_at.isoformat(),
                    'status': instance.status,
                }
            }
        )
    
    elif instance.status == 'evaluated':
        # Broadcast to specific student
        student_group = f'student_{instance.student.id}'
        
        async_to_sync(channel_layer.group_send)(
            student_group,
            {
                'type': 'submission_event',
                'event_type': 'evaluation_done',
                'submission': {
                    'id': instance.id,
                    'task_id': instance.task.id,
                    'task_title': instance.task.title,
                    'marks': instance.marks,
                    'feedback': instance.feedback,
                    'status': instance.status,
                }
            }
        )
