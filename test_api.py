"""
Simple API testing script.
Tests all endpoints without using pytest - just plain Python.
"""

import requests
import json
from datetime import datetime

# Base URL of API
BASE_URL = "http://localhost:8000"

def print_test(name):
    """Pretty print test name"""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print('='*60)

def print_result(response, description=""):
    """Pretty print response"""
    print(f"Status: {response.status_code}")
    if description:
        print(f"Description: {description}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

# Test data
test_email = f"testuser{datetime.now().timestamp()}@example.com"
test_username = f"testuser{int(datetime.now().timestamp())}"
test_password = "TestPassword123!"

print("\n" + "🚀 STARTING API TESTS 🚀".center(60))
print(f"Email: {test_email}")
print(f"Username: {test_username}")

# ============ TEST 1: Hello World ============
print_test("GET / (Hello World)")
response = requests.get(f"{BASE_URL}/")
print_result(response, "Should return hello world message")
assert response.status_code == 200, "Failed!"
print("✅ PASSED")

# ============ TEST 2: Health Check ============
print_test("GET /health")
response = requests.get(f"{BASE_URL}/health")
print_result(response, "Should return status ok")
assert response.status_code == 200, "Failed!"
assert response.json()["status"] == "ok", "Status not ok!"
print("✅ PASSED")

# ============ TEST 3: Register User ============
print_test("POST /users/register")
register_data = {
    "email": test_email,
    "username": test_username,
    "password": test_password
}
print(f"Sending: {json.dumps(register_data, indent=2)}")
response = requests.post(f"{BASE_URL}/users/register", json=register_data)
print_result(response, "Should create user and return user object without password")
assert response.status_code == 200, "Failed!"
user = response.json()
assert user["email"] == test_email, "Email doesn't match!"
assert user["username"] == test_username, "Username doesn't match!"
assert "hashed_password" not in user, "Password leaked in response!"
assert "id" in user, "No user ID!"
user_id = user["id"]
print("✅ PASSED")

# ============ TEST 4: Register Duplicate Email ============
print_test("POST /users/register (Duplicate Email - Should Fail)")
duplicate_data = {
    "email": test_email,  # Same email
    "username": f"different_user_{datetime.now().timestamp()}",
    "password": test_password
}
response = requests.post(f"{BASE_URL}/users/register", json=duplicate_data)
print_result(response, "Should return 400 error")
assert response.status_code == 400, f"Expected 400, got {response.status_code}"
assert "already registered" in response.json()["detail"].lower(), "Wrong error message!"
print("✅ PASSED (Correctly rejected duplicate)")

# ============ TEST 5: Login ============
print_test("POST /users/login")
login_data = {
    "email": test_email,
    "password": test_password
}
print(f"Sending: {json.dumps(login_data, indent=2)}")
response = requests.post(f"{BASE_URL}/users/login", json=login_data)
print_result(response, "Should return access token and user info")
assert response.status_code == 200, "Failed!"
login_response = response.json()
assert "access_token" in login_response, "No token!"
assert login_response["token_type"] == "bearer", "Wrong token type!"
assert "user" in login_response, "No user info!"
access_token = login_response["access_token"]
print(f"Token (first 50 chars): {access_token[:50]}...")
print("✅ PASSED")

# ============ TEST 6: Login Wrong Password ============
print_test("POST /users/login (Wrong Password - Should Fail)")
wrong_login = {
    "email": test_email,
    "password": "WrongPassword123!"
}
response = requests.post(f"{BASE_URL}/users/login", json=wrong_login)
print_result(response, "Should return 401 error")
assert response.status_code == 401, f"Expected 401, got {response.status_code}"
assert "Invalid" in response.json()["detail"], "Wrong error message!"
print("✅ PASSED (Correctly rejected wrong password)")

# ============ TEST 7: Get Current User ============
print_test("GET /users/me")
headers = {"token": access_token}
print(f"Sending token: {access_token[:50]}...")
response = requests.get(f"{BASE_URL}/users/me", params=headers)
print_result(response, "Should return current user info")
assert response.status_code == 200, "Failed!"
user_info = response.json()
assert user_info["id"] == user_id, "User ID doesn't match!"
assert user_info["email"] == test_email, "Email doesn't match!"
print("✅ PASSED")

# ============ TEST 8: Get User Without Token ============
print_test("GET /users/me (No Token - Should Fail)")
response = requests.get(f"{BASE_URL}/users/me")
print_result(response, "Should return 401 error")
assert response.status_code == 401, f"Expected 401, got {response.status_code}"
print("✅ PASSED (Correctly rejected no token)")

# ============ TEST 9: Get User With Invalid Token ============
print_test("GET /users/me (Invalid Token - Should Fail)")
bad_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.invalid"
response = requests.get(f"{BASE_URL}/users/me", params={"token": bad_token})
print_result(response, "Should return 401 error")
assert response.status_code == 401, f"Expected 401, got {response.status_code}"
print("✅ PASSED (Correctly rejected invalid token)")

# ============ SUMMARY ============
print("\n" + "="*60)
print("✅ ALL TESTS PASSED! 🎉".center(60))
print("="*60)
print("\nSummary:")
print("✅ Hello world endpoint works")
print("✅ Health check works")
print("✅ User registration works and password is NOT returned")
print("✅ Duplicate email rejected")
print("✅ Login works and returns token")
print("✅ Wrong password rejected")
print("✅ Get user with valid token works")
print("✅ Get user without token rejected")
print("✅ Get user with invalid token rejected")
print("\nYour API is working correctly! 🚀")
