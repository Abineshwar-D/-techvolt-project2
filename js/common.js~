// common.js - Included in ALL HTML pages

// 1. Helper function to extract user ID from URL or storage
function getActiveUserId() {
    const urlParams = new URLSearchParams(window.location.search);

    const userId =
        urlParams.get("user_id") ||
        urlParams.get("admin_id") ||
        urlParams.get("id") ||
        localStorage.getItem("user_id") ||
        sessionStorage.getItem("user_id");

    if (userId && userId.trim() !== "" && userId !== "null" && userId !== "undefined") {
        return userId.trim();
    }
    return null;
}

// 2. Load User Profile Header Info from Python Backend
function loadUserProfileHeader() {
    const userId = getActiveUserId();

    if (!userId) {
        console.warn("No valid user ID found in URL/Storage.");
        return;
    }

    // Call Python backend
    fetch(`/techvoltInstituteProject/py/getuserinformation/get_user_information.py?user_id=${encodeURIComponent(userId)}`)
        .then(response => response.json())
        .then(res => {
            if (res.success && res.data) {
                const user = res.data;

                // Target Header Elements
                const nameElem = document.getElementById("header-user-name");
                const roleElem = document.getElementById("header-user-role");

                if (nameElem) nameElem.textContent = user.fullname || user.employee_id;
                if (roleElem) roleElem.textContent = (user.role || "").toUpperCase();

                // Save user details locally for global usage
                localStorage.setItem("user_info", JSON.stringify(user));
            } else {
                console.error("Failed to load user details:", res.message);
            }
        })
        .catch(err => {
            console.error("Error fetching user header info:", err);
        });
}

// 3. Automatically execute when page loads
document.addEventListener("DOMContentLoaded", function () {
    // Validate session
    const userId = getActiveUserId();
    if (!userId) {
        alert("Session invalid or User ID missing. Please log in again.");
        window.location.href = "/techvoltInstituteProject/pages/login.html";
        return;
    }

    // Preserve user ID in storage
    localStorage.setItem('user_id', userId);
    sessionStorage.setItem('user_id', userId);

    // Update Header with User Name & Role
    loadUserProfileHeader();
});