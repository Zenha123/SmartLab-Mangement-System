from django.db import models
from django.conf import settings

class ControlCommand(models.Model):
    COMMAND_CHOICES = [
        ('lock_pc', 'Lock PC'),
        ('unlock_pc', 'Unlock PC'),
        ('block_internet', 'Block Internet'),
        ('unblock_internet', 'Unblock Internet'),
        ('enable_usb', 'Enable USB'),
        ('disable_usb', 'Disable USB'),
        ('app_whitelist', 'App Whitelist'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('acknowledged', 'Acknowledged'),
        ('failed', 'Failed'),
    ]
    
    batch = models.ForeignKey('core.Batch', on_delete=models.CASCADE, related_name='control_commands')
    faculty = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    command_type = models.CharField(max_length=50, choices=COMMAND_CHOICES)
    payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'control_commands'
        ordering = ['-created_at']

class ControlState(models.Model):
    batch = models.OneToOneField('core.Batch', on_delete=models.CASCADE, related_name='control_state')
    pc_locked = models.BooleanField(default=False)
    internet_blocked = models.BooleanField(default=False)
    usb_disabled = models.BooleanField(default=False)
    whitelisted_apps = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'control_states'
