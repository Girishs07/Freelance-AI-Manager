import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_api():
    print("🚀 Testing Freelance AI Manager API\n")
    
    # Test 1: Basic connectivity
    print("1. Testing basic connectivity...")
    try:
        response = requests.get(f"{BASE_URL}/test")
        if response.status_code == 200:
            print("✅ API is running!")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ API test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Home endpoint
    print("2. Testing home endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Home endpoint works!")
            data = response.json()
            print(f"   API: {data['message']}")
            print(f"   Version: {data['version']}")
        else:
            print(f"❌ Home endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Home endpoint error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: User Registration
    print("3. Testing user registration...")
    test_user = {
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
        "skills": "Python, JavaScript, React",
        "experience_level": "intermediate",
        "hourly_rate": 50.0
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=test_user)
        if response.status_code == 201:
            print("✅ User registration successful!")
            user_data = response.json()
            print(f"   User ID: {user_data['user']['id']}")
            print(f"   Email: {user_data['user']['email']}")
            USER_ID = user_data['user']['id']
        elif response.status_code == 409:
            print("⚠️  User already exists, trying login...")
            # Try login instead
            login_data = {"email": test_user["email"], "password": test_user["password"]}
            response = requests.post(f"{BASE_URL}/login", json=login_data)
            if response.status_code == 200:
                print("✅ Login successful!")
                user_data = response.json()
                USER_ID = user_data['user']['id']
            else:
                print(f"❌ Login failed: {response.status_code}")
                return
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return
    
    print("\n" + "="*50 + "\n")
    
    # Test 4: Job Search (this might have limitations due to web scraping)
    print("4. Testing job search...")
    try:
        response = requests.get(f"{BASE_URL}/jobs/search/{USER_ID}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Job search completed!")
            print(f"   Total found: {data.get('total_found', 0)}")
            print(f"   High match jobs: {data.get('high_match_jobs', 0)}")
        else:
            print(f"⚠️  Job search had issues: {response.json()}")
    except Exception as e:
        print(f"❌ Job search error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 5: Get Jobs
    print("5. Testing get jobs...")
    try:
        response = requests.get(f"{BASE_URL}/jobs/{USER_ID}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved {len(data['jobs'])} jobs!")
        else:
            print(f"⚠️  Get jobs response: {response.status_code}")
    except Exception as e:
        print(f"❌ Get jobs error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 6: Create Project
    print("6. Testing project creation...")
    test_project = {
        "user_id": USER_ID,
        "title": "Test Web Development Project",
        "client_name": "Test Client",
        "description": "A sample project for testing",
        "budget": 1500.0
    }
    
    try:
        response = requests.post(f"{BASE_URL}/projects", json=test_project)
        if response.status_code == 201:
            print("✅ Project created successfully!")
            project_data = response.json()
            print(f"   Project: {project_data['project']['title']}")
            PROJECT_ID = project_data['project']['id']
        else:
            print(f"❌ Project creation failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            PROJECT_ID = None
    except Exception as e:
        print(f"❌ Project creation error: {e}")
        PROJECT_ID = None
    
    print("\n" + "="*50 + "\n")
    
    # Test 7: Time Logging
    if PROJECT_ID:
        print("7. Testing time logging...")
        time_log_data = {
            "user_id": USER_ID,
            "project_id": PROJECT_ID,
            "description": "Working on frontend development",
            "hours": 3.5
        }
        
        try:
            response = requests.post(f"{BASE_URL}/time-logs", json=time_log_data)
            if response.status_code == 201:
                print("✅ Time logged successfully!")
                time_data = response.json()
                print(f"   Hours: {time_data['time_log']['hours']}")
            else:
                print(f"❌ Time logging failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Time logging error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 8: Analytics
    print("8. Testing analytics...")
    try:
        response = requests.get(f"{BASE_URL}/analytics/{USER_ID}")
        if response.status_code == 200:
            print("✅ Analytics retrieved successfully!")
            data = response.json()
            summary = data['summary']
            print(f"   Total earnings: ${summary['total_earnings']}")
            print(f"   Total hours: {summary['total_hours']}")
            print(f"   Active projects: {summary['active_projects']}")
        else:
            print(f"❌ Analytics failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Analytics error: {e}")
    
    print("\n" + "="*50 + "\n")
    print("🎉 API testing completed!")

if __name__ == "__main__":
    test_api()