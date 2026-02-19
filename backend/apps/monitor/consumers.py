import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()


class MonitorConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time student status monitoring.
    Handles live updates for student online/offline status and mode changes.
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.batch_id = self.scope['url_route']['kwargs']['batch_id']
        self.batch_group_name = f'monitor_batch_{self.batch_id}'
        
        # Authenticate user via JWT token
        token = self.scope['query_string'].decode().split('token=')[-1]
        user = await self.authenticate_token(token)
        
        if not user:
            await self.close()
            return
        
        self.scope['user'] = user
        
        # Join batch monitoring group
        await self.channel_layer.group_add(
            self.batch_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial student list
        students = await self.get_batch_students(self.batch_id)
        await self.send(text_data=json.dumps({
            'type': 'initial_load',
            'students': students
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'batch_group_name'):
            await self.channel_layer.group_discard(
                self.batch_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """
        Receive message from WebSocket.
        Expected format: {"type": "status_update", "student_id": 1, "status": "online", "mode": "normal"}
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'status_update':
                student_id = data.get('student_id')
                status = data.get('status')
                mode = data.get('mode')
                
                # Update student status in database
                student_data = await self.update_student_status(student_id, status, mode)
                
                # Broadcast to all clients in the batch group
                await self.channel_layer.group_send(
                    self.batch_group_name,
                    {
                        'type': 'status_broadcast',
                        'student_data': student_data
                    }
                )
        except json.JSONDecodeError:
            pass
    
    async def status_broadcast(self, event):
        """
        Receive broadcast from group and send to WebSocket.
        This is called when channel_layer.group_send is used.
        """
        student_data = event['student_data']
        
        await self.send(text_data=json.dumps({
            'type': 'status_broadcast',
            **student_data
        }))

    async def student_status(self, event):
        """
        Receive student status update from StudentConsumer
        """
        await self.send(text_data=json.dumps(event))

    async def submission_event(self, event):
        """
        Receive submission event (submission_received)
        """
        await self.send(text_data=json.dumps(event))
    
    @database_sync_to_async
    def authenticate_token(self, token_string):
        """Authenticate user from JWT token"""
        try:
            access_token = AccessToken(token_string)
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)
            return user
        except Exception:
            return None
    
    @database_sync_to_async
    def get_batch_students(self, batch_id):
        """Get all students in the batch"""
        from apps.students.models import Student
        from apps.students.serializers import StudentSerializer
        
        students = Student.objects.filter(batch_id=batch_id)
        serializer = StudentSerializer(students, many=True)
        return serializer.data
    
    @database_sync_to_async
    def update_student_status(self, student_id, status, mode):
        """Update student status and mode in database"""
        from apps.students.models import Student
        from django.utils import timezone
        
        try:
            student = Student.objects.get(id=student_id)
            
            if status:
                student.status = status
                student.last_seen = timezone.now()
            
            if mode:
                student.current_mode = mode
            
            student.save()
            
            return {
                'student_id': student.id,
                'student_name': student.name,
                'pc_id': student.pc_id,
                'status': student.status,
                'mode': student.current_mode,
                'last_seen': student.last_seen.isoformat() if student.last_seen else None
            }
        except Student.DoesNotExist:
            return None

class StudentConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for Students.
    Receives live updates for Lab Sessions, Tasks, Viva, Exams.
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        # Authenticate user via JWT token
        token = self.scope['query_string'].decode().split('token=')[-1]
        user = await self.authenticate_token(token)
        
        if not user:
            await self.close()
            return
        
        self.scope['user'] = user
        
        # Get student profile and batch
        student_data = await self.get_student_profile(user)
        if not student_data:
            await self.close()
            return
            
        self.student_id = student_data['id']
        self.batch_id = student_data['batch_id']
        self.batch_group_name = f'batch_{self.batch_id}'
        
        # Join batch group (for broadcast events)
        await self.channel_layer.group_add(
            self.batch_group_name,
            self.channel_name
        )
        
        # Join personal group (for individual events like Viva results)
        self.student_group_name = f'student_{self.student_id}'
        await self.channel_layer.group_add(
            self.student_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Mark as Online and Broadcast
        await self.broadcast_status('online')
        
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'batch_group_name'):
            await self.channel_layer.group_discard(
                self.batch_group_name,
                self.channel_name
            )
        
        if hasattr(self, 'student_group_name'):
             await self.channel_layer.group_discard(
                self.student_group_name,
                self.channel_name
            )
            
        # Mark as Offline and Broadcast
        if hasattr(self, 'student_id'):
            await self.broadcast_status('offline')

    async def session_status(self, event):
        """Receive session status update"""
        await self.send(text_data=json.dumps(event))

    async def task_event(self, event):
        """Receive task event (created, updated)"""
        await self.send(text_data=json.dumps(event))

    async def submission_event(self, event):
        """Receive submission event (evaluation_done)"""
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def authenticate_token(self, token_string):
        """Authenticate user from JWT token"""
        try:
            access_token = AccessToken(token_string)
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)
            return user
        except Exception:
            return None
            
    @database_sync_to_async
    def get_student_profile(self, user):
        """Get student ID and Batch ID"""
        try:
            student = user.student_profile
            return {'id': student.id, 'batch_id': student.batch.id}
        except Exception:
            return None

    @database_sync_to_async
    def update_student_status(self, student_id, status):
        """Update student status"""
        from apps.students.models import Student
        from django.utils import timezone
        try:
            student = Student.objects.get(id=student_id)
            student.status = status
            student.last_seen = timezone.now()
            student.save(update_fields=['status', 'last_seen'])
            return student
        except Student.DoesNotExist:
            return None

    async def broadcast_status(self, status):
        """Broadcast status change to Faculty Monitor group"""
        if not hasattr(self, 'batch_id'):
            return
            
        student = await self.update_student_status(self.student_id, status)
        if student:
            await self.channel_layer.group_send(
                f'monitor_batch_{self.batch_id}',
                {
                    'type': 'student_status',
                    'student_id': student.id,
                    'status': status,
                    'name': student.name,
                    'last_seen': student.last_seen.isoformat() if student.last_seen else None
                }
            )
