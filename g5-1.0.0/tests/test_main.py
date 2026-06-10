def test_status_endpoint(client):
    response = client.get("/status")

    assert response.status_code == 200
    assert response.json() == {
        "active_modules": [
            "students",
            "professors",
            "enrollments",
            "schedule",
            "grades",
            "materials",
            "announcements",
            "library",
            "reports",
        ],
        "missing_modules": [],
        "total": 9,
        "expected": 10,
    }
