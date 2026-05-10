# 🧪 How to Test Your Placement Portal APIs

Since this project currently lacks a registration or login API, testing requires a mix of using the **Django Admin Panel** (to create users) and an **API Testing Tool** like Postman, Thunder Client (VS Code extension), or cURL to test the endpoints.

Follow these steps in exact order to test the full flow of your application.

---

## Step 1: Preparation (Creating Users)

Before testing the APIs, create actual users in the database. Since there is no signup API yet, create them via the Django Admin.

### 1.1 Create a Superuser (Admin)
Open your terminal, navigate to your project folder (`placement_portal`), and run:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter a username (for example, `admin`), email, and password.

### 1.2 Start the Server
Run the development server:

```bash
python manage.py runserver
```

### 1.3 Create Test Users in Admin Panel
1. Open your browser and go to: `http://127.0.0.1:8000/admin/`
2. Log in with the superuser credentials you just created.
3. Click **Users** (under the Users app).
4. Click **Add user +** in the top right.
5. Create a **Student** user:
   - Username: `rohit_student`
   - Password: `testpassword123`
   - Click **Save and continue editing**.
   - Scroll down to the **Role** field and select **Student**.
   - Click **Save**.
   - Note: Because of your Django signal, a `StudentProfile` is automatically created.
6. Create a **Company** user:
   - Username: `tcs_company`
   - Password: `testpassword123`
   - Click **Save and continue editing**.
   - Scroll down to the **Role** field and select **Company**.
   - Click **Save**.
   - Note: A `CompanyProfile` is automatically created.

> **Important:** Note down the **ID** of the users you created. You can see the ID in the URL when editing a user in admin (for example, `/admin/users/user/2/change/` means user ID = 2).
> - Assume `rohit_student` has **ID: 2**
> - Assume `tcs_company` has **ID: 3**

---

## Step 2: Testing the APIs (Postman / Thunder Client / cURL)

Now test the main API endpoints. Keep the Django server running while testing.

### Test 1: Update Student Profile (POST)
Update skills for `rohit_student`.

- **Endpoint:** `POST http://127.0.0.1:8000/api/students/profile/`
- **Headers:** `Content-Type: application/json`
- **Body (JSON):**

```json
{
    "user_id": 2,
    "skills": "Python, Django, React, SQL"
}
```

Replace `2` with your actual student user ID.

- **Expected Response (200 OK):**

```json
{
    "message": "Student profile saved successfully.",
    "user": 2,
    "skills": "Python, Django, React, SQL",
    "resume": null
}
```

- **If it fails:**
  - If you get `"User does not exist"` or `"Only student users..."`, verify that the ID belongs to a user whose role is `student`.

### Test 2: Create a Job Posting (POST)
Have `tcs_company` post a job.

- **Endpoint:** `POST http://127.0.0.1:8000/api/jobs/`
- **Headers:** `Content-Type: application/json`
- **Body (JSON):**

```json
{
    "company_id": 3,
    "title": "Junior Python Developer",
    "description": "Looking for a fresh graduate with Django experience.",
    "location": "Bangalore",
    "salary": 600000
}
```

Replace `3` with your actual company user ID.

- **Expected Response (201 Created):**

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

### Test 3: List All Jobs (GET)
Verify that the job was created and is publicly visible.

- **Endpoint:** `GET http://127.0.0.1:8000/api/jobs/`
- **Body:** None

- **Expected Response (200 OK):**

```json
[
    {
        "id": 1,
        "title": "Junior Python Developer",
        "description": "Looking for a fresh graduate with Django experience.",
        "location": "Bangalore",
        "salary": 600000,
        "created_at": "2026-05-06T...",
        "company": 3
    }
]
```

### Test 4: Apply for a Job (POST)
Now `rohit_student` applies for the job posted by `tcs_company`.

- **Endpoint:** `POST http://127.0.0.1:8000/api/applications/`
- **Headers:** `Content-Type: application/json`
- **Body (JSON):**

```json
{
    "student_id": 2,
    "job_id": 1
}
```

Ensure `student_id` is your student and `job_id` is the ID returned in Test 2.

- **Expected Response (201 Created):**

```json
{
    "id": 1,
    "student_id": 2,
    "job_id": 1,
    "status": "pending",
    "applied_at": "2026-05-06T..."
}
```

- **Bonus test (duplicate application):** Send the exact same POST request again.
  - **Expected Response (400 Bad Request):**

```json
[
    "You already applied to this job."
]
```

This confirms your unique validation logic is working.

### Test 5: View Applications (GET)
Check all applications and filtered results.

- **All Applications:** `GET http://127.0.0.1:8000/api/applications/`
- **Filter by Student:** `GET http://127.0.0.1:8000/api/applications/?student_id=2`
- **Filter by Job:** `GET http://127.0.0.1:8000/api/applications/?job_id=1`

- **Expected Response (200 OK):**

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

---

## Step 3: Verify in Django Admin

Go to `http://127.0.0.1:8000/admin/` and verify:

1. **Applications** section: You should see Rohit's application to the Junior Python Developer job.
2. **Jobs** section: You should see the job posted by TCS.
3. **Student profiles** section: You should see Rohit's profile with the skills from Test 1.

This confirms the APIs are correctly interacting with the database.
