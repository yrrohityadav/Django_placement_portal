# Placement Portal Django

This repository contains a Django-based Placement Portal backend with modules for users, jobs, and applications.

## Project Structure

- `placement_portal/users`: User model, roles, profile APIs, and permissions
- `placement_portal/jobs`: Job posting and job listing APIs
- `placement_portal/applications`: Job application APIs and filtering
- `placement_portal/API_TESTING_GUIDE.md`: In-project API testing guide
- `api_testing_guide.md`: Root-level API testing guide

## Placement Portal Guide

Since this project currently lacks registration/login APIs, test the system using Django Admin for user creation and Postman/Thunder Client/cURL for API calls.

### Step 1: Preparation (Create Users)

1. Create superuser:

```bash
cd placement_portal
python manage.py createsuperuser
```

2. Start server:

```bash
python manage.py runserver
```

3. Open admin at `http://127.0.0.1:8000/admin/`.

4. Create a `Student` user:
- Example username: `rohit_student`
- Example password: `testpassword123`
- Save user, set role to `Student`, save again.

5. Create a `Company` user:
- Example username: `tcs_company`
- Example password: `testpassword123`
- Save user, set role to `Company`, save again.

6. Note the user IDs from admin URL:
- Example: `/admin/users/user/2/change/` means ID is `2`.
- Assume:
- `rohit_student` -> `2`
- `tcs_company` -> `3`

### Step 2: API Testing Flow

#### Test 1: Update Student Profile (POST)

- Endpoint: `POST http://127.0.0.1:8000/api/students/profile/`
- Headers: `Content-Type: application/json`
- Body:

```json
{
  "user_id": 2,
  "skills": "Python, Django, React, SQL"
}
```

- Expected `200 OK`:

```json
{
  "message": "Student profile saved successfully.",
  "user": 2,
  "skills": "Python, Django, React, SQL",
  "resume": null
}
```

If it fails with user/role errors, verify the ID belongs to a user with role `student`.

#### Test 2: Create Job (POST)

- Endpoint: `POST http://127.0.0.1:8000/api/jobs/`
- Headers: `Content-Type: application/json`
- Body:

```json
{
  "company_id": 3,
  "title": "Junior Python Developer",
  "description": "Looking for a fresh graduate with Django experience.",
  "location": "Bangalore",
  "salary": 600000
}
```

- Expected `201 Created`:

```json
{
  "id": 1,
  "title": "Junior Python Developer",
  "description": "Looking for a fresh graduate with Django experience.",
  "location": "Bangalore",
  "salary": 600000,
  "created_at": "2026-05-06T...",
  "company": 3
}
```

#### Test 3: List Jobs (GET)

- Endpoint: `GET http://127.0.0.1:8000/api/jobs/`
- Expected `200 OK` with created job records.

#### Test 4: Apply to Job (POST)

- Endpoint: `POST http://127.0.0.1:8000/api/applications/`
- Headers: `Content-Type: application/json`
- Body:

```json
{
  "student_id": 2,
  "job_id": 1
}
```

- Expected `201 Created`:

```json
{
  "id": 1,
  "student_id": 2,
  "job_id": 1,
  "status": "pending",
  "applied_at": "2026-05-06T..."
}
```

Duplicate request should return `400 Bad Request`:

```json
[
  "You already applied to this job."
]
```

#### Test 5: View Applications (GET)

- All: `GET http://127.0.0.1:8000/api/applications/`
- By student: `GET http://127.0.0.1:8000/api/applications/?student_id=2`
- By job: `GET http://127.0.0.1:8000/api/applications/?job_id=1`

Expected `200 OK`:

```json
[
  {
    "id": 1,
    "student_id": 2,
    "student_username": "rohit_student",
    "job_id": 1,
    "job_title": "Junior Python Developer",
    "status": "pending",
    "applied_at": "2026-05-06T..."
  }
]
```

### Step 3: Verify in Django Admin

Check in admin:

1. `Applications`: Application record exists
2. `Jobs`: Job posting exists
3. `Student profiles`: Skills are updated

If these are present, your APIs are correctly interacting with the database.

## Notes

- The content above consolidates guide details from:
- `api_testing_guide.md`
- `placement_portal/API_TESTING_GUIDE.md`
