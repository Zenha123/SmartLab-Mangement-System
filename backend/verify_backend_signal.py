import os
import django
import asyncio
import json
from channels.layers import get_channel_layer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.lab_sessions.models import LabSession
from apps.core.models import Batch
from apps.accounts.models import User

async def verify_signal():
    print("🧪 Starting Backend Signal Verification...")
    
    # 1. Get Channel Layer
    channel_layer = get_channel_layer()
    batch_name = "Batch A"
    try:
        batch = Batch.objects.get(name=batch_name)
    except Batch.DoesNotExist:
        print(f"❌ Batch '{batch_name}' not found. Run setup_test_data.py first.")
        return

    group_name = f"batch_{batch.id}"
    print(f"📡 Subscribing to Redis group: {group_name}")

    # 2. Create a specific channel to listen
    # In a real test, we'd add a consumer, but here we can't easily "listen" without a consumer 
    # hooked up to the layer. 
    # However, we can simulate being in the group?
    # Actually, channels_redis allows receiving from a channel if we know its name.
    # But groups broadcast to *specific channels* that joined the group.
    # So we need to:
    #   a. Create a temp channel name
    #   b. Add it to the group
    #   c. Trigger the signal
    #   d. Receive from the temp channel
    
    test_channel = await channel_layer.new_channel()
    await channel_layer.group_add(group_name, test_channel)
    print(f"✅ Joined group {group_name} with channel {test_channel}")

    # 3. Trigger Signal (Sync DB operation)
    print("📝 Creating/Updating Lab Session to trigger signal...")
    await asyncio.to_thread(trigger_db_change, batch)

    # 4. Receive Message
    print("⏳ Waiting for WebSocket message...")
    try:
        message = await asyncio.wait_for(channel_layer.receive(test_channel), timeout=5.0)
        print("\n🎉 MESSAGE RECEIVED!")
        print(json.dumps(message, indent=2))
        
        if message.get('type') == 'session_status' and message.get('status') == 'session_started':
             print("\n✅ SUCCESS: Signal fired and message delivered via Redis!")
        else:
             print("\n⚠️ WARNING: Message received but content unexpected.")
             
    except asyncio.TimeoutError:
        print("\n❌ TIMEOUT: No message received in 5 seconds. Signal might not be firing.")

    # Cleanup
    await channel_layer.group_discard(group_name, test_channel)

def trigger_db_change(batch):
    # Find Faculty
    faculty = User.objects.filter(is_staff=True).first()
    
    # Create or Update Session
    session = LabSession.objects.create(
        faculty=faculty,
        batch=batch,
        session_type='regular',
        status='active' # This triggers session_started
    )
    print(f"   -> LabSession {session.id} created with status 'active'")

if __name__ == "__main__":
    asyncio.run(verify_signal())
