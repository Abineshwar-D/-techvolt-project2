/* ==========================================================================
   MARKETING EXECUTIVE DASHBOARD JS
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
   02. MARKETING DASHBOARD MAIN SCREEN (PAGE 1)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
    calculateTotal();
    updateFabric();
    calculateTotal();
    loadFabricType();
    updateFabric();

    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                const delay = parseInt(entry.target.getAttribute('data-delay')) || 0;
                setTimeout(() => {
                    entry.target.classList.add('visible');
                }, delay);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.fade-in').forEach(el => {
        observer.observe(el);
    });

    const enquirySelect = document.getElementById('enquirySelect');
    if (enquirySelect) {
        enquirySelect.addEventListener('change', loadEnquiryData);
    }
});

document.addEventListener('DOMContentLoaded', function() {
    fetchEnquiryData();
    setInterval(fetchEnquiryData, 10000);

    updateDashboardStats();
    setInterval(updateDashboardStats, 5000);
});

function updateDashboardStats() {
    console.log('updateDashboardStats() called');
    console.log('Checking for dashTotalCustomers...');

    const dashboardElement = document.getElementById('dashTotalCustomers');
    console.log(' dashTotalCustomers found?', dashboardElement);

    if (!dashboardElement) {
        console.log('Not on dashboard page - skipping');
        return;
    }

    console.log('On dashboard page - continuing...');
    console.log('Updating dashboard stats...');

    fetch("../py/dashboard/get_dashboard_stats.py")
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                document.getElementById("dashTotalCustomers").innerText = data.kpis.total_customers.toLocaleString();
                document.getElementById("dashNewEnquiries").innerText = data.kpis.new_enquiries.toLocaleString();
                document.getElementById("dashQuotationsSent").innerText = data.kpis.quotations_sent.toLocaleString();
                document.getElementById("dashConfirmedOrders").innerText = data.kpis.confirmed_orders.toLocaleString();
                document.getElementById("dashTodayCount").innerText = data.kpis.today_enquiries.toLocaleString();

                document.getElementById("recentEnquiriesList").innerHTML = data.recent_enquiries_html;
            }
        })
        .catch(err => console.error("Error loading dashboard stats:", err));
}


/* ==========================================================================
   03. CUSTOMERS SCREEN (PAGE 2)
   ========================================================================== */
//
//document.querySelectorAll('.pagination-custom .page-btn').forEach(btn => {
//    btn.addEventListener('click', function() {
//        if (!this.disabled) {
//            document.querySelectorAll('.pagination-custom .page-btn').forEach(b => {
//                b.classList.remove('active');
//            });
//            this.classList.add('active');
//        }
//    });
//});
//
//fetch("../py/customer/get_customer.py")
//.then(res => res.text())
//.then(data => {
//    const custBody = document.getElementById("customerTableBody");
//    if (custBody) custBody.innerHTML = data;
//});
//
//function deleteCustomer(id) {
//    if (!confirm("Are you sure you want to delete this customer?")) return;
//
//    fetch("../py/customer/delete_customer.py?id=" + id)
//    .then(res => res.text())
//    .then(data => {
//        alert(data);
//        location.reload();
//    });
//}
//
//const searchCustElem = document.getElementById("searchCustomer");
//if (searchCustElem) {
//    searchCustElem.addEventListener("keyup", function () {
//        let search = this.value.toLowerCase();
//
//        document.querySelectorAll("#customerTableBody tr").forEach(row => {
//            row.style.display = row.textContent.toLowerCase().includes(search)
//                ? ""
//                : "none";
//        });
//    });
//}
//
//document.addEventListener("DOMContentLoaded", function () {
//    const tableBody = document.getElementById("customerTableBody");
//    if (!tableBody) return;
//
//    function loadCustomers() {
//        fetch('../py/customer/fetch_customer.py')
//            .then(response => response.text())
//            .then(html => {
//                tableBody.innerHTML = html;
//            });
//    }
//    loadCustomers();
//
//    tableBody.addEventListener("click", function (e) {
//        const btn = e.target.closest(".view-details-btn");
//        if (!btn) return;
//
//        const data = {
//            name: btn.getAttribute("data-name"),
//            email: btn.getAttribute("data-email"),
//            phone: btn.getAttribute("data-phone"),
//            company: btn.getAttribute("data-company"),
//            fabric: btn.getAttribute("data-fabric"),
//            gsm: btn.getAttribute("data-gsm"),
//            color: btn.getAttribute("data-color"),
//            price: btn.getAttribute("data-price"),
//            qty: btn.getAttribute("data-qty"),
//            remarks: btn.getAttribute("data-remarks"),
//            status: btn.getAttribute("data-status"),
//            badgeClass: btn.getAttribute("data-badge")
//        };
//
//        document.getElementById("modalCustomerName").innerText = data.name;
//        document.getElementById("modalEmail").innerText = data.email;
//        document.getElementById("modalPhone").innerText = `${data.phone} (${data.company})`;
//        document.getElementById("modalFabric").innerText = `${data.fabric} - ${data.gsm} GSM`;
//        document.getElementById("modalColor").innerText = data.color;
//        document.getElementById("modalPrice").innerText = `₹${data.price * data.qty} (Qty: ${data.qty})`;
//        document.getElementById("modalRemarks").innerText = data.remarks || "No remarks provided.";
//
//        const badge = document.getElementById("modalStatusBadge");
//        if (badge) {
//            badge.innerText = data.status;
//            badge.className = `badge ${data.badgeClass} mt-1`;
//        }
//
//        if (typeof myModal !== 'undefined') {
//            myModal.show();
//        }
//    });
//});


/* ==========================================================================
   04. ORDERS SCREEN (PAGE 3)
   ========================================================================== */

function updateFabric() {
    var fabricSelect = document.querySelector('[name="fabric_type"]');
    var gsmInput = document.querySelector('[name="gsm"]');
    var summaryFabric = document.getElementById("summaryFabric");
    if (fabricSelect && summaryFabric) {
        var fabricText = fabricSelect.options[fabricSelect.selectedIndex]?.text || "Select Fabric";
        var gsmText = gsmInput ? gsmInput.value : "0";
        summaryFabric.textContent = fabricText + " / " + gsmText + " GSM";
    }
}

function calculateTotal() {
    var qtyInput = document.getElementById("quantity1");
    var priceInput = document.getElementById("price");
    var summaryTotal = document.getElementById("summaryTotal");
    var totalAmounts = document.getElementById('totalAmounts');
    var summaryValue = document.getElementById('summaryValue');

    if (qtyInput && priceInput) {
        var qty = parseFloat(qtyInput.value) || 0;
        var priceVal = parseFloat(priceInput.value) || 0;
        var total = qty * priceVal;

        if (summaryTotal) summaryTotal.textContent = "₹ " + total.toLocaleString();

        var formatter = new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        });

        var formattedTotal = formatter.format(total);

        if (totalAmounts) totalAmounts.innerText = formattedTotal;
        if (summaryValue) summaryValue.textContent = formattedTotal;
    }
}

document.addEventListener("DOMContentLoaded", function() {
    document.addEventListener('click', function (event) {
        var btn = event.target.closest('.view-details-btn');
        if (btn) {
            event.preventDefault();

            var customer = btn.getAttribute('data-customer');
            var contact = btn.getAttribute('data-contact');
            var orderNo = btn.getAttribute('data-order');
            var fabric = btn.getAttribute('data-fabric');
            var gsm = btn.getAttribute('data-gsm');
            var color = btn.getAttribute('data-color');
            var total = btn.getAttribute('data-total');
            var remarks = btn.getAttribute('data-remarks');
            var priority = btn.getAttribute('data-priority');

            document.getElementById('modalCustomerName').innerText = customer || "--";
            document.getElementById('modalEmail').innerText = contact || "--";
            document.getElementById('modalPhone').innerText = orderNo || "--";
            document.getElementById('modalFabric').innerText = (fabric || "") + " (" + (gsm || "") + " GSM)";
            document.getElementById('modalColor').innerText = color || "--";
            document.getElementById('modalPrice').innerText = "₹" + (total || "0");
            document.getElementById('modalRemarks').innerText = remarks || "No remarks.";

            var badge = document.getElementById('modalStatusBadge');
            if (badge) {
                badge.innerText = (priority || "Active").toUpperCase();
                badge.className = (priority && priority.toLowerCase() === 'high') ? "badge bg-danger" : "badge bg-primary";
            }
        }
    });

    var searchOrder = document.getElementById("searchOrder");
    if (searchOrder) {
        searchOrder.addEventListener("input", function() {
            var search = this.value.trim().toLowerCase();
            var rows = document.querySelectorAll("#ordersTableBody tr");
            rows.forEach(function(row) {
                row.style.display = row.innerText.toLowerCase().includes(search) ? "" : "none";
            });
        });
    }

    updateFabric();
    calculateTotal();

    var orderValue = document.getElementById("order_value");
    var summaryOrderNo = document.getElementById("summaryOrderNo");
    if (orderValue && summaryOrderNo) {
        orderValue.addEventListener("input", function() {
            summaryOrderNo.textContent = this.value;
        });
    }

    var quantity1 = document.getElementById("quantity1");
    var summaryWeight = document.getElementById("summaryWeight");
    if (quantity1 && summaryWeight) {
        quantity1.addEventListener("input", function() {
            summaryWeight.textContent = (Number(this.value) || 0).toLocaleString() + " Kg";
            calculateTotal();
        });
    }

    var fabricSelect = document.querySelector('[name="fabric_type"]');
    var gsmInput = document.querySelector('[name="gsm"]');
    if (fabricSelect) fabricSelect.addEventListener("change", updateFabric);
    if (gsmInput) gsmInput.addEventListener("input", updateFabric);

    var price = document.getElementById("price");
    if (price) price.addEventListener("input", calculateTotal);

    var orderForm = document.getElementById("orderForm");
    if (orderForm) {
        orderForm.addEventListener("submit", function(e) {
            var submitBtn = this.querySelector('button[type="submit"]') || this.querySelector('.btn-secondary');
            if (submitBtn) {
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Saving...';
                submitBtn.disabled = true;
            }
        });
    }
});

function loadOrdersAndKPIs() {
    console.log("Loading orders and KPIs at:", new Date().toLocaleTimeString());

    const ordersTableBody = document.getElementById("ordersTableBody");
    const urlParams = new URLSearchParams(window.location.search);
    const currentUserId = urlParams.get('user_id') || ''; // Defined here

    if (!ordersTableBody) {
        console.error(" ordersTableBody not found");
        return;
    }

    const timestamp = new Date().getTime();

    // FIXED: Used currentUserId and fixed parenthesis syntax in fetch()
    fetch(`../py/orders/get_orders.py?t=${timestamp}&user_id=${currentUserId}`, {
        headers: {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("Data received successfully");

        if (data.status === "success") {
            if (document.getElementById("kpiTotalOrders"))
                document.getElementById("kpiTotalOrders").innerText = data.kpis.total;
            if (document.getElementById("kpiRunningOrders"))
                document.getElementById("kpiRunningOrders").innerText = data.kpis.running;
            if (document.getElementById("kpiCompletedOrders"))
                document.getElementById("kpiCompletedOrders").innerText = data.kpis.completed;
            if (document.getElementById("kpiPendingOrders"))
                document.getElementById("kpiPendingOrders").innerText = data.kpis.pending;

            ordersTableBody.innerHTML = data.rows_html;

            console.log(" Orders and KPIs updated successfully");
        } else {
            ordersTableBody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-danger text-center">
                         ${data.message || 'Failed to load data'}
                    </td>
                </tr>
            `;
        }
    })
    .catch(err => {
        console.error("Error:", err);
        ordersTableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-danger text-center">
                     Error connecting to server
                </td>
            </tr>
        `;
    });
}

document.addEventListener("DOMContentLoaded", function() {
    console.log(" Page loaded");
    loadOrdersAndKPIs();

    setInterval(loadOrdersAndKPIs, 30000);
});

window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        console.log("Page from cache - refreshing");
        loadOrdersAndKPIs();
    }
});

document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        console.log("Tab visible - refreshing");
        loadOrdersAndKPIs();
    }
});

console.log(" Script loaded successfully");

//THIS FUNCTION UPDATES THE BALANCE IN THE ENQUIRY FORM
function updateBalanceFromTotal() {
    // Read total text, remove '₹' and commas, convert to number
    let totalText = document.getElementById('totalAmounts').innerText;
    let totalValue = parseFloat(totalText.replace(/[^0-9.-]+/g, "")) || 0;

    // Calculate 50%
    let balanceValue = totalValue * 0.50;

    // Update the balance element
    document.getElementById('balanceAmount').innerText = '₹' + balanceValue.toLocaleString('en-IN');
}

//THIS FUNCTION HANDLE ORDER VIEW MODAL
function populateModalDetails(btn) {
    document.getElementById('modalOrderNumber').innerText = btn.getAttribute('data-order') || '--';
    document.getElementById('modalCustomerName1').innerText = btn.getAttribute('data-customer') || '--';
    document.getElementById('modalFabric1').innerText = btn.getAttribute('data-fabric') || '--';
    document.getElementById('modalColor1').innerText = btn.getAttribute('data-color') || '--';
    document.getElementById('modalQuantity').innerText = btn.getAttribute('data-qty') || '--';
    document.getElementById('modalPricePerKg').innerText = "₹" + (btn.getAttribute('data-price') || '0');
    document.getElementById('modalTotalAmount').innerText = "₹" + (btn.getAttribute('data-total') || '0');
    document.getElementById('modalOrderDate').innerText = btn.getAttribute('data-orderdate') || '--';
    document.getElementById('modalDeliveryDate').innerText = btn.getAttribute('data-deliverydate') || '--';
    document.getElementById('modalCreatedBy').innerText = btn.getAttribute('data-createdby') || '--';
    document.getElementById('modalRemarks1').innerText = btn.getAttribute('data-remarks') || 'No remarks provided.';

    const statusVal = btn.getAttribute('data-status') || 'New Order';
    const badgeEl = document.getElementById('modalStatusBadge1');
    badgeEl.innerText = statusVal;

    if (statusVal.toLowerCase() === 'new order') {
        badgeEl.className = 'badge bg-secondary';
    } else if (statusVal.toLowerCase() === 'running') {
        badgeEl.className = 'badge bg-info text-dark';
    } else if (statusVal.toLowerCase() === 'completed') {
        badgeEl.className = 'badge bg-success';
    } else {
        badgeEl.className = 'badge bg-primary';
    }
}

// THIS FUNCTION HANDLES PRODUCTION PLAN FILTER
document.addEventListener("DOMContentLoaded", function () {
    const statusSelect = document.querySelector(".filter-select");
    const tableBody = document.getElementById("ordersTableBody");

    if (statusSelect && tableBody) {
        statusSelect.addEventListener("change", function () {
            const selectedFilter = this.value.trim().toLowerCase();

            // Loop through each table row
            const rows = tableBody.querySelectorAll("tr");

            rows.forEach(row => {
                // Find the Status column badge inside the row (7th column)
                const statusBadge = row.querySelector("td:nth-child(6) .badge");

                if (statusBadge) {
                    const rowStatus = statusBadge.textContent.trim().toLowerCase();

                    // Show all rows if "All Status" selected, or match selected option
                    if (selectedFilter === "all status" || rowStatus === selectedFilter) {
                        row.style.display = "";
                    } else {
                        row.style.display = "none";
                    }
                }
            });
        });
    }
});

// THIS FUNCTION HANDLES ORDER DELETION
function deleteOrder(orderNo) {
    if (confirm("Are you sure you want to delete this order?")) {
        var formData = new FormData();
        formData.append('order_number', orderNo);

        fetch('../py//orders/delete_order.py', {
            method: 'POST',
            body: formData
        })
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            if (data.status === 'success') {
                alert(data.message);
                location.reload(); // Reload table
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(function(error) {
            alert('Error deleting order.');
        });
    }
}

/* ==========================================================================
   05. CREATE ORDER SCREEN
   ========================================================================== */

function loadOrderDropdown() {
    console.log("Attempting to fetch dropdown...");

    // Get user_id from the current browser URL (e.g. Marketing.html?user_id=EMP001#Enquiry)
    const urlParams = new URLSearchParams(window.location.search);
    const userId = urlParams.get('user_id') || '';

    // Pass the userId parameter in the fetch request
    fetch(`../py/orders/get_customer_dropdown.py?user_id=${encodeURIComponent(userId)}`)
        .then(res => res.text())
        .then(html => {
            const select = document.getElementById("customerSelect");
            if (select) {
                select.innerHTML = html;
                console.log("Dropdown HTML injected successfully for user:", userId);
            } else {
                console.error("CRITICAL: Cannot find element 'customerSelect'");
            }
        })
        .catch(err => console.error("Fetch Dropdown Error:", err));
}

function fillOrderForm(enqId) {
    if (!enqId) return;
    console.log("Fetching details for:", enqId);

    fetch('../py/orders/get_quoted_customer.py?enquiry_id=' + enqId)
        .then(res => res.text())
        .then(dataString => {
            console.log("SERVER RETURNED:", dataString);

            const p = dataString.split('|');
            if (p.length < 5) {
                console.error("Invalid Data String format");
                return;
            }

            const contact = document.getElementById("customerContact");
            if (contact) contact.value = p[0];

            const color = document.getElementById("colorInput");
            if (color) color.value = p[3];

            const qty = document.getElementById("quantity1");
            if (qty) qty.value = p[4];

            const price = document.getElementById("price");
            if (price) price.value = p[5];

            const subtotal = parseFloat(p[4]) * parseFloat(p[5]);
            const gst = subtotal * 0.18;
            const totalAmount = subtotal + gst;

            const perc = document.getElementById("percentage");
            if (perc) perc.value = p[6];

            const total = document.getElementById("totalAmounts");
            if (total) total.innerText = "₹" + totalAmount.toFixed(2);

            updateBalanceFromTotal();

            const hiddenId = document.getElementById("customerId");
            if (hiddenId) hiddenId.value = p[10];

            const fabric = document.getElementsByName("fabric_type")[0];
            if (fabric) fabric.value = p[1];

            const odate = document.getElementsByName("order_date")[0];
            if (odate) odate.value = p[8];

            const ddate = document.getElementsByName("delivery_date")[0];
            if (ddate) ddate.value = p[9];

            console.log("Form Fill Complete.");
        })
        .catch(err => console.error("Form Fill Error:", err));
}

document.addEventListener("DOMContentLoaded", function() {
    const select = document.getElementById("customerSelect");

    if (select) {
        select.addEventListener('focus', function() {
            console.log("User clicked dropdown - fetching fresh data...");
            loadOrderDropdown();
        });

        select.addEventListener('change', function() {
            fillOrderForm(this.value);
        });
    }

    loadOrderDropdown();
});


document.addEventListener("DOMContentLoaded", function() {
    const deliveryDateInput = document.getElementsByName("delivery_date")[0];
    if (!deliveryDateInput) return;

    function validateDates() {
        if (deliveryDateInput.value) {
           const today = new Date();
           const minDate = new Date(today);
           minDate.setDate(today.getDate() + 1);
           deliveryDateInput.min = minDate.toISOString().split('T')[0];
        }
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

//date disable with picker dynamic today date
document.addEventListener("DOMContentLoaded", function () {
    // Get the date input element by its ID
    const dateInput = document.getElementById("delivery_date");

    if (dateInput) {
        // Get today's local date
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed
        const day = String(today.getDate()).padStart(2, '0');

        // Format as YYYY-MM-DD
        const minDate = `${year}-${month}-${day}`;

        // Set the 'min' attribute dynamically to disable all past dates
        dateInput.setAttribute("min", minDate);
    }
});


/* ==========================================================================
   06. CUSTOMER ENQUIRIES SCREEN
   ========================================================================== */

// Function to extract user_id from URL (e.g. ?user_id=EMP001)
function getUserIdFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('user_id') || '';
}

// 1. Fetch KPI & Table Data (Role filtered by user_id in URL)
function fetchEnquiryData() {
    console.log('Fetching enquiry data...');
    const userId = getUserIdFromURL();

    fetch(`../py/enquiry/load_enquiry.py?user_id=${encodeURIComponent(userId)}&t=${new Date().getTime()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                if (document.getElementById('totalEnquiries')) {
                    document.getElementById('totalEnquiries').textContent = data.kpis.total_enquiries;
                }
                if (document.getElementById('pendingEnquiries')) {
                    document.getElementById('pendingEnquiries').textContent = data.kpis.pending_enquiries;
                }
                if (document.getElementById('followupRequired')) {
                    document.getElementById('followupRequired').textContent = data.kpis.followup_required;
                }
                if (document.getElementById('convertedOrders')) {
                    document.getElementById('convertedOrders').textContent = data.kpis.converted_orders;
                }

                const tableBody = document.getElementById('enquiryTableBody') || document.getElementById('customerTableBody');
                if (tableBody) {
                    tableBody.innerHTML = data.rows_html;
                }
            } else {
                console.error('API returned error:', data.message);
            }
        })
        .catch(error => {
            console.error('Error fetching enquiry data:', error);
        });
}

// 2. Single Event Listener for "Send Sample" & "Send Quotation" Actions
document.addEventListener("DOMContentLoaded", function () {
    const tableBody = document.getElementById("enquiryTableBody") || document.getElementById("customerTableBody");

    if (tableBody) {
        tableBody.addEventListener("click", function (event) {
            const btn = event.target.closest(".action-sample-btn");
            if (!btn) return;

            const dbId = btn.getAttribute("data-id");               // Database Numeric ID (1, 2, 3...)
            const enquiryId = btn.getAttribute("data-enquiry-id");   // Enquiry String ID (ENQ001, ENQ002...)
            const currentStatus = btn.getAttribute("data-current-status");

            // ACTION 1: Send Sample (Status 0 -> Status 1)
            if (currentStatus === "0") {
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Processing...';

                fetch(`../py/enquiry/update_sample.py?id=${encodeURIComponent(dbId)}&enquiry_id=${encodeURIComponent(enquiryId)}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === "success") {
                            alert("Sample status updated to 'Sample Sent'!");
                            fetchEnquiryData(); // Refresh UI
                        } else {
                            alert("Error: " + data.message);
                            btn.disabled = false;
                            btn.innerHTML = "Send Sample";
                        }
                    })
                    .catch(err => {
                        console.error(err);
                        alert("Error updating sample status.");
                        btn.disabled = false;
                        btn.innerHTML = "Send Sample";
                    });
            }
            // ACTION 2: Send Quotation Email (Status 1 -> Status 2)
            else if (currentStatus === "1") {
                if (confirm(`Send official quotation email for ${enquiryId}?`)) {
                    btn.disabled = true;
                    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Sending Email...';

                    fetch(`../py/enquiry/send_quotation.py?enquiry_id=${encodeURIComponent(enquiryId)}&id=${encodeURIComponent(dbId)}`)
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === "success") {
                                alert("Quotation Sent Successfully to " + data.email);
                                fetchEnquiryData(); // Refresh UI
                            } else {
                                alert("Error: " + data.message);
                                btn.disabled = false;
                                btn.innerHTML = "Send Quotation";
                            }
                        })
                        .catch(err => {
                            console.error(err);
                            alert("Failed to send quotation email.");
                            btn.disabled = false;
                            btn.innerHTML = "Send Quotation";
                        });
                }
            }
        });
    }

    // Initialize Search Filter
    const searchEnquiry = document.getElementById('searchEnquiry');
    const enquiryRefresh = document.getElementById('enquiryRefresh');

    if (searchEnquiry && tableBody) {
        searchEnquiry.addEventListener('input', function () {
            const query = searchEnquiry.value.toLowerCase().trim();
            const rows = tableBody.getElementsByTagName('tr');

            Array.from(rows).forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        });
    }

    if (enquiryRefresh && searchEnquiry && tableBody) {
        enquiryRefresh.addEventListener('click', function () {
            searchEnquiry.value = '';
            fetchEnquiryData();
        });
    }

    // Load Initial Data and start auto-refresh
    fetchEnquiryData();
    setInterval(fetchEnquiryData, 5000);
});

window.addEventListener("focus", function () {
    fetchEnquiryData();
});

//THIS FUNCTION IS USED FOR FILTERING ENQUIRIES BY STATUS
function filterEnquiriesByStatus() {
    // 1. Get selected value from filter dropdown
    const filterSelect = document.getElementById("statusFilter");
    const selectedStatus = filterSelect.value.trim();

    // 2. Get the enquiry table body and all its rows
    const tableBody = document.getElementById("enquiryTableBody");
    const rows = tableBody.getElementsByTagName("tr");

    // 3. Loop through each row in the table
    for (let i = 0; i < rows.length; i++) {
        const row = rows[i];

        // Skip empty or error message rows (which have only 1 cell spanning across)
        if (row.cells.length < 6) continue;

        // Extract text from the 6th column (Index 5 = Status)
        const statusCellText = row.cells[5].textContent.trim();

        // 4. Compare: If ALL is selected or Status matches cell text, show row; otherwise hide it
        if (selectedStatus === "ALL" || statusCellText.includes(selectedStatus)) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    }
}


// THIS CODE IS USED FOR OPEN EDIT ENQUIRY MODAL
  document.addEventListener('click', function (e) {
    var editBtn = e.target.closest('.edit-btn');
    if (editBtn) {
      var id = editBtn.getAttribute('data-id');
      var name = editBtn.getAttribute('data-name');
      var phone = editBtn.getAttribute('data-phone');
      var email = editBtn.getAttribute('data-email');
      var quantity = editBtn.getAttribute('data-quantity');

      document.getElementById('edit_db_id').value = id;
      document.getElementById('edit_customer_name').value = name;
      document.getElementById('edit_phone').value = phone;
      document.getElementById('edit_email').value = email;
      document.getElementById('edit_quantity').value = quantity;

      var modalElement = document.getElementById('editEnquiryModal');
      var modalInstance = new bootstrap.Modal(modalElement);
      modalInstance.show();
    }
  });

  // THIS FUNCTION IS USED FOR UPDATING ENQUIRIES
  document.getElementById('editEnquiryForm').addEventListener('submit', function (e) {
    e.preventDefault();

    fetch('../py/enquiry/update_enquiry.py', {
      method: 'POST',
      body: new FormData(this)
    })
    .then(function (response) {
      return response.json();
    })
    .then(function (data) {
      if (data.status === 'success') {
        alert(data.message);
        var modalElement = document.getElementById('editEnquiryModal');
        var modalInstance = bootstrap.Modal.getInstance(modalElement);
        if (modalInstance) {
          modalInstance.hide();
        }
        location.reload();
      } else {
        alert('Error: ' + data.message);
      }
    })
    .catch(function (error) {
      alert('Error updating data.');
    });
  });

  // THIS FUNCTION IS USED FOR DELETING ENQUIRIES
  function deleteCustomer(dbId) {
    var confirmDelete = confirm("Are you sure you want to delete this enquiry?");
    if (confirmDelete) {

      var formData = new FormData();
      formData.append('db_id', dbId);

      fetch('../py/enquiry/delete_enquiry.py', {
        method: 'POST',
        body: formData
      })
      .then(function (response) {
        return response.json();
      })
      .then(function (data) {
        if (data.status === 'success') {
          alert(data.message);
          location.reload();
        } else {
          alert('Error: ' + data.message);
        }
      })
      .catch(function (error) {
        alert('Error deleting data.');
      });
    }
  }
/* ==========================================================================
   07. CREATE ENQUIRY SCREEN
   ========================================================================== */



// THIS FUNCTION LOADS DYNAMIC FABRIC DROPDOWNS
function loadFabricType() {
    const container = document.getElementById("dynamicDropdowns");
    if (!container) return;

    // Adding ?t= prevents browser caching
    fetch("../py/enquiry/enquiry_form.py?t=" + new Date().getTime())
        .then(response => response.text())
        .then(data => {
            container.innerHTML = data;
        })
        .catch(error => console.error('Error loading fabric type:', error));
}

// Auto-refresh when switching back to this window/screen
window.addEventListener("focus", function () {
    loadFabricType();
});

// THIS FUNCTION SAVES ENQUIRY FORM
function saveEnquiry(event) {
    if (event) event.preventDefault();

    const form = document.getElementById("enquiryForm");
    if (!form) return;

    const requiredInputs = form.querySelectorAll("[required]");
    for (let input of requiredInputs) {
        if (!input.value || !input.value.trim()) {
            const parentDiv = input.closest('div');
            const labelElem = parentDiv ? parentDiv.querySelector('label') : null;
            const labelText = labelElem ? labelElem.innerText.trim() : (input.placeholder || input.name || "Field");

            input.focus();
            alert(`Please fill out the required field: ${labelText}`);
            return;
        }
    }

    if (!form.checkValidity()) {
        const invalidInput = form.querySelector(":invalid");
        if (invalidInput) {
            invalidInput.focus();
            const parentDiv = invalidInput.closest('div');
            const labelElem = parentDiv ? parentDiv.querySelector('label') : null;
            const labelText = labelElem ? labelElem.innerText.trim() : invalidInput.name;

            alert(invalidInput.title || `Invalid value in field: ${labelText}`);
            return;
        }
    }

    const hiddenField = document.getElementById("session_admin_id");
    const urlParams = new URLSearchParams(window.location.search);
    const userId = (hiddenField ? hiddenField.value : "") || urlParams.get("user_id") || urlParams.get("admin_id");

    if (!userId || !userId.trim()) {
        alert("Session Error: User ID was not found in form or URL.\nPlease log in again.");
        window.location.href = "/techvoltInstituteProject/pages/login.html";
        return;
    }

    const cleanUserId = userId.trim();

    let formData = new FormData(form);
    formData.set("admin_id", cleanUserId);
    formData.set("user_id", cleanUserId);

    const currentPage = window.location.pathname.split('/').pop() || "Marketing.html";
    formData.set("current_page", currentPage);

    fetch("../py/enquiry/save_enquiry.py", {
        method: "POST",
        body: formData
    })
    .then(async res => {
        const text = await res.text();
        try {
            return JSON.parse(text);
        } catch (e) {
            console.error("Non-JSON Server Output:", text);
            throw new Error("Python Server Crash / Invalid JSON output:\n\n" + text.slice(0, 300));
        }
    })
    .then(data => {
        if (data.success) {
            alert(data.message);
            form.reset();

            if (hiddenField) hiddenField.value = cleanUserId;

            if (data.redirect) {
                window.location.href = data.redirect;
            } else {
                window.location.href = `${currentPage}?user_id=${encodeURIComponent(cleanUserId)}`;
            }
        } else {
            alert("Validation Error from Server:\n\n" + data.message);
        }
    })
    .catch(error => {
        console.error("Fetch Exception:", error);
        alert(error.message || "Server Error or invalid response from backend.");
    });
}

// THIS FUNCTION LOADS DYNAMIC COLOR DROPDOWNS
function fetchColors(selectElement) {
    const colorSelect = document.getElementById('color1');
    const fabricNameInput = document.getElementById('fabric_type_name');

    if (!colorSelect || !fabricNameInput) return;

    colorSelect.innerHTML = '<option value="">Select Color</option>';
    fabricNameInput.value = '';

    const selectedOption = selectElement.options[selectElement.selectedIndex];
    const fabricId = selectElement.value;
    const fabricName = selectedOption.getAttribute('data-name');

    if (!fabricId) return;

    fabricNameInput.value = fabricName;

    fetch(`../py/enquiry/enquiry_form.py?fabric_id=${fabricId}`)
        .then(response => response.json())
        .then(colors => {
            colors.forEach(color => {
                const option = document.createElement('option');
                option.value = color;
                option.textContent = color;
                colorSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error fetching colors:', error));
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