// ===============================
// API & Utility Functions
// ===============================
const API_BASE_URL = "https://complaints-api-xyz.onrender.com"; // Updated API URL

function getLoggedInUser() {
    return JSON.parse(sessionStorage.getItem('loggedInUser'));
}

function isLoggedIn() {
    return !!sessionStorage.getItem('loggedInUser');
}

function setLoggedInUser(user) {
    sessionStorage.setItem('loggedInUser', JSON.stringify(user));
}

function clearLoggedInUser() {
    sessionStorage.removeItem('loggedInUser');
    window.location.href = 'index.html';
}

// ===============================
// Main Logic
// ===============================
document.addEventListener('DOMContentLoaded', () => {

    // ===============================
    // Admin Login
    // ===============================
    const adminLoginForm = document.getElementById("adminLoginForm");
    if (adminLoginForm) {
        adminLoginForm.addEventListener("submit", async e => {
            e.preventDefault();

            const username = document.getElementById("admin-user").value.trim();
            const password = document.getElementById("admin-pass").value.trim();

            try {
                const response = await fetch(`${API_BASE_URL}/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });

                const result = await response.json();
                if (response.ok) {
                    setLoggedInUser(result);
                    window.location.href = "admin-dashboard.html";
                } else {
                    alert(result.error);
                }
            } catch (error) {
                console.error("Login failed:", error);
                alert("Login failed. Check server connection.");
            }
        });
    }

    // ===============================
    // Citizen Signup
    // ===============================
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', async e => {
            e.preventDefault();
            const name = document.getElementById('signup-name').value;
            const email = document.getElementById('signup-email').value;
            const password = document.getElementById('signup-password').value;

            try {
                const response = await fetch(`${API_BASE_URL}/signup`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, password })
                });

                const result = await response.json();
                if (response.ok) {
                    alert('Signup successful! Please log in.');
                    window.location.href = 'citizen-login.html';
                } else {
                    alert(result.error);
                }
            } catch (error) {
                console.error("Signup failed:", error);
                alert("Signup failed. Check server connection.");
            }
        });
    }

    // ===============================
    // Citizen Login
    // ===============================
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async e => {
            e.preventDefault();
            const email = document.getElementById('citizen-email').value;
            const password = document.getElementById('citizen-password').value;

            try {
                const response = await fetch(`${API_BASE_URL}/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });

                const result = await response.json();
                if (response.ok) {
                    setLoggedInUser(result);
                    window.location.href = 'citizen-dashboard.html';
                } else {
                    alert(result.error);
                }
            } catch (error) {
                console.error("Login failed:", error);
                alert("Login failed. Check server connection.");
            }
        });
    }

    // ===============================
    // New Complaint Submission
    // ===============================
    const complaintForm = document.getElementById('complaintForm');
    if (complaintForm) {
        complaintForm.addEventListener('submit', submitComplaint);
    }

    async function submitComplaint(event) {
        event.preventDefault();

        const user = getLoggedInUser();
        if (!user) {
            alert("You must be logged in to submit a complaint.");
            window.location.href = "citizen-login.html";
            return;
        }

        const title = document.getElementById("complaint-title").value.trim();
        const description = document.getElementById("complaint-desc").value.trim();
        const location = document.getElementById("complaint-location").value.trim();

        if (!title || !description || !location) {
            alert("Please fill in all fields.");
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/complaints`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    title,
                    description,
                    location,
                    user_id: user.user_id
                })
            });

            const result = await response.json();
            if (response.ok) {
                const dept = result.complaint.department;
                const resDiv = document.getElementById("classificationResult");
                if (resDiv) {
                    document.getElementById("predDept").textContent = dept;
                    resDiv.classList.remove("hidden");
                }
                alert(`Complaint submitted! Assigned to ${dept}`);
                window.location.href = "citizen-dashboard.html";
            } else {
                alert("Submission failed: " + result.error);
            }
        } catch (err) {
            console.error("Error during complaint submission:", err);
            alert("Server error. Check console.");
        }
    }

    // ===============================
    // Render Citizen Dashboard
    // ===============================
    const citizenTableBody = document.querySelector('#complaintsTable tbody');
    if (citizenTableBody) {
        renderCitizenComplaints();

        document.getElementById('sortOption').addEventListener('change', renderCitizenComplaints);
        document.getElementById('filterStatus').addEventListener('change', renderCitizenComplaints);
        document.getElementById('searchBox').addEventListener('input', renderCitizenComplaints);
    }

    async function renderCitizenComplaints() {
        const user = getLoggedInUser();
        if (!user) return;

        try {
            const response = await fetch(`${API_BASE_URL}/complaints/user/${user.user_id}`);
            let complaints = await response.json();

            const filterVal = document.getElementById('filterStatus').value;
            if (filterVal !== "all") {
                complaints = complaints.filter(c => c.status === filterVal);
            }

            const searchVal = document.getElementById('searchBox').value.toLowerCase();
            if (searchVal) {
                complaints = complaints.filter(c =>
                    c.title.toLowerCase().includes(searchVal) ||
                    c.description.toLowerCase().includes(searchVal) ||
                    c.location.toLowerCase().includes(searchVal) ||
                    c.department.toLowerCase().includes(searchVal)
                );
            }

            const sortVal = document.getElementById('sortOption').value;
            complaints.sort((a, b) => {
                if (sortVal === "date") return new Date(b.registered) - new Date(a.registered);
                return a[sortVal].localeCompare(b[sortVal]);
            });

            citizenTableBody.innerHTML = "";
            complaints.forEach(c => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${c.title}</td>
                    <td>${c.description}</td>
                    <td>${c.location}</td>
                    <td>${c.department}</td>
                    <td>${c.status}</td>
                    <td>${c.registered.split('T')[0]}</td>
                    <td><button onclick="deleteComplaint('${c.id}')">Delete</button></td>
                `;
                citizenTableBody.appendChild(row);
            });
        } catch (error) {
            console.error("Error fetching complaints:", error);
        }
    }
    
    // ===============================
    // Admin Dashboard
    // ===============================
    const adminTableBody = document.getElementById('adminComplaintsBody');
    if (adminTableBody) renderAdminComplaints();

    const sortDropdown = document.getElementById('adminSort');
    if (sortDropdown) {
        sortDropdown.addEventListener('change', () => {
            renderAdminComplaints(sortDropdown.value);
        });
    }

    async function renderAdminComplaints(sortBy = null) {
        const user = getLoggedInUser();
        if (!user) return;

        try {
            const response = await fetch(`${API_BASE_URL}/complaints`);
            let complaints = await response.json();
            
            const welcomeEl = document.getElementById("welcomeAdmin");
            if (welcomeEl) {
                if (user.role === "superadmin") {
                    welcomeEl.textContent = "Welcome Super Admin - You can manage all complaints.";
                } else {
                    complaints = complaints.filter(c => c.department === user.department);
                    welcomeEl.textContent = `Welcome ${user.department} Admin - You can manage only your department's complaints.`;
                }
            }
            
            if (sortBy) {
                complaints.sort((a, b) => {
                    if (sortBy === "date") return new Date(b.registered) - new Date(a.registered);
                    return a[sortBy].localeCompare(b[sortBy]);
                });
            }

            adminTableBody.innerHTML = "";
            complaints.forEach(c => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${c.id}</td>
                    <td>${c.title}</td>
                    <td>${c.location}</td>
                    <td>${c.department}</td>
                    <td>${c.citizen_email}</td>
                    <td>${c.registered.split('T')[0]}</td>
                    <td>${c.resolved ? c.resolved.split('T')[0] : '-'}</td>
                    <td>
                        <select onchange="updateComplaintStatus('${c.id}', this.value)">
                            <option value="Registered" ${c.status === "Registered" ? "selected" : ""}>Registered</option>
                            <option value="In Progress" ${c.status === "In Progress" ? "selected" : ""}>In Progress</option>
                            <option value="Resolved" ${c.status === "Resolved" ? "selected" : ""}>Resolved</option>
                        </select>
                    </td>
                    <td><button onclick="deleteComplaint('${c.id}')">Delete</button></td>
                `;
                adminTableBody.appendChild(row);
            });
        } catch (error) {
            console.error("Error fetching complaints:", error);
        }
    }

    // ===============================
    // Delete & Update Functions
    // ===============================
    window.deleteComplaint = async function (id) {
        if (!confirm("Are you sure you want to delete this complaint?")) return;
        try {
            const response = await fetch(`${API_BASE_URL}/complaints/${id}`, { method: 'DELETE' });
            if (response.ok) {
                alert("Complaint deleted.");
                location.reload();
            } else {
                const result = await response.json();
                alert(result.error);
            }
        } catch (error) {
            console.error("Error deleting complaint:", error);
            alert("Error deleting complaint. Check server connection.");
        }
    };

    window.updateComplaintStatus = async function (id, status) {
        try {
            const response = await fetch(`${API_BASE_URL}/complaints/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status })
            });

            if (response.ok) {
                location.reload();
            } else {
                const result = await response.json();
                alert(result.error);
            }
        } catch (error) {
            console.error("Error updating complaint:", error);
            alert("Error updating complaint. Check server connection.");
        }
    };

    // Logout
    const logoutBtn = document.querySelector('a[href="index.html"]');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', clearLoggedInUser);
    }
});