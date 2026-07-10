"""
Phase 4 Document Management Tests

This test suite validates:
1. Document upload
2. Document listing
3. Document download
4. Document deletion
5. Ownership authorization
6. Error handling
"""

import requests
import os
from datetime import datetime

BASE_URL = "http://localhost:8000"


def test_phase4():
    print("\n" + "=" * 70)
    print("PHASE 4: DOCUMENT MANAGEMENT TESTS".center(70))
    print("=" * 70)

    # ---------------------------------------------------------
    # SETUP
    # ---------------------------------------------------------

    print("\n[SETUP] Creating two test users...")

    user1_email = f"user1_docs_{int(datetime.now().timestamp())}@test.com"
    user2_email = f"user2_docs_{int(datetime.now().timestamp())}@test.com"

    # Register User 1
    r = requests.post(
        f"{BASE_URL}/users/register",
        json={
            "email": user1_email,
            "username": f"user1_{int(datetime.now().timestamp())}",
            "password": "Password123!"
        }
    )

    assert r.status_code == 200
    user1_id = r.json()["id"]
    print(f"✅ User 1 created (ID: {user1_id})")

    # Register User 2
    r = requests.post(
        f"{BASE_URL}/users/register",
        json={
            "email": user2_email,
            "username": f"user2_{int(datetime.now().timestamp())}",
            "password": "Password123!"
        }
    )

    assert r.status_code == 200
    user2_id = r.json()["id"]
    print(f"✅ User 2 created (ID: {user2_id})")

    # Login User 1
    r = requests.post(
        f"{BASE_URL}/users/login",
        json={
            "email": user1_email,
            "password": "Password123!"
        }
    )

    user1_token = r.json()["access_token"]
    print("✅ User 1 logged in")

    # Login User 2
    r = requests.post(
        f"{BASE_URL}/users/login",
        json={
            "email": user2_email,
            "password": "Password123!"
        }
    )

    user2_token = r.json()["access_token"]
    print("✅ User 2 logged in")

    # ---------------------------------------------------------
    # Create project
    # ---------------------------------------------------------

    print("\n[SETUP] Creating project...")

    r = requests.post(
        f"{BASE_URL}/projects",
        params={"token": user1_token},
        json={
            "name": "Document Test Project",
            "description": "Phase 4"
        }
    )

    assert r.status_code == 201

    project = r.json()
    project_id = project["id"]

    print(f"✅ Project created (ID: {project_id})")

    # ---------------------------------------------------------
    # Create sample PDF
    # ---------------------------------------------------------

    pdf_name = "sample.pdf"

    with open(pdf_name, "wb") as f:
        f.write(b"%PDF-1.4\nFake PDF")

    # ---------------------------------------------------------
    # TEST 1
    # ---------------------------------------------------------

    print("\n[TEST 1] Upload PDF document...")

    with open(pdf_name, "rb") as f:

        r = requests.post(
            f"{BASE_URL}/documents/projects/{project_id}",
            params={"token": user1_token},
            files={
                "file": (
                    pdf_name,
                    f,
                    "application/pdf"
                )
            }
        )

    assert r.status_code == 201, r.text

    document = r.json()
    document_id = document["id"]

    print(f"✅ Document uploaded (ID: {document_id})")

    # ---------------------------------------------------------
    # TEST 2
    # ---------------------------------------------------------

    print("\n[TEST 2] List project documents...")

    r = requests.get(
        f"{BASE_URL}/documents/projects/{project_id}",
        params={"token": user1_token}
    )

    assert r.status_code == 200

    documents = r.json()

    assert any(d["id"] == document_id for d in documents)

    print(f"✅ Project contains {len(documents)} document(s)")

    # ---------------------------------------------------------
    # TEST 3
    # ---------------------------------------------------------

    print("\n[TEST 3] Download document...")

    r = requests.get(
        f"{BASE_URL}/documents/{document_id}",
        params={"token": user1_token}
    )

    assert r.status_code == 200

    print("✅ Download successful")

    # ---------------------------------------------------------
    # TEST 4
    # ---------------------------------------------------------

    print("\n[TEST 4] User 2 tries to list User 1 documents - SHOULD FAIL...")

    r = requests.get(
        f"{BASE_URL}/documents/projects/{project_id}",
        params={"token": user2_token}
    )

    print(f"   Status: {r.status_code}, Response: {r.json()}")

    assert r.status_code == 403

    print("✅ Correctly blocked (403 Forbidden)")

    # ---------------------------------------------------------
    # TEST 5
    # ---------------------------------------------------------

    print("\n[TEST 5] User 2 tries to download document - SHOULD FAIL...")

    r = requests.get(
        f"{BASE_URL}/documents/{document_id}",
        params={"token": user2_token}
    )

    print(f"   Status: {r.status_code}, Response: {r.json()}")

    assert r.status_code == 403

    print("✅ Correctly blocked (403 Forbidden)")

    # ---------------------------------------------------------
    # TEST 6
    # ---------------------------------------------------------

    print("\n[TEST 6] User 2 tries to delete document - SHOULD FAIL...")

    r = requests.delete(
        f"{BASE_URL}/documents/{document_id}",
        params={"token": user2_token}
    )

    print(f"   Status: {r.status_code}, Response: {r.json()}")

    assert r.status_code == 403

    print("✅ Correctly blocked (403 Forbidden)")

    # ---------------------------------------------------------
    # TEST 7
    # ---------------------------------------------------------

    print("\n[TEST 7] Owner deletes document...")

    r = requests.delete(
        f"{BASE_URL}/documents/{document_id}",
        params={"token": user1_token}
    )

    assert r.status_code == 200

    print("✅ Document deleted")

    # ---------------------------------------------------------
    # TEST 8
    # ---------------------------------------------------------

    print("\n[TEST 8] Download deleted document - SHOULD RETURN 404...")

    r = requests.get(
        f"{BASE_URL}/documents/{document_id}",
        params={"token": user1_token}
    )

    assert r.status_code == 404

    print("✅ Correctly returned 404")

    # ---------------------------------------------------------
    # TEST 9
    # ---------------------------------------------------------

    print("\n[TEST 9] Missing token...")

    r = requests.get(
        f"{BASE_URL}/documents/projects/{project_id}"
    )

    assert r.status_code == 401

    print("✅ Correctly blocked (401 Unauthorized)")

    # ---------------------------------------------------------
    # TEST 10
    # ---------------------------------------------------------

    print("\n[TEST 10] Invalid token...")

    r = requests.get(
        f"{BASE_URL}/documents/projects/{project_id}",
        params={"token": "invalid.token"}
    )

    assert r.status_code == 401

    print("✅ Correctly blocked (401 Unauthorized)")

    if os.path.exists(pdf_name):
        os.remove(pdf_name)

    print("\n" + "=" * 70)
    print("✅ ALL PHASE 4 DOCUMENT TESTS PASSED!".center(70))
    print("=" * 70)

    print("\nKey findings:")
    print("✅ Owner can upload documents")
    print("✅ Owner can list documents")
    print("✅ Owner can download documents")
    print("✅ Owner can delete documents")
    print("✅ Other users cannot access documents (403)")
    print("✅ Missing and invalid tokens are rejected")
    print("✅ Deleted documents return 404")


if __name__ == "__main__":
    try:
        test_phase4()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        exit(1)