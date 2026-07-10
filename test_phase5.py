"""
Phase 5 Collaboration Tests

This test suite validates:

1. Project collaboration
2. Project members
3. Authorization
4. Documents
"""

import os
import requests

from datetime import datetime

from app.routes import members

BASE_URL = "http://localhost:8000"


def test_phase5():

    print("\n" + "=" * 70)
    print("PHASE 5: PROJECT COLLABORATION TESTS".center(70))
    print("=" * 70)

    ##############################################################
    # SETUP
    ##############################################################

    print("\n[SETUP] Creating test users...")

    timestamp = int(datetime.now().timestamp())

    owner_email = f"owner_{timestamp}@test.com"
    participant_email = f"user_{timestamp}@test.com"

    ##############################################################
    # Register Owner
    ##############################################################

    r = requests.post(
        f"{BASE_URL}/users/register",
        json={
            "email": owner_email,
            "username": f"owner_{timestamp}",
            "password": "Password123!"
        }
    )

    assert r.status_code == 200, r.text

    owner = r.json()

    owner_id = owner["id"]

    print(f"✅ Owner created (ID: {owner_id})")

    ##############################################################
    # Register Participant
    ##############################################################

    r = requests.post(
        f"{BASE_URL}/users/register",
        json={
            "email": participant_email,
            "username": f"user_{timestamp}",
            "password": "Password123!"
        }
    )

    assert r.status_code == 200, r.text

    participant = r.json()

    participant_id = participant["id"]

    print(f"✅ Participant created (ID: {participant_id})")

    ##############################################################
    # Login Owner
    ##############################################################

    r = requests.post(
        f"{BASE_URL}/users/login",
        json={
            "email": owner_email,
            "password": "Password123!"
        }
    )

    assert r.status_code == 200

    owner_token = r.json()["access_token"]

    print("✅ Owner logged in")

    ##############################################################
    # Login Participant
    ##############################################################

    r = requests.post(
        f"{BASE_URL}/users/login",
        json={
            "email": participant_email,
            "password": "Password123!"
        }
    )

    assert r.status_code == 200

    participant_token = r.json()["access_token"]

    print("✅ Participant logged in")

    ##############################################################
    # TEST 1
    ##############################################################

    print("\n[TEST 1] Owner creates a project...")

    r = requests.post(
        f"{BASE_URL}/projects",
        json={
            "name": "Phase 5 Test Project",
            "description": "Testing collaboration"
        },
        params={
            "token": owner_token
        }
    )

    assert r.status_code == 201, r.text

    project = r.json()

    project_id = project["id"]

    print(f"✅ Project created (ID: {project_id})")

    ##############################################################
    # TEST 2
    ##############################################################

    print("\n[TEST 2] Owner invites participant...")

    r = requests.post(
        f"{BASE_URL}/projects/{project_id}/members",
        json={
            "email": participant_email
        },
        params={
            "token": owner_token
        }
    )

    assert r.status_code == 201, r.text

    print("✅ Participant invited successfully")

    ##############################################################
    # TEST 3
    ##############################################################

    print("\n[TEST 3] Owner lists members...")

    r = requests.get(
        f"{BASE_URL}/projects/{project_id}/members",
        params={
            "token": owner_token
        }
    )

    assert r.status_code == 200

    members = r.json()
    print(members)
    print(f"Members count: {len(members)}")
    assert len(members) == 2

    print(f"✅ Project has {len(members)} members")

    ##############################################################
    # TEST 4
    ##############################################################

    print("\n[TEST 4] Participant can see the shared project...")

    r = requests.get(
        f"{BASE_URL}/projects/{project_id}",
        params={
            "token": participant_token
        }
    )

    assert r.status_code == 200, r.text

    print("✅ Participant can access the project")

    ##############################################################
    # TEST 5
    ##############################################################

    print("\n[TEST 5] Participant updates the project...")

    r = requests.put(
        f"{BASE_URL}/projects/{project_id}",
        json={
            "name": "Updated by Participant",
            "description": "Participant successfully edited the project"
        },
        params={
            "token": participant_token
        }
    )

    assert r.status_code == 200, r.text

    updated_project = r.json()

    assert updated_project["name"] == "Updated by Participant"

    print("✅ Participant updated the project")

    ##############################################################
    # TEST 6
    ##############################################################

    print("\n[TEST 6] Participant cannot delete the project...")

    r = requests.delete(
        f"{BASE_URL}/projects/{project_id}",
        params={
            "token": participant_token
        }
    )

    assert r.status_code == 403

    print("✅ Participant is correctly forbidden from deleting the project")

    ##############################################################
    # TEST 7
    ##############################################################

    print("\n[TEST 7] Participant uploads a document...")

    test_filename = "phase5_test.pdf"

    with open(test_filename, "w", encoding="utf-8") as f:
        f.write("Phase 5 document upload test.")

    with open(test_filename, "rb") as f:

        r = requests.post(
            f"{BASE_URL}/documents/projects/{project_id}",
            files={
                "file": (
                    test_filename,
                    f,
                    "text/plain"
                )
            },
            params={
                "token": participant_token
            }
        )

    os.remove(test_filename)

    assert r.status_code == 201, r.text

    document = r.json()

    document_id = document["id"]

    print(f"✅ Document uploaded (ID: {document_id})")

    ##############################################################
    # TEST 8
    ##############################################################

    print("\n[TEST 8] Participant lists project documents...")

    r = requests.get(
        f"{BASE_URL}/documents/projects/{project_id}",
        params={
            "token": participant_token
        }
    )

    assert r.status_code == 200

    documents = r.json()

    assert len(documents) >= 1

    print(f"✅ Project contains {len(documents)} document(s)")

    ##############################################################
    # TEST 9
    ##############################################################

    print("\n[TEST 9] Participant downloads a document...")

    r = requests.get(
        f"{BASE_URL}/documents/{document_id}",
        params={
            "token": participant_token
        }
    )

    assert r.status_code == 200

    print("✅ Document downloaded successfully")

    ##############################################################
    # TEST 10
    ##############################################################

    print("\n[TEST 10] Participant cannot delete a document...")

    r = requests.delete(
        f"{BASE_URL}/documents/{document_id}",
        params={
            "token": participant_token
        }
    )

    assert r.status_code == 403

    print("✅ Participant is correctly forbidden from deleting documents")

        ##############################################################
    # TEST 11
    ##############################################################

    print("\n[TEST 11] Owner removes the participant...")

    r = requests.delete(
        f"{BASE_URL}/projects/{project_id}/members/{participant_id}",
        params={
            "token": owner_token
        }
    )

    assert r.status_code == 200, r.text

    print("✅ Participant removed successfully")

    ##############################################################
    # TEST 12
    ##############################################################

    print("\n[TEST 12] Removed participant loses project access...")

    r = requests.get(
        f"{BASE_URL}/projects/{project_id}",
        params={
            "token": participant_token
        }
    )

    assert r.status_code == 403

    print("✅ Removed participant no longer has access")

    ##############################################################
    # TEST 13
    ##############################################################

    print("\n[TEST 13] Owner deletes the document...")

    r = requests.delete(
        f"{BASE_URL}/documents/{document_id}",
        params={
            "token": owner_token
        }
    )

    assert r.status_code == 200, r.text

    print("✅ Owner deleted the document")

    ##############################################################
    # TEST 14
    ##############################################################

    print("\n[TEST 14] Owner deletes the project...")

    r = requests.delete(
        f"{BASE_URL}/projects/{project_id}",
        params={
            "token": owner_token
        }
    )

    assert r.status_code == 200, r.text

    print("✅ Owner deleted the project")

    ##############################################################
    # TEST 15
    ##############################################################

    print("\n[TEST 15] Deleted project returns 404...")

    r = requests.get(
        f"{BASE_URL}/projects/{project_id}",
        params={
            "token": owner_token
        }
    )

    assert r.status_code == 404

    print("✅ Deleted project correctly returns 404")

    ##############################################################
    # SUMMARY
    ##############################################################

    print("\n" + "=" * 70)
    print("ALL PHASE 5 TESTS PASSED".center(70))
    print("=" * 70)

    print("\nVerified functionality:")

    print("✅ Owner can invite participants")
    print("✅ Participants can access shared projects")
    print("✅ Participants can update projects")
    print("✅ Participants cannot delete projects")
    print("✅ Participants can upload documents")
    print("✅ Participants can list documents")
    print("✅ Participants can download documents")
    print("✅ Participants cannot delete documents")
    print("✅ Owner can remove participants")
    print("✅ Removed participants immediately lose access")
    print("✅ Owner can delete documents")
    print("✅ Owner can delete projects")


if __name__ == "__main__":

    try:

        test_phase5()

    except AssertionError as e:

        print(f"\n❌ TEST FAILED: {e}")

        exit(1)

    except Exception as e:

        print(f"\n❌ ERROR: {e}")

        exit(1)