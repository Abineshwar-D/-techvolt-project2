/* ==========================================================================
   MERCHANDISING DASHBOARD JS
   - Strictly preserved original functions and logic
   - Organized into clean, distinct module blocks
   ========================================================================== */


/* ==========================================================================
   01. GLOBAL LAYOUT & SIDEBAR NAVIGATION
   ========================================================================== */

// Mobile Sidebar Toggle
document.getElementById('sidebarToggle').addEventListener('click', function() {
    document.getElementById('sidebar').classList.toggle('open');
});

// Close sidebar on outside click (mobile)
document.addEventListener('click', function(e) {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.getElementById('sidebarToggle');
    if (window.innerWidth < 992) {
        if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    }
});

// Toggle button functionality
document.querySelectorAll('.btn-toggle').forEach(btn => {
    btn.addEventListener('click', function() {
        const parent = this.closest('.d-flex');
        parent.querySelectorAll('.btn-toggle').forEach(b => {
            b.classList.remove('active');
            b.classList.add('inactive');
        });
        this.classList.add('active');
        this.classList.remove('inactive');
    });
});

// Quick action click feedback
document.querySelectorAll('.quick-action').forEach(action => {
    action.addEventListener('click', function() {
        this.style.transform = 'scale(0.98)';
        setTimeout(() => {
            this.style.transform = 'scale(1)';
        }, 200);
    });
});

// Nav Item Click Handler
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function(e) {
        e.preventDefault();
        document.querySelectorAll('.nav-item').forEach(nav => {
            nav.classList.remove('active');
        });
        this.classList.add('active');
    });
});


/* ==========================================================================
   02. MERCHANDISING DASHBOARD MAIN SCREEN (PAGE 1)
   ========================================================================== */

document.addEventListener("DOMContentLoaded", function () {
    fetch("../py/dashboard/get_merchandising.py")
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                document.getElementById("kpi-card1").innerText = data.card1;
                document.getElementById("kpi-card2").innerText = data.card2;
                document.getElementById("kpi-card3").innerText = data.card3;
                document.getElementById("kpi-card4").innerText = data.card4;
                document.getElementById("kpi-card5").innerText = data.card5;
                document.getElementById("kpi-card6").innerText = data.card6;
            } else {
                console.error("Error fetching KPI data:", data.message);
            }
        })
        .catch(error => {
            console.error("Network or script error:", error);
        });
});


/* ==========================================================================
   03. ORDERS SCREEN (PAGE 3)
   ========================================================================== */

function loadOrdersData(){
    var ordersTableBody = document.getElementById("ordersTableBody");
    if (ordersTableBody) {
        fetch("../py/orders/get_orders.py")
        .then(response => response.json())
        .then(data => {
            if (data.status === "success" || data.kpis) {
                document.getElementById("kpiTotalOrders").innerText = data.kpis.total.toLocaleString();
                document.getElementById("kpiRunningOrders").innerText = data.kpis.running.toLocaleString();
                document.getElementById("kpiCompletedOrders").innerText = data.kpis.completed.toLocaleString();
                document.getElementById("kpiPendingOrders").innerText = data.kpis.pending.toLocaleString();

                ordersTableBody.innerHTML = data.rows_html;
            } else {
                ordersTableBody.innerHTML = "<tr><td colspan='5' class='text-danger'>Failed to load data.</td></tr>";
            }
        })
        .catch(err => {
            console.error("Error loading orders and KPIs:", err);
            ordersTableBody.innerHTML = "<tr><td colspan='5' class='text-danger'>Error connecting to server.</td></tr>";
        });
    }
}

document.addEventListener("DOMContentLoaded", function() {
    loadOrdersData();
    setInterval(loadOrdersData, 5000);
});


//THIS FUNCTION IS USED TO SEARCH ORDER
document.addEventListener('DOMContentLoaded', function () {
    const searchOrder = document.getElementById('searchOrder');
    const ordersTableBody = document.getElementById('ordersTableBody');

    function filterOrders() {
        const query = searchOrder.value.toLowerCase().trim();
        const rows = ordersTableBody.getElementsByTagName('tr');

        Array.from(rows).forEach(row => {
            // Get text from each column
            const orderNo = row.children[0]?.textContent.toLowerCase() || '';
            const customer = row.children[1]?.textContent.toLowerCase() || '';
            const quantity = row.children[2]?.textContent.toLowerCase() || '';
            const deliveryDate = row.children[3]?.textContent.toLowerCase() || '';

            // Match query against ANY column (Order No, Customer, Quantity, or Date)
            const matches = orderNo.includes(query) ||
                            customer.includes(query) ||
                            quantity.includes(query) ||
                            deliveryDate.includes(query);

            if (matches) {
                row.style.display = ''; // Show row
            } else {
                row.style.display = 'none'; // Hide row
            }
        });
    }

    // Trigger search on input
    searchOrder.addEventListener('input', filterOrders);
});


/* ==========================================================================
   04. PURCHASE ORDERS (PO) SCREEN (PAGE 5)
   ========================================================================== */

document.querySelectorAll('.table-custom tbody tr').forEach(row => {
    row.addEventListener('click', function() {
        document.querySelectorAll('.table-custom tbody tr').forEach(r => {
            r.classList.remove('selected');
        });
        this.classList.add('selected');

        const poNumber = this.querySelector('.po-number')?.textContent || 'PO001';
        const supplier = this.querySelector('.supplier-name')?.textContent || 'ABC Yarns';
        const material = this.querySelectorAll('td')[2]?.textContent || 'Cotton Yarn';
        const quantity = this.querySelectorAll('td')[3]?.textContent || '2000 Kg';

        const detailHeader = document.querySelector('.details-header h3');
        if (detailHeader) detailHeader.textContent = poNumber;

        const detailItems = document.querySelectorAll('.detail-item .value');
        if (detailItems.length >= 4) {
            detailItems[0].textContent = supplier;
            detailItems[2].textContent = quantity;
        }

        const statusBadge = document.querySelector('.priority-badge');
        const statusCell = this.querySelector('.status-badge');
        if (statusBadge && statusCell) {
            statusBadge.textContent = statusCell.textContent.trim();
            statusBadge.className = 'priority-badge';
            if (statusCell.classList.contains('pending')) {
                statusBadge.style.background = '#e65100';
            } else if (statusCell.classList.contains('approved')) {
                statusBadge.style.background = '#2e7d32';
            } else if (statusCell.classList.contains('rejected')) {
                statusBadge.style.background = '#c62828';
            }
        }

        console.log('PO Selected:', poNumber);
    });
});

const searchPoKeyUp = document.getElementById("SearchPo");
if (searchPoKeyUp) {
    searchPoKeyUp.addEventListener("keyup", function () {
        let search = this.value.toLowerCase();

        document.querySelectorAll("#poTableBody tr").forEach(row => {
            row.style.display = row.textContent.toLowerCase().includes(search)
                ? ""
                : "none";
        });
    });
}

const poTableBodyElem = document.getElementById("poTableBody");
if (poTableBodyElem) {
    poTableBodyElem.addEventListener("click", function(e) {
        const row = e.target.closest("tr");
        if (!row) return;

        document.querySelectorAll("#poTableBody tr").forEach(r => {
            r.classList.remove("selected");
        });

        row.classList.add("selected");

        const poNumber = row.cells[0].textContent.trim();
        const supplier = row.cells[1].textContent.trim();
        const material = row.cells[2].textContent.trim();
        const quantity = row.cells[3].textContent.trim();
        const status = row.querySelector(".status-badge").textContent.trim();

        document.getElementById("detailPo").textContent = poNumber;
        document.getElementById("detailSupplier").textContent = supplier;
        document.getElementById("detailMaterial").textContent = material;
        document.getElementById("detailQuantity").textContent = quantity;
        document.getElementById("Status").textContent = status;
    });
}

// Master function to fetch both the Table and the KPIs
function refreshAllData() {
    const tableBody = document.getElementById("poTableBody");

    // 1. FETCH TABLE DATA (HTML)
fetch("../py/purchase/get_po_list.py?t=" + new Date().getTime())
    .then(response => {
        if (!response.ok) throw new Error(`HTTP Error ${response.status}`);
        return response.text();
    })
    .then(data => {
        if (data.trim() && tableBody) {
            tableBody.innerHTML = data;
        } else if (tableBody) {
            //  Show a clean message if no data exists instead of crashing
            tableBody.innerHTML = `<tr><td colspan="10" style="text-align:center;">No PO records found</td></tr>`;
        }

        if (typeof initializeTableEvents === "function") {
            initializeTableEvents();
        }
    })
    .catch(err => {
        console.error("Table fetch error:", err);
    });

    // 2. FETCH KPI DATA (JSON)
    fetch("../py/purchase/get_po_kpis.py?t=" + new Date().getTime())
        .then(response => {
            if (!response.ok) throw new Error(`HTTP Error ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (data.status === "success") {
                const totalPoElem = document.getElementById("kpi-total-po");
                const pendingPoElem = document.getElementById("kpi-pending-po");

                if (totalPoElem) totalPoElem.innerText = data.total_po ?? 0;
                if (pendingPoElem) pendingPoElem.innerText = data.pending_po ?? 0;
            } else {
                console.error("Error fetching PO KPIs:", data.message);
            }
        })
        .catch(error => {
            console.error("KPI fetch error:", error);
        });
}

// 1. Trigger when DOM page finishes loading
document.addEventListener('DOMContentLoaded', function() {
    refreshAllData();
});

// 2. Trigger automatically whenever the user switches back to this browser tab!
window.addEventListener("focus", function () {
    refreshAllData();
});

/* ==========================================================================
   05. ADD PURCHASE ORDER SCREEN
   ========================================================================== */

console.log("JS LOADED");

document.querySelectorAll('input[name="priority"]').forEach(radio => {
    radio.addEventListener('change', function() {
        const badge = document.getElementById('priorityBadge');
        if (!badge) return;
        const label = this.nextElementSibling.textContent;
        badge.textContent = label + ' Priority';
        badge.className = 'priority-badge';

        if (label === 'High') {
            badge.classList.add('bg-error-container', 'text-on-error-container');
        } else if (label === 'Medium') {
            badge.classList.add('medium');
        } else {
            badge.classList.add('low');
        }
    });
});

function showpurchasedToast() {
    const toast = document.getElementById('SuccessAddPO');
    if (toast) toast.style.display = 'flex';
}

function hidepurchasedToast() {
    const toast = document.getElementById('SuccessAddPO');
    if (toast) toast.style.display = 'none';
}

function handlepurchasedSubmit(e) {
    e.preventDefault();
    showpurchasedToast();
    setTimeout(hidepurchasedToast, 5000);
}

document.addEventListener("DOMContentLoaded", function () {
    const supplierSelect = document.getElementById("supplier");
    const materialSelect = document.getElementById("material");
    const availableStockInput = document.getElementById("available_stock");

    if (!supplierSelect || !materialSelect || !availableStockInput) return;

    fetch('../py/purchase/get_supplier_option.py')
        .then(response => response.json())
        .then(suppliers => {
            supplierSelect.innerHTML = '<option value="">Select Supplier</option>';
            if (Array.isArray(suppliers)) {
                suppliers.forEach(sup => {
                    supplierSelect.innerHTML += `<option value="${sup.code}">${sup.name}</option>`;
                });
            }
        })
        .catch(err => console.error("Error loading suppliers:", err));

    supplierSelect.addEventListener("change", function () {
    const supplierCode = this.value;

    materialSelect.innerHTML = '<option value="">Select Material</option>';
    availableStockInput.value = "0";

    if (!supplierCode) return;

    fetch(`../py/purchase/get_supplier_material.py?supplier_code=${encodeURIComponent(supplierCode)}`)
        .then(response => response.json())
        .then(data => {
            // Safely get materials array whether sent as data or data.materials
            const materials = Array.isArray(data) ? data : (data.materials || []);

            if (materials.length > 0) {
                materials.forEach(mat => {
                    materialSelect.innerHTML += `<option value="${mat}">${mat}</option>`;
                });
            } else {
                materialSelect.innerHTML = '<option value="">No Materials Found</option>';
            }
        })
        .catch(err => console.error("Error loading materials:", err));
});

    materialSelect.addEventListener("change", function () {
    const materialName = this.value;

    // Reset input if default blank option is selected
    if (!materialName) {
        availableStockInput.value = "0";
        return;
    }

    fetch(`../py/purchase/get_material_option.py?material_name=${encodeURIComponent(materialName)}`)
        .then(response => response.json())
        .then(data => {
            // If material is in 'materials' table -> fills with real stock value
            // If material is ONLY in 'supplier' table -> fills with 0
            if (data && data.stock !== undefined) {
                availableStockInput.value = data.stock;
            } else {
                availableStockInput.value = "0";
            }
        })
        .catch(err => {
            console.error("Error checking material stock:", err);
            availableStockInput.value = "0";
        });
});
});

const poForm = document.getElementById("poForm");
if (poForm) {
    poForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const submitBtn = this.querySelector('button[type="submit"]');
        if (submitBtn) submitBtn.disabled = true;

        const currentUserId = getActiveUserId() || "EMP001";
        const userIdInput = document.getElementById("po_user_id");
        if (userIdInput) userIdInput.value = currentUserId;

        let formData = new FormData(this);

        fetch("../py/purchase/save_po.py", {
            method: "POST",
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                window.location.href = `/techvoltInstituteProject/pages/Merchandising.html?user_id=${encodeURIComponent(currentUserId)}#page5`;
            } else {
                alert("Failed to save: " + data.message);
            }
        })
        .catch(err => {
            console.error("Error saving PO:", err);
            alert("Server Error: Check browser console (F12).");
        })
        .finally(() => {
            if (submitBtn) submitBtn.disabled = false;
        });
    });
}

//SHOWING DELIVERY DATE TODAY
document.addEventListener("DOMContentLoaded", function() {
    // Uses your exact line with [0], matching name="expected_delivery" from your HTML
    const deliveryDateInput = document.getElementsByName("expected_delivery")[0];
    if (!deliveryDateInput) return;

    function validateDates() {
        // Removed "if (deliveryDateInput.value)" so min works even when the field is empty
        const today = new Date();
        const minDate = new Date(today);
        minDate.setDate(today.getDate() + 1);

        // This disables past dates and today in the calendar picker
        deliveryDateInput.min = minDate.toISOString().split('T')[0];
    }

    validateDates();

    deliveryDateInput.addEventListener("change", function() {
        const todayStr = new Date().toISOString().split('T')[0];

        if (this.value <= todayStr) {
            alert("Delivery Date must be after today's date.");
            this.value = "";
        }
    });
});


/* ==========================================================================
   06. SUPPLIER SCREEN (PAGE 4)
   ========================================================================== */

// THIS FUNCTION LOADS SUPPLIER TABLE DATA & KPIS
function loadSuppliersAndKPIs() {
    var supplierTableBody = document.getElementById("supplierTableBody");

    if (supplierTableBody) {
        // Adding ?t= prevents browser caching
        fetch("../py/supplier/get_supplier.py?t=" + new Date().getTime())
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error("Database Error:", data.error);
                return;
            }

            // Update KPI Cards
            const totalElem = document.getElementById("totalSuppliersCount");
            const activeElem = document.getElementById("activeSuppliersCount");
            const inactiveElem = document.getElementById("inactiveSuppliersCount");

            if (totalElem) totalElem.innerText = data.total ?? 0;
            if (activeElem) activeElem.innerText = data.active ?? 0;
            if (inactiveElem) inactiveElem.innerText = data.inactive ?? 0;

            // Update Table HTML
            supplierTableBody.innerHTML = data.table_html || '';
        })
        .catch(error => {
            console.error("Error fetching supplier data:", error);
            supplierTableBody.innerHTML = "<tr><td colspan='7' class='text-danger text-center'>Error connecting to server.</td></tr>";
        });
    }
}

// Auto-refresh logic on DOM load and 5-second interval
document.addEventListener("DOMContentLoaded", function () {
    loadSuppliersAndKPIs();
    setInterval(loadSuppliersAndKPIs, 5000);
});

// Auto-refresh when switching back to this window/screen
window.addEventListener("focus", function () {
    loadSuppliersAndKPIs();
});

//THIS FUNCTION IS USED TO SEARCH SUPPLIER
document.addEventListener('DOMContentLoaded', function () {
    const searchSupplier = document.getElementById('searchSupplier');
    const supplierStatus = document.getElementById('supplierStatus');
    const supplierRefresh = document.getElementById('supplierRefresh');
    const supplierTableBody = document.getElementById('supplierTableBody');

    // Filter Function
    function filterSuppliers() {
        const query = searchSupplier.value.toLowerCase().trim();
        const selectedStatus = supplierStatus.value.toLowerCase().trim();
        const rows = supplierTableBody.getElementsByTagName('tr');

        Array.from(rows).forEach(row => {
            // Get text from columns
            const name = row.children[0]?.textContent.toLowerCase() || '';
            const contact = row.children[1]?.textContent.toLowerCase() || '';
            const phone = row.children[2]?.textContent.toLowerCase() || '';
            const email = row.children[3]?.textContent.toLowerCase() || '';
            const address = row.children[4]?.textContent.toLowerCase() || '';
            const status = row.children[5]?.textContent.toLowerCase() || '';

            // Check if search matches ANY text column
            const matchesSearch = name.includes(query) ||
                                  contact.includes(query) ||
                                  phone.includes(query) ||
                                  email.includes(query) ||
                                  address.includes(query);

            // Check if status dropdown matches
            const matchesStatus = (selectedStatus === '') || status.includes(selectedStatus);

            // Toggle visibility
            if (matchesSearch && matchesStatus) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    // Event Listeners
    searchSupplier.addEventListener('input', filterSuppliers);
    supplierStatus.addEventListener('change', filterSuppliers);

    // Refresh/Reset Button
    supplierRefresh.addEventListener('click', function () {
        searchSupplier.value = '';
        supplierStatus.value = '';
        filterSuppliers();
    });
});

/* ==========================================================================
   07. ADD SUPPLIER SCREEN
   ========================================================================== */

const supplierInputs = {
    'input_name': 'preview_name',
    'input_contact': 'preview_contact',
    'input_phone': 'preview_phone',
    'input_email': 'preview_email',
    'input_material': 'preview_material',
    'input_city': 'preview_city'
};

Object.entries(supplierInputs).forEach(([id, previewId]) => {
    const inputEl = document.getElementById(id);
    const previewEl = document.getElementById(previewId);

    if (inputEl && previewEl) {
        inputEl.addEventListener('input', function(e) {
            previewEl.textContent = e.target.value || '—';
        });
    }
});

function showsupplierToast() {
    const toast = document.getElementById('AddsupplierToadt');
    if (toast) toast.classList.add('show');

    setTimeout(() => {
        hidesupplierToast();
    }, 5000);
}

function hidesupplierToast() {
    const toast = document.getElementById('AddsupplierToadt');
    if (toast) toast.classList.remove('show');
}

function handleSubmit(e) {
    e.preventDefault();
    showsupplierToast();
}


/* ==========================================================================
   08. LOGOUT MODAL & ACTIONS
   ========================================================================== */

const modal = document.getElementById('logoutModal');
const btnLogout = document.getElementById('btnLogout');
const btnCancel = document.getElementById('btnCancel');

// Show modal smoothly when page/section loads
window.addEventListener('load', function() {
    setTimeout(() => {
        if (modal) modal.classList.add('show');
    }, 100);
});

// "No, Stay Logged In" Action
if (btnCancel) {
    btnCancel.addEventListener('click', function() {
        if (modal) {
            modal.style.transform = 'scale(0.95)';
            modal.style.opacity = '0';
            modal.style.transition = 'transform 0.3s ease, opacity 0.3s ease';
        }

        setTimeout(() => {
            // Option 1: Go back in browser history if came from a page
            if (window.history.length > 1) {
                window.history.back();
            } else {
                // Option 2: Fallback hash navigation to main dashboard section
                const urlParams = new URLSearchParams(window.location.search);
                const userId = urlParams.get('user_id') || '';
                window.location.hash = '#page1';
            }

            // Reset modal styles for future display
            if (modal) {
                modal.style.transform = 'scale(1)';
                modal.style.opacity = '1';
            }
        }, 300);
    });
}

// "Yes, Logout" Action
if (btnLogout) {
    btnLogout.addEventListener('click', function() {
        // Show loading spinner animation
        this.innerHTML = '<span class="spinner"><i class="bi bi-arrow-repeat spin"></i></span> Logging out...';
        this.disabled = true;
        this.style.opacity = '0.7';

        // Add optional CSS animation class if icon needs spinning
        const icon = this.querySelector('i');
        if (icon) icon.style.animation = 'spin 1s linear infinite';

        setTimeout(() => {
            // Smoothly fade out body
            document.body.style.opacity = '0';
            document.body.style.transition = 'opacity 0.5s ease-out';

            setTimeout(() => {
                // Clear all session storage & local storage data
                sessionStorage.clear();
                localStorage.clear();

                // Redirect to actual Login page
                window.location.href = '/techvoltInstituteProject/pages/login.html';
            }, 500);
        }, 800);
    });
}