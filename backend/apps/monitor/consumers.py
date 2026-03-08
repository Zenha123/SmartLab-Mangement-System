import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from aiortc import RTCPeerConnection, RTCSessionDescription


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

        token = self.scope['query_string'].decode().split('token=')[-1]
        user = await self.authenticate_token(token)

        if not user:
            await self.close()
            return

        self.scope['user'] = user
        self.broadcast_group_name = f'batch_{self.batch_id}'

        # Join the monitor group (faculty-specific events)
        await self.channel_layer.group_add(
            self.batch_group_name,
            self.channel_name
        )

        # Join the broadcast group (session/task events)
        await self.channel_layer.group_add(
            self.broadcast_group_name,
            self.channel_name
        )

        await self.accept()


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
        
        if hasattr(self, 'broadcast_group_name'):
            await self.channel_layer.group_discard(
                self.broadcast_group_name,
                self.channel_name
            )


    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            print("Backend MonitorConsumer received:", data)

            if message_type == 'status_update':
                student_id = data.get('student_id')
                status = data.get('status')
                mode = data.get('mode')

                student_data = await self.update_student_status(student_id, status, mode)

                await self.channel_layer.group_send(
                    self.batch_group_name,
                    {
                        'type': 'status_broadcast',
                        'student_data': student_data
                    }
                )

            elif message_type == "monitor_offer":
                student_id = data.get("student_id")

                # Forward offer to the specific student
                await self.channel_layer.group_send(
                    f"student_{student_id}",
                    {
                        "type": "monitor_offer",
                        "offer": data.get("offer"),
                        "faculty_channel": self.channel_name,
                        "student_id": student_id
                    }
                )

            elif message_type == "monitor_ice":
                student_id = data.get("student_id")

                # FIX 3: ICE candidates from faculty must go to the STUDENT, not
                # back to the faculty group. Mirroring the same routing as monitor_offer.
                await self.channel_layer.group_send(
                    f"student_{student_id}",
                    {
                        "type": "monitor_ice",
                        "candidate": data.get("candidate"),
                        "student_id": student_id
                    }
                )

            elif message_type == "monitor_stop":
                student_id = data.get("student_id")

                await self.channel_layer.group_send(
                    f"student_{student_id}",
                    {
                        "type": "monitor_stop"
                    }
                )

        except json.JSONDecodeError:
            pass

    async def monitor_answer(self, event):
        """Receive answer from student group, forward to faculty WebSocket"""
        print("Faculty received answer event:", event)
        await self.send(text_data=json.dumps({
            "type": "monitor_answer",
            "answer": event["answer"],
            "student_id": event["student_id"]
        }))

    async def monitor_ice(self, event):
        """Receive ICE candidate from student, forward to faculty WebSocket"""
        await self.send(text_data=json.dumps({
            "type": "monitor_ice",
            "candidate": event["candidate"],
            "student_id": event["student_id"]
        }))

    async def status_broadcast(self, event):
        student_data = event['student_data']
        await self.send(text_data=json.dumps({
            'type': 'status_broadcast',
            **student_data
        }))

    async def student_status(self, event):
        await self.send(text_data=json.dumps(event))

    async def submission_event(self, event):
        await self.send(text_data=json.dumps(event))


    async def viva_event(self, event):
        """
        Receive viva event (viva_evaluated, viva_online_published).
        Called by channel_layer.group_send with type='viva_event'.
        """
        await self.send(text_data=json.dumps(event))
    

    @database_sync_to_async
    def authenticate_token(self, token_string):
        try:
            access_token = AccessToken(token_string)
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)
            return user
        except Exception:
            return None

    @database_sync_to_async
    def get_batch_students(self, batch_id):
        from apps.students.models import Student
        from apps.students.serializers import StudentSerializer

        students = Student.objects.filter(batch_id=batch_id)
        serializer = StudentSerializer(students, many=True)
        return serializer.data

    @database_sync_to_async
    def update_student_status(self, student_id, status, mode):
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
        token = self.scope['query_string'].decode().split('token=')[-1]
        user = await self.authenticate_token(token)

        if not user:
            await self.close()
            return

        self.scope['user'] = user

        student_data = await self.get_student_profile(user)
        if not student_data:
            await self.close()
            return

        self.student_id = student_data['id']
        self.batch_id = student_data['batch_id']
        # Fixed typo: changed monitor_batch__ to batch_
        self.batch_group_name = f'batch_{self.batch_id}'

        # Join batch group (for broadcast events like session start)
        await self.channel_layer.group_add(
            self.batch_group_name,
            self.channel_name
        )


        # Join personal group (for individual events like monitor_offer)
        self.student_group_name = f'student_{self.student_id}'
        await self.channel_layer.group_add(
            self.student_group_name,
            self.channel_name
        )

        await self.accept()
        self.pc = None
        self.faculty_channel = None

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

        if hasattr(self, 'student_id'):
            await self.broadcast_status('offline')

    async def session_status(self, event):
        await self.send(text_data=json.dumps(event))

    async def task_event(self, event):
        await self.send(text_data=json.dumps(event))

    async def submission_event(self, event):
        await self.send(text_data=json.dumps(event))

    async def viva_event(self, event):
        """Forward viva/exam events to student WebSocket"""
        await self.send(text_data=json.dumps(event))

    async def monitor_offer(self, event):
        """Forward offer down to the student's WebSocket client"""
        await self.send(text_data=json.dumps({
            "type": "monitor_offer",
            "offer": event["offer"],
            "student_id": event["student_id"]
        }))

    
    async def monitor_ice(self, event):
        """Forward ICE candidate down to the student's WebSocket client"""
        await self.send(text_data=json.dumps({
            "type": "monitor_ice",
            "candidate": event["candidate"],
            "student_id": event["student_id"]
        }))

    async def monitor_stop(self, event):
        """Forward stop signal to student's WebSocket client"""
        await self.send(text_data=json.dumps({
            "type": "monitor_stop"
        }))

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get("type")

            print("StudentConsumer received:", data)

            if message_type == "monitor_answer":
                # Forward answer back to faculty monitor group
                await self.channel_layer.group_send(
                    f"monitor_batch_{self.batch_id}",
                    {
                        "type": "monitor_answer",
                        "answer": data.get("answer"),
                        "student_id": data.get("student_id"),
                    }
                )

            elif message_type == "monitor_ice":
                # Forward student ICE candidates to faculty monitor group
                await self.channel_layer.group_send(
                    f"monitor_batch_{self.batch_id}",
                    {
                        "type": "monitor_ice",
                        "candidate": data.get("candidate"),
                        "student_id": data.get("student_id"),
                    }
                )

        except Exception as e:
            print("StudentConsumer receive error:", e)

    @database_sync_to_async
    def authenticate_token(self, token_string):
        try:
            access_token = AccessToken(token_string)
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)
            return user
        except Exception:
            return None

    @database_sync_to_async
    def get_student_profile(self, user):
        try:
            student = user.student_profile
            return {'id': student.id, 'batch_id': student.batch.id}
        except Exception:
            return None

    @database_sync_to_async
    def update_student_status(self, student_id, status):
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