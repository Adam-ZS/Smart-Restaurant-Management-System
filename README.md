<img width="1172" height="680" alt="image" src="https://github.com/user-attachments/assets/ac474215-08a8-4247-9387-dc1c218527f2" /># 🍽️ Smart Restaurant Management System (SRMS) - Prototype v1.0

**A unified, simulated full-stack management system for restaurant operations.**

This prototype implements core functionalities—Menu, Cart, Reservations, and Staff Portals (Admin, Waiter, Kitchen)—using a Python Flask API and a native JavaScript Single Page Application (SPA).

## ✨ Project Overview

| Component | Code File | Technology | Description |
| :--- | :--- | :--- | :--- |
| **Frontend (UI)** | `index.html` | HTML/CSS/JS (SPA) | Multi-panel interface for Customer, Waiter, Admin, and Kitchen roles. |
| **Backend (API)** | `newstyle.py` | Python Flask | Provides RESTful endpoints and manages **in-memory** data for Menu, Orders, Reservations, and Inventory. |
| **Data Storage** | *In-Memory* | Python Dictionaries | Data is temporary and resets every time the Python server restarts. |

## ⚙️ Technology Stack

* **Frontend**: Native JavaScript (ES6+), HTML5, CSS3.
* **Backend**: Python 3.x, Flask (for API handling), Flask-CORS.
* **Data**: In-memory Python data structures (simulating a database).
<img width="1902" height="877" alt="image" src="https://github.com/user-attachments/assets/60aba38f-8c7a-473b-8525-cef5539e7e8c" />
<img width="345" height="304" alt="image" src="https://github.com/user-attachments/assets/95ae08a6-8916-4826-b693-a84b8a17b080" />
<img width="1172" height="680" alt="image" src="https://github.com/user-attachments/assets/79bcc3f5-0096-4a5e-a3d6-c88d98e85823" />
<img width="738" height="472" alt="image" src="https://github.com/user-attachments/assets/70ef43de-585a-4aa4-bdd6-f1459fc0534c" />
<img width="852" height="381" alt="image" src="https://github.com/user-attachments/assets/c5b50807-a240-4d73-b4e9-44adff1c75c4" />





## 🛠️ Getting Started (Run Locally)

To run the full application, you must start the Python API first, and then open the HTML file in your browser.

### 1. Backend Setup and Start (API)

1.  **Save the file:** Ensure your Python file is saved as `newstyle.py` (or rename it to `app.py`).
2.  **Install Dependencies:** If you haven't already, install Flask and Flask-CORS.
    ```bash
    pip install Flask Flask-CORS
    ```
3.  **Run the Server:**
    ```bash
    python newstyle.py
    ```
    The API will start running on `http://127.0.0.1:5000`. Keep this terminal window open.

### 2. Frontend Launch (UI)

1.  **Launch the App:** Simply double-click the **`index.html`** file in your file explorer.
2.  **Verify Connection:** The "Backend: checking..." status in the header should update to "Backend: ok."

> **Note:** The frontend JavaScript explicitly calls the backend at `http://127.0.0.1:5000`. Both the Python server and the HTML file must be running on your local machine for the application to function.

## 🔑 Demo Access Credentials

The system includes simple, hardcoded login credentials for staff panel access:

| Role | Username | Password | Access Panel |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Admin Panel |
| **Waiter** | `waiter` | `waiter123` | Waiter POS |
| **Chef** | `chef` | `chef123` | Kitchen Display System |

## 📖 API Endpoints (Flask Backend)

The backend (`newstyle.py`) exposes the following primary endpoints:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Checks if the server is running. |
| `POST` | `/api/login` | Authenticates user and returns role. |
| `GET` | `/api/menu` | Lists all menu items. |
| `PUT` | `/api/menu/<id>` | Updates the name, price, or category of a menu item. |
| `GET` | `/api/inventory` | Lists all inventory items and thresholds. |
| `POST` | `/api/reservations` | Creates a new reservation booking. |
| `GET` | `/api/reservations` | Lists all reservations. |
| `POST` | `/api/orders` | Creates a new customer/waiter order. |
| `GET` | `/api/orders` | Lists all orders (supports `?for=kitchen` filter). |
| `PATCH` | `/api/orders/<id>/status` | Updates an order status (e.g., to `PREPARING` or `READY`). |

## 👩‍💻 Frontend Logic Summary

The application uses global functions and DOM manipulation (found in the `<script>` block of `index.html`) to manage state:

* **`menuCache`**: Stores menu data retrieved from the backend.
* **`cart`**: Stores items added by the customer.
* **`currentRole`**: Tracks the currently active interface panel.
* **`loggedRole`**: Tracks the user role after successful login.
* **`loadMenu()`**: Fetches menu data and renders the menu cards.
* **`placeOrder()`**: Gathers cart details and submits a `POST` request to the `/api/orders` endpoint.

---
## 🧑‍🤝‍🧑 Team Members

* **Adam Soman**: Frontend Development, UI/UX.
* **Hadi Alnader**: Project Documentation, Testing.
* **Anas**: Database/Backend Structure.
* **Mohammed Sami**: Analytics and Smart Features (Simulated).
