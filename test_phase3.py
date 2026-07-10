"""
Phase 3 Project Management Tests

This test suite validates:
1. Project CRUD operations
2. Ownership authorization (THE CRITICAL SECURITY CHECK)
3. Error handling
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_phase3():
    print("\n" + "="*70)
    print("PHASE 3: PROJECT MANAGEMENT TESTS".center(70))
    print("="*70)

    # Setup: Create two users
    print("\n[SETUP] Creating two test users...")
    user1_email = f"user1_{int(datetime.now().timestamp())}@test.com"
    user2_email = f"user2_{int(datetime.now().timestamp())}@test.com"
    
    # Register User 1
    r = requests.post(f"{BASE_URL}/users/register", json={
        "email": user1_email,
        "username": f"user1_{int(datetime.now().timestamp())}",
        "password": "Password123!"
    })
    assert r.status_code == 200, f"User1 registration failed: {r.text}"
    user1_id = r.json()["id"]
    print(f"✅ User 1 created (ID: {user1_id})")

    # Register User 2
    r = requests.post(f"{BASE_URL}/users/register", json={
        "email": user2_email,
        "username": f"user2_{int(datetime.now().timestamp())}",
        "password": "Password123!"
    })
    assert r.status_code == 200, f"User2 registration failed: {r.text}"
    user2_id = r.json()["id"]
    print(f"✅ User 2 created (ID: {user2_id})")

    # Login both users
    r = requests.post(f"{BASE_URL}/users/login", json={
        "email": user1_email,
        "password": "Password123!"
    })
    user1_token = r.json()["access_token"]
    print(f"✅ User 1 logged in")

    r = requests.post(f"{BASE_URL}/users/login", json={
        "email": user2_email,
        "password": "Password123!"
    })
    user2_token = r.json()["access_token"]
    print(f"✅ User 2 logged in")

    # Test 1: User 1 creates a project
    print("\n[TEST 1] User 1 creates a project...")
    r = requests.post(f"{BASE_URL}/projects", json={
        "name": "User 1 Secret Project",
        "description": "Only User 1 should see this"
    }, params={"token": user1_token})
    assert r.status_code == 201, f"Project creation failed: {r.text}"
    project1 = r.json()
    project1_id = project1["id"]
    assert project1["owner_id"] == user1_id, "Owner ID mismatch!"
    print(f"✅ Project created (ID: {project1_id}, Owner: {project1['owner_id']})")

    # Test 2: User 1 lists projects (should see 1)
    print("\n[TEST 2] User 1 lists their projects...")
    r = requests.get(f"{BASE_URL}/projects", params={"token": user1_token})
    assert r.status_code == 200
    projects = r.json()
    assert len(projects) >= 1, "User1 should see at least 1 project"
    assert any(p["id"] == project1_id for p in projects), "User1 should see their own project"
    print(f"✅ User 1 can see {len(projects)} project(s)")

    # Test 3: User 2 lists projects (should NOT see User 1's project)
    print("\n[TEST 3] User 2 lists their projects (should be empty)...")
    r = requests.get(f"{BASE_URL}/projects", params={"token": user2_token})
    assert r.status_code == 200
    projects = r.json()
    assert not any(p["id"] == project1_id for p in projects), "User2 should NOT see User1's project!"
    print(f"✅ User 2 correctly sees {len(projects)} project(s) (not User1's)")

    # Test 4: User 2 tries to GET User 1's project (CRITICAL AUTHORIZATION TEST)
    print("\n[TEST 4] User 2 tries to READ User 1's project - SHOULD FAIL...")
    r = requests.get(f"{BASE_URL}/projects/{project1_id}", params={"token": user2_token})
    print(f"   Status: {r.status_code}, Response: {r.json()}")
    assert r.status_code == 403, f"AUTHORIZATION FAILED! User2 should NOT access User1's project. Got {r.status_code}"
    print(f"✅ Correctly blocked (403 Forbidden)")

    # Test 5: User 2 tries to UPDATE User 1's project (CRITICAL AUTHORIZATION TEST)
    print("\n[TEST 5] User 2 tries to UPDATE User 1's project - SHOULD FAIL...")
    r = requests.put(f"{BASE_URL}/projects/{project1_id}", json={
        "name": "HACKED by User 2",
        "description": "User 2 is malicious"
    }, params={"token": user2_token})
    print(f"   Status: {r.status_code}, Response: {r.json()}")
    assert r.status_code == 403, f"AUTHORIZATION FAILED! User2 should NOT update User1's project. Got {r.status_code}"
    print(f"✅ Correctly blocked (403 Forbidden)")

    # Test 6: User 2 tries to DELETE User 1's project (CRITICAL AUTHORIZATION TEST)
    print("\n[TEST 6] User 2 tries to DELETE User 1's project - SHOULD FAIL...")
    r = requests.delete(f"{BASE_URL}/projects/{project1_id}", params={"token": user2_token})
    print(f"   Status: {r.status_code}, Response: {r.json()}")
    assert r.status_code == 403, f"AUTHORIZATION FAILED! User2 should NOT delete User1's project. Got {r.status_code}"
    print(f"✅ Correctly blocked (403 Forbidden)")

    # Test 7: User 1 updates their own project (SHOULD WORK)
    print("\n[TEST 7] User 1 updates their own project - SHOULD WORK...")
    r = requests.put(f"{BASE_URL}/projects/{project1_id}", json={
        "name": "Updated by Owner",
        "description": "This should work"
    }, params={"token": user1_token})
    assert r.status_code == 200, f"Update failed: {r.text}"
    updated = r.json()
    assert updated["name"] == "Updated by Owner", "Name not updated!"
    print(f"✅ Project updated successfully")

    # Test 8: User 1 deletes their own project (SHOULD WORK)
    print("\n[TEST 8] User 1 deletes their own project - SHOULD WORK...")
    r = requests.delete(f"{BASE_URL}/projects/{project1_id}", params={"token": user1_token})
    assert r.status_code == 200, f"Delete failed: {r.text}"
    print(f"✅ Project deleted successfully")

    # Test 9: Try to access deleted project (SHOULD BE 404)
    print("\n[TEST 9] User 1 tries to access deleted project - SHOULD BE 404...")
    r = requests.get(f"{BASE_URL}/projects/{project1_id}", params={"token": user1_token})
    assert r.status_code == 404, f"Should be 404, got {r.status_code}"
    print(f"✅ Correctly returns 404")

    # Test 10: Missing token
    print("\n[TEST 10] Request without token - SHOULD FAIL...")
    r = requests.get(f"{BASE_URL}/projects")
    assert r.status_code == 401, f"Should be 401, got {r.status_code}"
    print(f"✅ Correctly blocks missing token (401)")

    # Test 11: Invalid token
    print("\n[TEST 11] Request with invalid token - SHOULD FAIL...")
    r = requests.get(f"{BASE_URL}/projects", params={"token": "invalid.token.here"})
    assert r.status_code == 401, f"Should be 401, got {r.status_code}"
    print(f"✅ Correctly blocks invalid token (401)")

    print("\n" + "="*70)
    print("✅ ALL PHASE 3 AUTHORIZATION TESTS PASSED!".center(70))
    print("="*70)
    print("\nKey findings:")
    print("✅ Users can only see their own projects")
    print("✅ Users cannot read other users' projects (403)")
    print("✅ Users cannot update other users' projects (403)")
    print("✅ Users cannot delete other users' projects (403)")
    print("✅ Users can read/update/delete their own projects")
    print("✅ Deleted projects return 404")
    print("✅ Missing/invalid tokens are rejected")

if __name__ == "__main__":
    try:
        test_phase3()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        exit(1)
