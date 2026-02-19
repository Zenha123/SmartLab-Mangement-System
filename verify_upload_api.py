from student.api_client import authenticate, submit_task
import os
import time

def create_test_file():
    """Create a dummy file to upload"""
    filename = f"test_submission_{int(time.time())}.txt"
    with open(filename, 'w') as f:
        f.write("print('Hello from test upload')")
    return filename

def test_upload():
    print("Testing File Upload...")
    
    # Authenticate
    print("Authenticating...")
    token = authenticate("S001", "password123")
    if not token:
        print("❌ Auth failed")
        return
    print("✅ Authenticated")
    
    # Create file
    test_file = create_test_file()
    print(f"Created test file: {test_file}")
    
    # Submit (using a hardcoded task ID - needs to exist in DB)
    # We'll assume Task ID 1 exists from previous setup
    task_id = 1 
    
    print(f"Submitting file for Task {task_id}...")
    result = submit_task(task_id, os.path.abspath(test_file))
    
    if result.get("success"):
        print("✅ Upload Success!")
        print(f"API Response: {result}")
        
        # Verify file path in response
        data = result.get('data', {})
        file_path = data.get('file_url')
        print(f"File Path stored: {file_path}")
        
        if file_path and 'submissions' in file_path:
             print("✅ File path looks correct")
        else:
             print("⚠️ File path format unexpected")
             
    else:
        print(f"❌ Upload Failed: {result.get('error')}")
    
    # Cleanup
    try:
        os.remove(test_file)
        print("Cleaned up test file")
    except:
        pass

if __name__ == "__main__":
    test_upload()
