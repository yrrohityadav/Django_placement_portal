# 🧪 How to Test Your Placement Portal APIs

Since your project currently lacks a registration or login API, testing requires a mix of using the **Django Admin Panel** (to create users) and an **API Testing Tool** like Postman, Thunder Client (VS Code extension), or cURL to test the endpoints.

Follow these steps in exact order to test the full flow of your application.

---

## Step 1: Preparation (Creating Users)

Before testing the APIs, we need actual users in the database. Since we don't have a signup API yet, we will create them via the Django Admin.

### 1.1 Create a Superuser (Admin)
Open your terminal, navigate to your project folder (`placement_portal`), and run:
```bash
python manage.py createsuperuser
```
Follow the prompts to enter a username (e.g., `admin`), email, and password.

### 1.2 Start the Server
Run the development server:
```bash
python manage.py runserver
```

### 1.3 Create Test Users in Admin Panel
1. Open your browser and go to: `http://127.0.0.1:8000/admin/`
2. Log in with the superuser credentials you just created.
3. Click on **Users** (under the Users app).
4. Click **Add user +** in the top right.
5. Create a **Student** User:
   *   Username: `rohit_student`
   *   Password: `testpassword123`
   *   Click "Save and continue editing".
   *   Scroll down to the **Role** field and select **Student**.
   *   Click "Save".
   *   *Note: Because of your Django signal, a `StudentProfile` was just automatically created in the background!*
6. Create a **Company** User:
   *   Username: `tcs_company`
   *   Password: `testpassword123`
   *   Click "Save and continue editing".
   *   Scroll down to the **Role** field and select **Company**.
   *   Click "Save".
   *   *Note: A `CompanyProfile` was automatically created!*

> **IMPORTANT:** Note down the **ID** of the users you just created. You can see the ID in the URL when editing the user in the admin panel (e.g., `/admin/users/user/2/change/` means the ID is 2).
> *   Let's assume `rohit_student` has **ID: 2**
> *   Let's assume `tcs_company` has **ID: 3**

---

## Step 2: Testing the APIs (Using Postman or similar)

Now we will test the 4 main API endpoints. Open Postman or your preferred API tool. Ensure your Django server is still running.

### Test 1: Update Student Profile (POST)
Let's update the skills for `rohit_student`.

*   **Endpoint:** `POST http://127.0.0.1:8000/api/students/profile/`
*   **Headers:** `Content-Type: application/json`
*   **Body (JSON):**
    ```json
    {
        "user_id": 2,
        "skills": "Python, Django, React, SQL"
    }
    ```
    *(Replace `2` with the actual ID of your student user)*

*   **Expected Response (200 OK):**
    ```json
    {
        "message": "Student profile saved successfully.",
        "user": 2,
        "skills": "Python, Django, React, SQL",
        "resume": null
    }
    ```
*   **What to check if it fails:**
    *   If you get "User does not exist" or "Only student users...", ensure the ID you used actually belongs to a user with the `student` role.

---

### Test 2: Create a Job Posting (POST)
Let's have `tcs_company` post a new job.

*   **Endpoint:** `POST http://127.0.0.1:8000/api/jobs/`
*   **Headers:** `Content-Type: application/json`
*   **Body (JSON):**
    ```json
    {
        "company_id": 3,
        "title": "Junior Python Developer",
        "description": "Looking for a fresh graduate with Django experience.",
        "location": "Bangalore",
        "salary": 600000
    }
    ```
    *(Replace `3` with the actual ID of your company user)*

*   **Expected Response (201 Created):**
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

---

### Test 3: List all Jobs (GET)
Let's verify the job was actually created and can be viewed by anyone.

*   **Endpoint:** `GET http://127.0.0.1:8000/api/jobs/`
*   **No Body needed.**

*   **Expected Response (200 OK):**
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

---

### Test 4: Apply for a Job (POST)
Now `rohit_student` will apply for the job posted by `tcs_company`.

*   **Endpoint:** `POST http://127.0.0.1:8000/api/applications/`
*   **Headers:** `Content-Type: application/json`
*   **Body (JSON):**
    ```json
    {
        "student_id": 2,
        "job_id": 1
    }
    ```
    *(Ensure `student_id` is your student, and `job_id` is the ID from Test 2)*

*   **Expected Response (201 Created):**
    ```json
    {
        "id": 1,
        "student_id": 2,
        "job_id": 1,
        "status": "pending",
        "applied_at": "2026-05-06T..."
    }
    ```

*   **Bonus Test (Duplicate Application):** Try sending the exact same POST request again.
    *   **Expected Response (400 Bad Request):**
        ```json
        [
            "You already applied to this job."
        ]
        ```
        This proves your unique validation logic is working!

---

### Test 5: View Applications (GET)
Let's see the list of applications. You can test the filtering here.

*   **Endpoint 1 (All Applications):** `GET http://127.0.0.1:8000/api/applications/`
*   **Endpoint 2 (Filter by Student):** `GET http://127.0.0.1:8000/api/applications/?student_id=2`
*   **Endpoint 3 (Filter by Job):** `GET http://127.0.0.1:8000/api/applications/?job_id=1`

*   **Expected Response (200 OK):**
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

Finally, go back to your browser at `http://127.0.0.1:8000/admin/`.
1. Look at the **Applications** section. You should see Rohit's application to the Junior Python Developer job.
2. Look at the **Jobs** section. You should see the job posted by TCS.
3. Look at the **Student profiles** section. You should see Rohit's profile now contains the skills you POSTed in Test 1.

This confirms that the APIs are correctly interacting with the database!
