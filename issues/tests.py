import pytest
from .models import Issue, IssueComment, IssueLike

def is_sre(response_data):
    """Helper to check if response is from SRE system"""
    if isinstance(response_data, dict) and "success" in response_data and ("response" in response_data or "error" in response_data):
        return True
    return False

@pytest.mark.django_db
class TestIssueLifecycle:

    # --- Creation Tests ---

    def test_issue_creation_success(self, user1_client, dummy_image):
        print("\n--- Test: Create Issue Success ---")
        payload = {
            "title": "User1 Issue",
            "description": "Description",
            "category": "General",
            "uploaded_images": [dummy_image]
        }
        response = user1_client.post("/issues/create/", payload, format='multipart')
        data = response.json()
        
        print(f"Response: {data}")
        assert response.status_code == 201
        assert is_sre(data)
        assert data['success'] is True
        assert data['response']['title'] == "User1 Issue"
        assert Issue.objects.count() == 1
        assert Issue.objects.first().images.count() == 1

    def test_issue_creation_fail_no_image(self, user1_client):
        print("\n--- Test: Create Issue Fail (No Image) ---")
        payload = {
            "title": "No Image Issue",
            "description": "Desc",
            "category": "General"
        }
        response = user1_client.post("/issues/create/", payload)
        data = response.json()

        print(f"Response: {data}")
        assert response.status_code == 400
        assert is_sre(data)
        assert data['success'] is False
        # Verify error details contain uploaded_images
        # The error structure depends on DRF + Renderer. 
        # Usually: error -> details -> uploaded_images
        assert 'uploaded_images' in data['error']['details']

    def test_issue_creation_unauth(self, anon_client, dummy_image):
        print("\n--- Test: Create Issue Unauthenticated ---")
        payload = {
            "title": "Anon Issue",
            "description": "Desc",
            "uploaded_images": [dummy_image]
        }
        response = anon_client.post("/issues/create/", payload, format='multipart')
        print(f"Response Status: {response.status_code}")
        assert response.status_code == 401

    # --- Update Tests ---

    def test_issue_update_owner(self, user1_client, dummy_image):
        print("\n--- Test: Update Issue (Owner) ---")
        # Setup
        payload = {"title": "Original", "description": "Desc", "uploaded_images": [dummy_image]}
        create_resp = user1_client.post("/issues/create/", payload, format='multipart')
        issue_id = create_resp.json()['response']['id']

        # Update
        update_payload = {"title": "Updated Title", "description": "Updated Desc"}
        response = user1_client.patch(f"/issues/update/{issue_id}/", update_payload)
        data = response.json()

        print(f"Response: {data}")
        assert response.status_code == 200
        assert data['success'] is True
        assert data['response']['title'] == "Updated Title"
        
        issue = Issue.objects.get(id=issue_id)
        assert issue.title == "Updated Title"

    def test_issue_update_others_fail(self, user1_client, user2_client, dummy_image):
        print("\n--- Test: Update Issue (Non-Owner) ---")
        # User1 creates
        payload = {"title": "User1 Issue", "description": "Desc", "uploaded_images": [dummy_image]}
        create_resp = user1_client.post("/issues/create/", payload, format='multipart')
        issue_id = create_resp.json()['response']['id']

        # User2 tries to update
        update_payload = {"title": "Hacked Title"}
        response = user2_client.patch(f"/issues/update/{issue_id}/", update_payload)
        
        print(f"Response Status: {response.status_code}")
        assert response.status_code == 403
        assert response.json()['success'] is False

    def test_issue_update_admin(self, user1_client, admin_client, dummy_image):
        print("\n--- Test: Update Issue (Admin) ---")
        # User1 creates
        payload = {"title": "User1 Issue", "description": "Desc", "uploaded_images": [dummy_image]}
        create_resp = user1_client.post("/issues/create/", payload, format='multipart')
        issue_id = create_resp.json()['response']['id']

        # Admin updates (IsOwnerOrStaff permission allows staff/admin)
        update_payload = {"title": "Admin Edited"}
        response = admin_client.patch(f"/issues/update/{issue_id}/", update_payload)
        
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        assert Issue.objects.get(id=issue_id).title == "Admin Edited"

    # --- Delete Tests ---

    def test_issue_delete_owner(self, user1_client, dummy_image):
        print("\n--- Test: Delete Issue (Owner) ---")
        payload = {"title": "To Delete", "description": "Desc", "uploaded_images": [dummy_image]}
        create_resp = user1_client.post("/issues/create/", payload, format='multipart')
        issue_id = create_resp.json()['response']['id']

        response = user1_client.delete(f"/issues/delete/{issue_id}/")
        print(f"Response Status: {response.status_code}")
        assert response.status_code == 204
        assert not Issue.objects.filter(id=issue_id).exists()

    def test_issue_delete_others_fail(self, user1_client, user2_client, dummy_image):
        print("\n--- Test: Delete Issue (Non-Owner) ---")
        payload = {"title": "User1 Issue", "description": "Desc", "uploaded_images": [dummy_image]}
        create_resp = user1_client.post("/issues/create/", payload, format='multipart')
        issue_id = create_resp.json()['response']['id']

        response = user2_client.delete(f"/issues/delete/{issue_id}/")
        print(f"Response Status: {response.status_code}")
        assert response.status_code == 403
        assert Issue.objects.filter(id=issue_id).exists()

    def test_issue_delete_admin(self, user1_client, admin_client, dummy_image):
        print("\n--- Test: Delete Issue (Admin) ---")
        payload = {"title": "User1 Issue", "description": "Desc", "uploaded_images": [dummy_image]}
        create_resp = user1_client.post("/issues/create/", payload, format='multipart')
        issue_id = create_resp.json()['response']['id']

        # Using the generic delete view which allows staff
        response = admin_client.delete(f"/issues/delete/{issue_id}/")
        print(f"Response Status: {response.status_code}")
        assert response.status_code == 204
        assert not Issue.objects.filter(id=issue_id).exists()

    # --- Comment Tests ---

    def test_comment_flow(self, user1_client, user2_client, dummy_image):
        print("\n--- Test: Comment Flow ---")
        # User1 creates issue
        payload = {"title": "Discuss", "description": "Desc", "uploaded_images": [dummy_image]}
        create_resp = user1_client.post("/issues/create/", payload, format='multipart')
        issue_id = create_resp.json()['response']['id']

        # User2 comments
        comment_payload = {"issue_id": issue_id, "text": "Nice issue"}
        resp = user2_client.post("/issues/comments/create/", comment_payload)
        assert resp.status_code == 201
        
        # Verify comment list
        list_resp = user1_client.get(f"/issues/comments/of/{issue_id}/")
        comments = list_resp.json()['response']
        assert len(comments) == 1
        assert comments[0]['text'] == "Nice issue"
        comment_id = comments[0]['id']

        # User1 tries to delete User2's comment (should fail)
        del_resp = user1_client.delete(f"/issues/comments/delete/{comment_id}/")
        assert del_resp.status_code == 403

        # User2 deletes their own comment
        del_resp = user2_client.delete(f"/issues/comments/delete/{comment_id}/")
        assert del_resp.status_code == 204
        assert IssueComment.objects.count() == 0

    # --- Like Tests ---

    def test_like_flow(self, user1_client, user2_client, dummy_image):
        print("\n--- Test: Like Flow ---")
        # User1 creates issue
        payload = {"title": "Like me", "description": "Desc", "uploaded_images": [dummy_image]}
        create_resp = user1_client.post("/issues/create/", payload, format='multipart')
        issue_id = create_resp.json()['response']['id']

        # User2 toggles like (ON)
        resp = user2_client.post("/issues/likes/toggle/", {"issue_id": issue_id})
        assert resp.status_code == 200
        assert resp.json()['response']['liked'] is True
        assert IssueLike.objects.count() == 1

        # Verify likes list
        list_resp = user1_client.get(f"/issues/likes/of/{issue_id}/")
        likes = list_resp.json()['response']
        assert len(likes) == 1
        assert likes[0]['user'] == "strela500@gmail.com" # user2 email

        # User2 toggles like (OFF)
        resp = user2_client.post("/issues/likes/toggle/", {"issue_id": issue_id})
        assert resp.status_code == 200
        assert resp.json()['response']['liked'] is False
        assert IssueLike.objects.count() == 0

    # --- Isolation Tests ---

    def test_my_issues_isolation(self, user1_client, user2_client, dummy_image):
        print("\n--- Test: My Issues Isolation ---")
        # User1 creates issue
        user1_client.post("/issues/create/", {"title": "U1", "description": "D", "uploaded_images": [dummy_image]}, format='multipart')
        
        # Reset image for reuse
        dummy_image.seek(0)

        # User2 creates issue
        user2_client.post("/issues/create/", {"title": "U2", "description": "D", "uploaded_images": [dummy_image]}, format='multipart')

        # User1 checks mine
        resp1 = user1_client.get("/issues/mine/")
        issues1 = resp1.json()['response']
        assert len(issues1) == 1
        assert issues1[0]['title'] == "U1"

        # User2 checks mine
        resp2 = user2_client.get("/issues/mine/")
        issues2 = resp2.json()['response']
        assert len(issues2) == 1
        assert issues2[0]['title'] == "U2"

    # --- Edge Cases ---

    def test_create_comment_missing_fields(self, user1_client):
        print("\n--- Test: Create Comment Missing Fields ---")
        resp = user1_client.post("/issues/comments/create/", {})
        assert resp.status_code == 400
        assert resp.json()['success'] is False

    def test_get_non_existent_issue(self, user1_client):
        print("\n--- Test: Get Non-Existent Issue ---")
        # Bypass SRE wrapper to test 404
        response = user1_client.client.get("/issues/of/99999/")
        assert response.status_code == 404
        data = response.json()
        assert is_sre(data)
        assert data['success'] is False
        assert data['error']['message'] == "No Issue matches the given query."

