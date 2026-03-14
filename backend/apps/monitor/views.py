from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json

from .models import ControlCommand, ControlState
from .serializers import ControlCommandSerializer, ControlStateSerializer
from apps.core.models import Batch

class ControlViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='command')
    def send_command(self, request):
        """
        Faculty issues a control command.
        POST /api/control/command/
        { "batch": <id>, "command_type": "lock_pc", "payload": {} }
        """
        batch_id = request.data.get('batch')
        command_type = request.data.get('command_type')
        payload = request.data.get('payload', {})

        if not batch_id or not command_type:
            return Response({'error': 'batch and command_type are required'}, status=status.HTTP_400_BAD_REQUEST)

        batch = get_object_or_404(Batch, id=batch_id)
        
        # Create ControlCommand record
        command = ControlCommand.objects.create(
            batch=batch,
            faculty=request.user,
            command_type=command_type,
            payload=payload
        )

        # Update ControlState
        state, created = ControlState.objects.get_or_create(batch=batch)
        if command_type == 'lock_pc':
            state.pc_locked = True
        elif command_type == 'unlock_pc':
            state.pc_locked = False
        elif command_type == 'block_internet':
            state.internet_blocked = True
        elif command_type == 'unblock_internet':
            state.internet_blocked = False
        elif command_type == 'disable_usb':
            state.usb_disabled = True
        elif command_type == 'enable_usb':
            state.usb_disabled = False
        elif command_type == 'app_whitelist':
            state.whitelisted_apps = payload.get('apps', [])
        
        state.save()

        # Broadcast via WebSocket to students in the batch
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'batch_{batch_id}',
            {
                'type': 'control_command',
                'command_id': command.id,
                'command_type': command_type,
                'payload': payload,
                'batch_id': batch_id
            }
        )

        return Response(ControlCommandSerializer(command).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='state')
    def get_state(self, request):
        """
        Student app fetches current state on startup.
        GET /api/control/state/?batch=<id>
        """
        batch_id = request.query_params.get('batch')
        if not batch_id:
            return Response({'error': 'batch id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        state, created = ControlState.objects.get_or_create(batch_id=batch_id)
        return Response(ControlStateSerializer(state).data)

    @action(detail=False, methods=['post'], url_path='ack')
    def acknowledge_command(self, request):
        """
        Student app acknowledges command execution.
        POST /api/control/ack/
        { "command_id": <id>, "status": "acknowledged" }
        """
        command_id = request.data.get('command_id')
        status_val = request.data.get('status', 'acknowledged')
        
        if not command_id:
            return Response({'error': 'command_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        command = get_object_or_404(ControlCommand, id=command_id)
        command.status = status_val
        command.save()

        # Notify Faculty via monitor group
        try:
            student_id = request.user.student_profile.id
            student_name = request.user.student_profile.name
        except Exception:
            student_id = None
            student_name = "Unknown"

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'monitor_batch_{command.batch.id}',
            {
                'type': 'control_ack',
                'command_id': command.id,
                'student_id': student_id,
                'student_name': student_name,
                'status': status_val,
                'command_type': command.command_type
            }
        )

        return Response({'status': 'updated'})
