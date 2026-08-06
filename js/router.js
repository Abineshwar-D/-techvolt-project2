document.addEventListener("DOMContentLoaded", async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const userId = urlParams.get('user_id');

  // 1. Automatically detect the current HTML filename (e.g., "Production_Executive.html")
  const currentPage = window.location.pathname.split('/').pop();

  // 2. Missing user_id parameter check
  if (!userId || userId.trim() === "") {
    alert("Unauthorized access! User ID is missing.");
    window.location.href = "/techvoltInstituteProject/pages/login.html";
    return;
  }

  try {
    // 3. Send BOTH user_id AND current page filename to Python backend
    const verifyUrl = `../py/verify_user.py?user_id=${encodeURIComponent(userId)}&page=${encodeURIComponent(currentPage)}`;

    const response = await fetch(verifyUrl);
    const data = await response.json();

    // 4. Handle authorization failure / blocked accounts / wrong role
    if (data.status !== "success") {
      alert(data.message);
      window.location.href = "/techvoltInstituteProject/pages/login.html";
      return;
    }

    // 5. Access Granted
    console.log(`Access Granted for ${userId} (${data.role}) on page ${currentPage}`);

  } catch (error) {
    console.error("Verification error:", error);
    alert("Authentication error. Returning to login.");
    window.location.href = "/techvoltInstituteProject/pages/login.html";
  }
});