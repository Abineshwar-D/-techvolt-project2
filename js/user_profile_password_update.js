// Helper: Extract active user_id
function getActiveUserId() {
    const urlParams = new URLSearchParams(window.location.search);
    const userId = urlParams.get("user_id") ||
                   urlParams.get("admin_id") ||
                   localStorage.getItem("user_id") ||
                   sessionStorage.getItem("user_id");
    return userId ? userId.trim() : null;
}

// Load Header Info
function loadUserProfileHeader() {
    const userId = getActiveUserId();
    if (!userId) return;

    fetch(`../py/getuserinformation/get_user_profile.py?action=fetch&user_id=${encodeURIComponent(userId)}`)
        .then(res => res.json())
        .then(res => {
            if (res.success && res.data) {
                const u = res.data;

                if (document.getElementById("header-user-name")) document.getElementById("header-user-name").textContent = u.fullname || u.employee_id;
                if (document.getElementById("header-user-role")) document.getElementById("header-user-role").textContent = u.role || "";
                if (document.getElementById("header-dropdown-userid")) document.getElementById("header-dropdown-userid").textContent = u.employee_id;
                if (document.getElementById("pwd_email")) document.getElementById("pwd_email").value = u.email || "";

                if (u.profile_pic && u.profile_pic !== "null" && document.getElementById("header-user-avatar")) {
                    document.getElementById("header-user-avatar").src = u.profile_pic + "?t=" + new Date().getTime();
                }
            }
        })
        .catch(err => console.error("Profile load error:", err));
}

// Single Upload Handler Function
function uploadProfilePicture(input) {
    const userId = getActiveUserId();
    if (!input.files || !input.files[0] || !userId) return;

    let formData = new FormData();
    formData.append("action", "upload_pic");
    formData.append("user_id", userId);
    formData.append("profile_pic", input.files[0]);

    fetch("../py/getuserinformation/get_user_profile.py", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            const avatarImg = document.getElementById("header-user-avatar");
            if (avatarImg) {
                avatarImg.src = data.image_url + "?t=" + new Date().getTime();
            }
        } else {
            alert("Upload Failed: " + data.message);
        }
        // Reset file input value so selecting the same file again triggers change event
        input.value = "";
    })
    .catch(err => {
        console.error("Upload error:", err);
        alert("Server error during photo upload.");
        input.value = "";
    });
}

document.addEventListener("DOMContentLoaded", function () {
    loadUserProfileHeader();

    const fileInput = document.getElementById("profilePicInput");
    if (fileInput) {
        // Clone element or remove existing listeners to avoid duplicate bindings
        fileInput.replaceWith(fileInput.cloneNode(true));
        const cleanFileInput = document.getElementById("profilePicInput");
        cleanFileInput.addEventListener("change", function () {
            uploadProfilePicture(this);
        });
    }

    const pwdForm = document.getElementById("changePasswordForm");
    if (pwdForm) {
        pwdForm.addEventListener("submit", function (e) {
            e.preventDefault();

            const userId = getActiveUserId();
            const newPwd = document.getElementById("pwd_new").value;
            const confirmPwd = document.getElementById("pwd_confirm").value;

            if (newPwd !== confirmPwd) {
                alert("New password and confirm password do not match!");
                return;
            }

            let formData = new FormData();
            formData.append("action", "change_password");
            formData.append("user_id", userId);
            formData.append("new_password", newPwd);

            fetch("../py/getuserinformation/get_user_profile.py", {
                method: "POST",
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    const modalElem = document.getElementById('changePasswordModal');
                    if (modalElem && typeof bootstrap !== "undefined") {
                        const modal = bootstrap.Modal.getInstance(modalElem) || new bootstrap.Modal(modalElem);
                        modal.hide();
                    }
                    pwdForm.reset();
                } else {
                    alert("Error: " + data.message);
                }
            })
            .catch(err => console.error("Error changing password:", err));
        });
    }
});