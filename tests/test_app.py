"""
Test suite for the Mergington High School Activities API

This module contains comprehensive tests for all API endpoints and functionality.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy


@pytest.fixture
def original_activities():
    """Store the original activities data for restoration after tests."""
    return copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def restore_activities(original_activities):
    """Restore original activities data after each test."""
    yield
    # Clear current activities and restore original data
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Test cases for the root endpoint."""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers["location"]


class TestActivitiesEndpoint:
    """Test cases for the activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Check if expected activities are present
        assert "Chess Club" in data
        assert "Programming Class" in data
        
        # Verify activity structure
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupEndpoint:
    """Test cases for the signup endpoint."""
    
    def test_signup_for_existing_activity_success(self, client):
        """Test successful signup for an existing activity."""
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"
        
        # Ensure student is not already signed up
        initial_participants = len(activities[activity_name]["participants"])
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify student was added to participants
        assert len(activities[activity_name]["participants"]) == initial_participants + 1
        assert email in activities[activity_name]["participants"]
    
    def test_signup_for_nonexistent_activity_fails(self, client):
        """Test signup fails for non-existent activity."""
        email = "student@mergington.edu"
        activity_name = "Nonexistent Club"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_duplicate_signup_fails(self, client):
        """Test that signing up twice for the same activity fails."""
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_with_url_encoded_activity_name(self, client):
        """Test signup works with URL-encoded activity names."""
        email = "newstudent@mergington.edu"
        activity_name = "Soccer Team"
        encoded_activity = "Soccer%20Team"
        
        response = client.post(f"/activities/{encoded_activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify student was added
        assert email in activities[activity_name]["participants"]


class TestUnregisterEndpoint:
    """Test cases for the unregister endpoint."""
    
    def test_unregister_existing_participant_success(self, client):
        """Test successful unregistration of an existing participant."""
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        activity_name = "Chess Club"
        
        # Verify student is initially signed up
        assert email in activities[activity_name]["participants"]
        initial_participants = len(activities[activity_name]["participants"])
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify student was removed
        assert len(activities[activity_name]["participants"]) == initial_participants - 1
        assert email not in activities[activity_name]["participants"]
    
    def test_unregister_from_nonexistent_activity_fails(self, client):
        """Test unregistration fails for non-existent activity."""
        email = "student@mergington.edu"
        activity_name = "Nonexistent Club"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_unregister_non_participant_fails(self, client):
        """Test unregistration fails for student not registered for activity."""
        email = "notregistered@mergington.edu"
        activity_name = "Chess Club"
        
        # Verify student is not signed up
        assert email not in activities[activity_name]["participants"]
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_with_url_encoded_activity_name(self, client):
        """Test unregistration works with URL-encoded activity names."""
        email = "lucas@mergington.edu"  # Already signed up for Soccer Team
        activity_name = "Soccer Team"
        encoded_activity = "Soccer%20Team"
        
        # Verify student is initially signed up
        assert email in activities[activity_name]["participants"]
        
        response = client.delete(f"/activities/{encoded_activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify student was removed
        assert email not in activities[activity_name]["participants"]


class TestIntegrationScenarios:
    """Integration test scenarios combining multiple operations."""
    
    def test_signup_and_unregister_flow(self, client):
        """Test complete flow of signing up and then unregistering."""
        email = "testflow@mergington.edu"
        activity_name = "Programming Class"
        
        # Initial state
        initial_participants = len(activities[activity_name]["participants"])
        assert email not in activities[activity_name]["participants"]
        
        # Sign up
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_participants + 1
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert unregister_response.status_code == 200
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_participants
    
    def test_multiple_students_signup_same_activity(self, client):
        """Test multiple students can sign up for the same activity."""
        activity_name = "Art Workshop"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        initial_participants = len(activities[activity_name]["participants"])
        
        # Sign up multiple students
        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
            assert email in activities[activity_name]["participants"]
        
        # Verify all students are signed up
        assert len(activities[activity_name]["participants"]) == initial_participants + len(emails)
        for email in emails:
            assert email in activities[activity_name]["participants"]


class TestDataValidation:
    """Test data validation and edge cases."""
    
    def test_activities_data_structure(self, client):
        """Test that activities data structure is valid."""
        response = client.get("/activities")
        activities_data = response.json()
        
        for activity_name, activity_details in activities_data.items():
            assert isinstance(activity_name, str)
            assert len(activity_name) > 0
            
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            
            assert isinstance(activity_details["description"], str)
            assert isinstance(activity_details["schedule"], str)
            assert isinstance(activity_details["max_participants"], int)
            assert isinstance(activity_details["participants"], list)
            
            assert activity_details["max_participants"] > 0
            assert len(activity_details["participants"]) <= activity_details["max_participants"]
    
    def test_email_format_handling(self, client):
        """Test various email formats are handled correctly."""
        activity_name = "Drama Club"
        
        # Test normal email
        email1 = "normal@mergington.edu"
        response1 = client.post(f"/activities/{activity_name}/signup?email={email1}")
        assert response1.status_code == 200
        
        # Test email with special characters (URL encoded)
        email2 = "test+user@mergington.edu"
        encoded_email2 = "test%2Buser@mergington.edu"
        response2 = client.post(f"/activities/{activity_name}/signup?email={encoded_email2}")
        assert response2.status_code == 200