/* ==========================================================================
   PRODUCTION EXECUTIVE DASHBOARD JS
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

// Nav Item Click Feedback
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function(e) {
        e.preventDefault();
        document.querySelectorAll('.nav-item').forEach(nav => {
            nav.classList.remove('active');
        });
        this.classList.add('active');
    });
});

// Button Scale Effect
document.querySelectorAll('button, a').forEach(el => {
    el.addEventListener('mousedown', function() {
        this.classList.add('scale-95');
    });
    el.addEventListener('mouseup', function() {
        this.classList.remove('scale-95');
    });
    el.addEventListener('mouseleave', function() {
        this.classList.remove('scale-95');
    });
});

// Pagination Active State
document.querySelectorAll('.pagination-custom .page-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        if (!this.textContent.includes('Prev') && !this.textContent.includes('Next')) {
            document.querySelectorAll('.pagination-custom .page-btn').forEach(b => {
                b.classList.remove('active');
            });
            this.classList.add('active');
        }
    });
});


/* ==========================================================================
   02. PRODUCTION DASHBOARD MAIN SCREEN (DASHBOARD)
   ========================================================================== */

async function fetchDashboardData() {
    try {
        const response = await fetch('../py/dashboard/get_productiondashboard.py?action=get_dashboard_data');
        const result = await response.json();

        if (result.success) {
            const data = result.data;

            document.getElementById('todayProduction').textContent = data.today_production;
            document.getElementById('productionTarget').textContent = data.production_target;
            document.getElementById('runningOrders').textContent = data.running_orders;
            document.getElementById('pendingProduction').textContent = data.pending_production;

            document.getElementById('targetValue').textContent = data.target_value + ' Kg';
            document.getElementById('producedValue').textContent = data.produced_value + ' Kg';
            document.getElementById('pendingValue').textContent = data.pending_value + ' Kg';
            document.getElementById('completionPercentage').textContent = data.completion_percentage + '%';

            updateCircularProgress(data.completion_percentage);

            console.log('Dashboard data updated successfully:', data);
        } else {
            console.error('Error from server:', result.error);
        }
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
    }
}

function updateCircularProgress(percentage) {
    const circle = document.getElementById('progressCircle');
    if (circle) {
        const circumference = 440;
        const offset = circumference - (percentage / 100) * circumference;
        circle.style.strokeDashoffset = offset;

        if (percentage < 30) {
            circle.style.stroke = '#dc3545';
        } else if (percentage < 70) {
            circle.style.stroke = '#ffc107';
        } else {
            circle.style.stroke = '#006a61';
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    fetchDashboardData();
    setInterval(fetchDashboardData, 30000);
});


/* ==========================================================================
   03. PRODUCTION PLANNING SCREEN (PAGE 7)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {

    function showproductionToast() {
        const toast = document.getElementById('successProductionPlan');
        if (toast) {
            toast.classList.remove('hidden');
            clearTimeout(window.toastTimeout);
            window.toastTimeout = setTimeout(() => {
                hideproductionToast();
            }, 5000);
        }
    }

    function hideproductionToast() {
        const toast = document.getElementById('successProductionPlan');
        if (toast) {
            toast.classList.add('hidden');
        }
    }

    function handleproductionSubmit(e) {
        e.preventDefault();
        showproductionToast();
    }
// Load production plans IN TABLE
    fetch("../py/inventory/get_production_plan.py")
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error("Backend Error:", data.error);
            return;
        }

        if (document.getElementById("totalPlans"))
            document.getElementById("totalPlans").textContent = data.total_plan;

        if (document.getElementById("runningPlans"))
            document.getElementById("runningPlans").textContent = data.running_plan;

        if (document.getElementById("completedPlans"))
            document.getElementById("completedPlans").textContent = data.completed_plan;

        if (document.getElementById("pendingPlans"))
            document.getElementById("pendingPlans").textContent = data.pending_plan;

        const tableBody = document.getElementById("productionPlanTable");
        if (tableBody) {
            tableBody.innerHTML = data.table_html;
        }
    })
    .catch(error => console.error("Error loading production plans:", error));

    const materialName = document.getElementById("materialName");
    const unitCost = document.getElementById("unitCost");
    const category = document.querySelector('[name="category"]');
    const openingStock = document.querySelector('[name="opening_stock"]');
    const unit = document.querySelector('[name="unit"]');
    const locationField = document.querySelector('[name="location"]');
    const statusRadio = document.querySelectorAll('[name="status"]');

    const previewName = document.getElementById("previewMaterialName");
    const previewCategory = document.getElementById("previewCategory");
    const previewStock = document.getElementById("previewStock");
    const previewValue = document.getElementById("previewValue");
    const previewLocation = document.getElementById("previewLocation");
    const previewStatus = document.getElementById("previewStatu");

    function updatePreview() {
        if (previewName && materialName) {
            previewName.textContent = materialName.value || "-";
        }

        if (previewCategory && category) {
            previewCategory.textContent = category.value;
        }

        if (previewStock && openingStock && unit) {
            const stock = Number(openingStock.value) || 0;
            previewStock.textContent = stock.toLocaleString('en-IN') + " " + unit.value;
        }

        if (previewValue && unitCost && openingStock) {
            const cost = Number(unitCost.value) || 0;
            const stock = Number(openingStock.value) || 0;
            const total = stock * cost;
            previewValue.textContent = "₹" + total.toLocaleString('en-IN');
        }

        if (previewLocation && locationField) {
            previewLocation.textContent = locationField.value || "-";
        }

        if (previewStatus) {
            const selectedStatus = document.querySelector('[name="status"]:checked');
            if (selectedStatus) {
                previewStatus.innerHTML = `
                    <span class="status-dot"></span>
                    ${selectedStatus.value}
                `;
            }
        }
    }

    if (materialName) materialName.addEventListener("input", updatePreview);
    if (category) category.addEventListener("change", updatePreview);
    if (openingStock) openingStock.addEventListener("input", updatePreview);
    if (unit) unit.addEventListener("change", updatePreview);
    if (unitCost) unitCost.addEventListener("input", updatePreview);
    if (locationField) locationField.addEventListener("input", updatePreview);

    if (statusRadio) {
        statusRadio.forEach(radio => {
            radio.addEventListener("change", updatePreview);
        });
    }

    updatePreview();

    const table = document.getElementById("productionPlanTable");
    if (table) {
        table.addEventListener("click", function(e) {
            const row = e.target.closest("tr");
            if (!row) return;

            table.querySelectorAll("tr").forEach(r => r.classList.remove("selected"));
            row.classList.add("selected");

            const cells = row.cells;
            if (cells.length >= 5) {
                const plan = cells[0].innerText.trim() || "N/A";
                const order = cells[1].innerText.trim() || "N/A";
                const machine = cells[2].innerText.trim() || "N/A";
                const windowText = cells[3].innerText.replace(/\n/g, " ").trim() || "N/A";
                const priority = cells[4].innerText.trim() || "N/A";

                const detailPlan = document.getElementById("detailPlan");
                const detailPriority = document.getElementById("detailPriority");
                const detailOrder = document.getElementById("detailOrder");
                const detailMachine = document.getElementById("detailMachine");
                const detailWindow = document.getElementById("detailWindow");

                if (detailPlan) detailPlan.textContent = "Active Plan: " + plan;
                if (detailPriority) detailPriority.textContent = "Priority: " + priority;
                if (detailOrder) detailOrder.textContent = order;
                if (detailMachine) detailMachine.textContent = machine;
                if (detailWindow) detailWindow.textContent = windowText;
            }
        });
    }

    const searchInput = document.getElementById("SearchPp");
    if (searchInput) {
        searchInput.addEventListener("keyup", function() {
            let search = this.value.toLowerCase();

            const tableRows = document.querySelectorAll("#productionPlanTable tr");
            if (tableRows) {
                tableRows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(search) ? "" : "none";
                });
            }
        });
    }

    window.showproductionToast = showproductionToast;
    window.hideproductionToast = hideproductionToast;
    window.handleproductionSubmit = handleproductionSubmit;

});


/* ==========================================================================
   04. CREATE PRODUCTION PLAN SCREEN
   ========================================================================== */

// THIS FUNCTION LOADS ORDER LIST
function loadOrders() {
    fetch("../py/production/get_order_list.py")
        .then(res => res.text())
        .then(data => {
            const orderSelect = document.getElementById("orderSelect");
            if (orderSelect) {
                orderSelect.innerHTML = data;
            }
        })
        .catch(error => console.error('Error loading orders:', error));
}

document.addEventListener("DOMContentLoaded", function() {
    loadOrders();
    setInterval(loadOrders, 30000);
});

// THIS FUNCTION LOADS ORDER DETAILS AFTER USER SELECTS AN ORDER
const orderSelectElem = document.getElementById("orderSelect");
if (orderSelectElem) {
    orderSelectElem.addEventListener("change", function() {
        const orderValue = this.value;
        if (!orderValue) return;

        fetch("../py/production/get_order_details.py?order=" + orderValue)
            .then(res => res.json())
            .then(data => {
                const customer = document.getElementById("customer");
                const fabric = document.getElementById("fabric");
                const orderQty = document.getElementById("orderQty");

                if (customer) customer.value = data.customer || "";
                if (fabric) fabric.value = data.fabric || "";
                if (orderQty) orderQty.value = (data.quantity || 0) + " Kg";
            })
            .catch(error => console.error('Error loading order details:', error));
    });
}

// THIS FUNCTION LOADS MACHINE AND SUPERVISOR DROPDOWNS
function loadMachineAndSupervisorDropdowns() {
    const machineSelect = document.getElementById("machine1");
    const supervisorSelect = document.getElementById("supervisor");

    // Only run if the dropdown elements exist on the screen
    if (machineSelect && supervisorSelect) {

        // Replace with your exact Python file path (e.g., ../py/inventory/get_machines_supervisors.py)
        fetch("../py/production/get_production_dropdown.py?t=" + new Date().getTime())
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    // Populate Machine Dropdown
                    if (data.machine_options) {
                        machineSelect.innerHTML = data.machine_options;
                    }

                    // Populate Supervisor Dropdown
                    if (data.supervisor_options) {
                        supervisorSelect.innerHTML = data.supervisor_options;
                    }
                } else {
                    console.error("Backend Error:", data.message);
                }
            })
            .catch(error => console.error("Error loading dropdowns:", error));
    }
}

// Automatically load dropdowns on page load & tab focus
document.addEventListener("DOMContentLoaded", function () {
    loadMachineAndSupervisorDropdowns();
});

window.addEventListener("focus", function () {
    loadMachineAndSupervisorDropdowns();
});

// THIS FUNCTION HANDLES FORM SUBMISSION
document.addEventListener("DOMContentLoaded", function () {
    const planForm = document.getElementById("planForm");

    if (planForm) {
        planForm.addEventListener("submit", function (e) {
            // 1. PREVENT the browser from opening the raw JSON page
            e.preventDefault();

            const formData = new FormData(this);

            // 2. Send form data in the background
            fetch(this.action, {
                method: "POST",
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "error") {
                    // 3. SHOW REAL ALERT POPUP (User stays on the form page)
                    alert("Validation Errors:\n- " + data.errors.join("\n- "));
                } else if (data.status === "success") {
                    // 4. SHOW SUCCESS ALERT & REDIRECT
                    alert(data.message);
                    window.location.href = data.redirect_url;
                }
            })
            .catch(error => {
                console.error("Error submitting form:", error);
                alert("An error occurred while saving the plan.");
            });
        });
    }
});

/* ==========================================================================
   05. MACHINE ALLOCATION SCREEN
   ========================================================================== */

document.querySelectorAll('.view-toggle .view-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.view-toggle .view-btn').forEach(b => {
            b.classList.remove('active');
        });
        this.classList.add('active');
    });
});

document.querySelectorAll('.filter-chip').forEach(chip => {
    chip.addEventListener('click', function() {
        document.querySelectorAll('.filter-chip').forEach(c => {
            c.style.background = '#ffffff';
            c.style.color = '#45464d';
        });
        this.style.background = '#86f2e4';
        this.style.color = '#006f66';
    });
});

setInterval(() => {
    document.querySelectorAll('.telemetry-chart .bar').forEach(bar => {
        const randomHeight = Math.floor(Math.random() * (95 - 60 + 1)) + 60;
        bar.style.height = randomHeight + '%';
    });
}, 2000);

function loadAllAllocations() {
    console.log('🔄 Loading all allocations...');
    fetch('../py/machine/machine_allocation.py?action=get_all_allocations')
        .then(response => {
            console.log('📡 Allocations Response status:', response.status);
            if (!response.ok) {
                throw new Error('HTTP error! status: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log('📊 All Allocations Data:', data);

            const tbody = document.getElementById('allocations_table_body1');
            if (!tbody) {
                console.warn('⚠️ Table body with id "allocations_table_body" not found!');
                return;
            }

            if (data.error) {
                console.error('❌ Error:', data.error);
                tbody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">${data.error}</td></tr>`;
                return;
            }

            if (!Array.isArray(data) || data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">No allocations found</td></tr>`;
                console.log('ℹ️ No allocations found');
                return;
            }

            let html = '';
            data.forEach((item) => {
                const statusClass = (item.status || 'assigned').toLowerCase();
                let badgeClass = 'running';
                let dotClass = 'running';
                let avatarClass = 'bg-teal';

                if (statusClass === 'maintenance') {
                    badgeClass = 'maintenance';
                    dotClass = 'maintenance';
                    avatarClass = 'bg-red';
                } else if (statusClass === 'idle') {
                    badgeClass = 'idle';
                    dotClass = 'idle';
                    avatarClass = 'bg-gray';
                } else if (statusClass === 'assigned') {
                    badgeClass = 'assigned';
                    dotClass = 'assigned';
                    avatarClass = 'bg-primary';
                }

                const firstLetter = item.operator_name && item.operator_name !== '-' ?
                                   item.operator_name.charAt(0).toUpperCase() : '?';

                const statusDisplay = item.status ? item.status.toUpperCase() : 'ASSIGNED';
                const orderNo = item.order_no || '-';

                html += `
                    <tr data-machine="${item.machine_name}"
                        data-order="${orderNo}"
                        data-operator="${item.operator_name}"
                        data-status="${item.status}">
                        <td><span class="machine-name">${item.machine_name}</span></td>
                        <td>${orderNo}</td>
                        <td>
                            <div class="d-flex align-items-center gap-2">
                                <div class="operator-avatar ${avatarClass}">${firstLetter}</div>
                                <span>${item.operator_name}</span>
                            </div>
                        </td>
                        <td>
                            <span class="status-badge ${badgeClass}">
                                <span class="status-dot ${dotClass}"></span>
                                ${statusDisplay}
                            </span>
                        </td>
                        <td class="text-right">
                            <div class="d-flex justify-content-end gap-1">
                                <button class="table-action-btn" onclick="viewAllocation('${item.allocation_no}')">
                                    <i class="bi bi-gear"></i>
                                </button>
                                <button class="table-action-btn" onclick="editAllocation('${item.allocation_no}')">
                                    <i class="bi bi-arrow-repeat"></i>
                                </button>
                                <button class="table-action-btn" onclick="viewAllocation('${item.allocation_no}')">
                                    <i class="bi bi-eye"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            });
            tbody.innerHTML = html;
            console.log(`✅ Loaded ${data.length} allocations`);

            attachRowClickHandlers();
        })
        .catch(error => {
            console.error('❌ Error loading allocations:', error);
            const tbody = document.getElementById('allocations_table_body1');
            if (tbody) {
                tbody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Error loading allocations</td></tr>`;
            }
        });
}

function loadMachineKPI() {
    fetch('../py/machine/machine_allocation.py?action=machine_kpi')
        .then(response => response.json())
        .then(data => {
            if (data && !data.error) {
                document.getElementById('kpi_total').innerText = data.total_machines;
                document.getElementById('kpi_running1').innerText = data.running;
                document.getElementById('kpi_assigned').innerText = data.assigned;
                document.getElementById('kpi_maintenance1').innerText = data.maintenance;
            }
        })
        .catch(error => console.error("Error:", error));
}

loadMachineKPI();

function attachRowClickHandlers() {
    document.querySelectorAll('.table-custom tbody tr').forEach(row => {
        row.removeEventListener('click', rowClickHandler);
        row.addEventListener('click', rowClickHandler);
    });
}

function rowClickHandler() {
    const machine = this.dataset.machine || 'Machine A';
    const order = this.dataset.order || '-';
    const operator = this.dataset.operator || '-';
    const status = this.dataset.status || 'Running';

    const machineTitle = document.querySelector('.machine-title');
    const machineSubtitle = document.querySelector('.machine-subtitle');
    if (machineTitle) machineTitle.textContent = machine;
    if (machineSubtitle) machineSubtitle.textContent = 'Order: ' + order;

    const items = document.querySelectorAll('.detail-item .value');
    if (items.length >= 4) {
        items[0].textContent = order;
        items[1].textContent = operator;
        items[2].textContent = status;
        items[3].textContent = 'N/A';
    }

    const statusBadge = document.querySelector('.sidebar-header .rounded-pill');
    if (statusBadge) {
        statusBadge.textContent = status.toUpperCase();
        if (status.toLowerCase() === 'running') {
            statusBadge.className = 'px-3 py-1 bg-secondary text-white rounded-pill small fw-bold';
        } else if (status.toLowerCase() === 'maintenance') {
            statusBadge.className = 'px-3 py-1 bg-danger text-white rounded-pill small fw-bold';
        } else {
            statusBadge.className = 'px-3 py-1 bg-secondary text-white rounded-pill small fw-bold';
        }
    }

    document.querySelectorAll('.table-custom tbody tr').forEach(r => {
        r.style.background = '';
    });
    this.style.background = 'rgba(0, 106, 97, 0.05)';
}

window.viewAllocation = function(allocationNo) {
    alert('View allocation: ' + allocationNo);
};

window.editAllocation = function(allocationNo) {
    alert('Edit allocation: ' + allocationNo);
};

window.deleteAllocation = function(allocationNo) {
    if (confirm('Are you sure you want to delete allocation ' + allocationNo + '?')) {
        fetch('../py/machine/machine_allocation.py?action=delete_allocation&allocation_no=' + allocationNo)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    loadAllAllocations();
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => console.error('Error deleting allocation:', error));
    }
};


/* ==========================================================================
   06. CREATE MACHINE ALLOCATION SCREEN
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {

    let currentAllocationNo = 'MA001';

    function loadKPI() {
        fetch('../py/machine/machine_allocation.py?action=get_kpi')
            .then(response => response.json())
            .then(data => {
                const kpiElements = {
                    'kpi_available': data.available || 0,
                    'kpi_running': data.running || 0,
                    'kpi_maintenance': data.maintenance || 0,
                    'kpi_today': data.today_allocations || 0
                };

                Object.keys(kpiElements).forEach(id => {
                    const el = document.getElementById(id);
                    if (el) el.textContent = kpiElements[id];
                });
            })
            .catch(error => console.error('Error loading KPI:', error));
    }

    function loadMachines() {
        fetch('../py/machine/machine_allocation.py?action=get_machines')
            .then(response => response.json())
            .then(data => {
                const machineSelect = document.getElementById('machine');
                if (machineSelect) {
                    machineSelect.innerHTML = '<option value="">Select Machine</option>';

                    if (Array.isArray(data) && !data.error) {
                        data.forEach(machine => {
                            const option = document.createElement('option');
                            option.value = machine.name;
                            option.textContent = machine.name + ' - ' + machine.status;
                            machineSelect.appendChild(option);
                        });
                    } else {
                        const fallbackMachines = ['Machine A', 'Machine B', 'Machine C', 'Machine D'];
                        fallbackMachines.forEach(machine => {
                            const option = document.createElement('option');
                            option.value = machine;
                            option.textContent = machine + ' - Available';
                            machineSelect.appendChild(option);
                        });
                    }
                }
            })
            .catch(error => {
                console.error('Error loading machines:', error);
                const machineSelect = document.getElementById('machine');
                if (machineSelect) {
                    machineSelect.innerHTML = '<option value="">Select Machine</option>';
                    const fallbackMachines = ['Machine A', 'Machine B', 'Machine C', 'Machine D'];
                    fallbackMachines.forEach(machine => {
                        const option = document.createElement('option');
                        option.value = machine;
                        option.textContent = machine + ' - Available';
                        machineSelect.appendChild(option);
                    });
                }
            });
    }

    function loadOperators() {
        fetch('../py/machine/machine_allocation.py?action=get_operators')
            .then(response => response.json())
            .then(data => {
                const operatorSelect = document.getElementById('operator');
                if (operatorSelect) {
                    operatorSelect.innerHTML = '<option value="">Select Operator</option>';

                    if (Array.isArray(data) && !data.error) {
                        data.forEach(operator => {
                            const option = document.createElement('option');
                            option.value = operator;
                            option.textContent = operator;
                            operatorSelect.appendChild(option);
                        });
                    } else {
                        const fallbackOperators = ['Ramesh', 'Suresh', 'Amit', 'Rajesh', 'Priya'];
                        fallbackOperators.forEach(operator => {
                            const option = document.createElement('option');
                            option.value = operator;
                            option.textContent = operator;
                            operatorSelect.appendChild(option);
                        });
                    }
                }
            })
            .catch(error => {
                console.error('Error loading operators:', error);
                const operatorSelect = document.getElementById('operator');
                if (operatorSelect) {
                    operatorSelect.innerHTML = '<option value="">Select Operator</option>';
                    const fallbackOperators = ['Ramesh', 'Suresh', 'Amit', 'Rajesh', 'Priya'];
                    fallbackOperators.forEach(operator => {
                        const option = document.createElement('option');
                        option.value = operator;
                        option.textContent = operator;
                        operatorSelect.appendChild(option);
                    });
                }
            });
    }

    function loadPlans() {
        fetch('../py/machine/machine_allocation.py?action=get_plans')
            .then(response => response.json())
            .then(data => {
                const select = document.getElementById('production_plan');
                if (select) {
                    select.innerHTML = '<option value="">Select Plan</option>';
                    if (Array.isArray(data) && !data.error) {
                        data.forEach(plan => {
                            const option = document.createElement('option');
                            option.value = plan;
                            option.textContent = plan;
                            select.appendChild(option);
                        });
                    }
                }
            })
            .catch(error => console.error('Error loading plans:', error));
    }

    function loadPlanDetails(planId) {
        if (!planId) {
            resetOrderDetails();
            return;
        }

        console.log('Loading plan details for:', planId);
        fetch(`../py/machine/machine_allocation.py?action=get_plan_details&plan_id=${planId}`)
            .then(response => response.json())
            .then(data => {
                console.log('Plan Details:', data);
                if (data.error) {
                    alert(data.error);
                    return;
                }

                const orderCells = document.querySelectorAll('.info-box-dashed .fw-bold');
                if (orderCells.length >= 4) {
                    orderCells[0].textContent = data.order_no || '-';
                    orderCells[1].textContent = data.customer || '-';
                    orderCells[2].textContent = data.fabric || '-';
                    orderCells[3].textContent = data.qty_required ? data.qty_required + ' Kg' : '-';
                }

                if (data.machine) {
                    const machineSelect = document.getElementById('machine');
                    if (machineSelect) {
                        let optionExists = false;
                        for (let option of machineSelect.options) {
                            if (option.value === data.machine) {
                                optionExists = true;
                                break;
                            }
                        }
                        if (!optionExists) {
                            const option = document.createElement('option');
                            option.value = data.machine;
                            option.textContent = data.machine + ' (From Plan)';
                            machineSelect.appendChild(option);
                        }
                        machineSelect.value = data.machine;
                        console.log('Auto-filled machine:', data.machine);
                    }
                } else {
                    console.log('No machine found in plan');
                }

                if (data.operator) {
                    const operatorSelect = document.getElementById('operator');
                    if (operatorSelect) {
                        let optionExists = false;
                        for (let option of operatorSelect.options) {
                            if (option.value === data.operator) {
                                optionExists = true;
                                break;
                            }
                        }
                        if (!optionExists) {
                            const option = document.createElement('option');
                            option.value = data.operator;
                            option.textContent = data.operator + ' (From Plan)';
                            operatorSelect.appendChild(option);
                        }
                        operatorSelect.value = data.operator;
                        console.log('Auto-filled operator:', data.operator);
                    }
                } else {
                    console.log('No operator found in plan');
                }

                const dateInputs = document.querySelectorAll('#assignmentForm input[type="date"]');
                if (dateInputs.length >= 2) {
                    if (data.start_date) {
                        dateInputs[0].value = data.start_date;
                        console.log('Auto-filled start date:', data.start_date);
                    }
                    if (data.end_date) {
                        dateInputs[1].value = data.end_date;
                        console.log('Auto-filled end date:', data.end_date);
                    }
                }

                updateSummary();
            })
            .catch(error => console.error('Error loading plan details:', error));
    }

    function resetOrderDetails() {
        const orderCells = document.querySelectorAll('.info-box-dashed .fw-bold');
        if (orderCells.length >= 4) {
            orderCells[0].textContent = '-';
            orderCells[1].textContent = '-';
            orderCells[2].textContent = '-';
            orderCells[3].textContent = '-';
        }
    }

    function updateSummary() {
        const allocationNo = document.getElementById('allocation_no');
        const machineSelect = document.getElementById('machine');
        const operatorSelect = document.getElementById('operator');
        const statusSelect = document.getElementById('status');
        const remarksText = document.getElementById('remarks');

        const orderCells = document.querySelectorAll('.info-box-dashed .fw-bold');
        const qty = orderCells.length >= 4 ? orderCells[3].textContent : '-';

        const summaryAllocation = document.querySelector('.summary-panel .fw-bold.fs-4');
        const summaryMachine = document.querySelectorAll('.summary-item .value')[0];
        const summaryOperator = document.querySelectorAll('.summary-item .value')[1];
        const summaryTarget = document.querySelectorAll('.summary-item .value')[2];
        const summaryStatus = document.querySelector('.preview-badge');
        const summaryRemarks = document.querySelector('.summary-panel .fst-italic');

        if (summaryAllocation && allocationNo) {
            summaryAllocation.textContent = allocationNo.value || 'MA001';
        }

        if (summaryMachine && machineSelect) {
            summaryMachine.textContent = machineSelect.value || '-';
        }

        if (summaryOperator && operatorSelect) {
            summaryOperator.textContent = operatorSelect.value || '-';
        }

        if (summaryTarget) {
            summaryTarget.textContent = qty || '-';
        }

        if (summaryStatus && statusSelect) {
            summaryStatus.textContent = statusSelect.value || 'Assigned';
        }

        if (summaryRemarks && remarksText) {
            summaryRemarks.textContent = remarksText.value ? `"${remarksText.value}"` : '"No remarks yet"';
        }
    }

    function handleMachineSubmit(e) {
        e.preventDefault();

        const planSelect = document.getElementById('production_plan');
        const machineSelect = document.getElementById('machine');
        const operatorSelect = document.getElementById('operator');
        const shiftSelect = document.getElementById('shift');
        const statusSelect = document.getElementById('status');
        const dateInputs = document.querySelectorAll('#assignmentForm input[type="date"]');
        const remarksText = document.getElementById('remarks');

        const plan_no = planSelect ? planSelect.value : '';
        const machine = machineSelect ? machineSelect.value : '';
        const operator = operatorSelect ? operatorSelect.value : '';
        const shift = shiftSelect ? shiftSelect.value : 'Morning';
        const status = statusSelect ? statusSelect.value : 'Assigned';
        const start_date = dateInputs.length >= 1 ? dateInputs[0].value : '';
        const end_date = dateInputs.length >= 2 ? dateInputs[1].value : '';
        const remarks = remarksText ? remarksText.value : '';

        if (!plan_no) {
            alert('Please select a Production Plan');
            return;
        }
        if (!machine) {
            alert('Please select a Machine');
            return;
        }
        if (!operator) {
            alert('Please select an Operator');
            return;
        }

        const formData = new URLSearchParams();
        formData.append('action', 'submit_allocation');
        formData.append('plan_no', plan_no);
        formData.append('machine', machine);
        formData.append('operator', operator);
        formData.append('shift', shift);
        formData.append('status', status);
        formData.append('start_date', start_date);
        formData.append('end_date', end_date);
        formData.append('remarks', remarks);

        fetch('../py/machine/machine_allocation.py?' + formData.toString(), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                const allocationInput = document.getElementById('allocation_no');
                if (allocationInput) {
                    allocationInput.value = data.allocation_no;
                }
                resetForm();
                loadKPI();
                loadAllAllocations();
                updateSummary();
            } else {
                alert('Error: ' + (data.error || 'Unknown error occurred'));
            }
        })
        .catch(error => {
            console.error('Error submitting form:', error);
            alert('Error submitting form. Please check console.');
        });
    }

    function resetForm() {
        const selects = document.querySelectorAll('#assignmentForm select');
        const dateInputs = document.querySelectorAll('#assignmentForm input[type="date"]');
        const textarea = document.getElementById('remarks');

        selects.forEach((select) => {
            if (select.id === 'production_plan') {
                select.value = '';
            } else if (select.id === 'shift') {
                select.value = 'Morning';
            } else if (select.id === 'status') {
                select.value = 'Assigned';
            } else {
                select.value = '';
            }
        });

        dateInputs.forEach(input => {
            input.value = '';
        });

        if (textarea) {
            textarea.value = '';
        }

        resetOrderDetails();
        updateSummary();
    }

    const form = document.getElementById('assignmentForm');
    if (form) {
        form.onsubmit = handleMachineSubmit;
    }

    const cancelBtn = document.querySelector('.btn-cancel-form');
    if (cancelBtn) {
        cancelBtn.onclick = resetForm;
    }

    const planSelect = document.getElementById('production_plan');
    if (planSelect) {
        planSelect.onchange = function() {
            loadPlanDetails(this.value);
        };
    }

    document.querySelectorAll('#assignmentForm select, #assignmentForm input, #assignmentForm textarea').forEach(element => {
        element.addEventListener('change', updateSummary);
        element.addEventListener('input', updateSummary);
    });

    const refreshBtn = document.querySelector('.bi-arrow-repeat')?.closest('button');
    if (refreshBtn) {
        refreshBtn.onclick = loadAllAllocations;
    }

    const dateInputsElem = document.querySelectorAll('#assignmentForm input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    if (dateInputsElem.length >= 1) {
        dateInputsElem[0].value = today;
    }

    loadKPI();
    loadPlans();
    loadMachines();
    loadOperators();
    loadAllAllocations();

    setInterval(loadKPI, 30000);
    setInterval(loadAllAllocations, 60000);

});

function handlemahineSubmit(e) {
    e.preventDefault();
    alert('Machine assigned successfully!');
}


/* ==========================================================================
   07. ADD MACHINE SCREEN (PAGE 12)
   ========================================================================== */

function loadMachinesTable() {
    fetch("../py/Addmachine/get_machinedata.py")
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById("machineTablebody");
            if (tableBody) {
                if (data.status === "success") {
                    tableBody.innerHTML = data.table_html;
                } else {
                    tableBody.innerHTML = `<tr><td colspan="2" class="text-danger text-center">Error loading machines: ${data.message}</td></tr>`;
                }
            }
        })
        .catch(error => {
            console.error("Error loading machines:", error);
        });
}

document.addEventListener("DOMContentLoaded", function() {
    loadMachinesTable();
});

//THIS FUNCTION HANDLES MACHINE SEARCH
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchFabric');
    const machineTableBody = document.getElementById('machineTablebody');

    // Filter Function
    function filterMachines() {
        const query = searchInput.value.toLowerCase().trim();
        const rows = machineTableBody.getElementsByTagName('tr');

        Array.from(rows).forEach(row => {
            // Get text from the first column (Name)
            const name = row.children[0]?.textContent.toLowerCase() || '';

            // Toggle visibility based on search match
            if (name.includes(query)) {
                row.style.display = ''; // Show row
            } else {
                row.style.display = 'none'; // Hide row
            }
        });
    }

    // Trigger filter live as user types
    searchInput.addEventListener('input', filterMachines);
});

/* ==========================================================================
   08. ADD SUPERVISOR SCREEN (PAGE 13)
   ========================================================================== */

function loadSupervisorTable() {
    fetch("../py/supervisor/get_Supervisor.py")
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById("SupervisorTablebody");
            if (tableBody) {
                if (data.status === "success") {
                    tableBody.innerHTML = data.table_html;
                } else {
                    tableBody.innerHTML = `<tr><td colspan="2" class="text-danger text-center">Error loading machines: ${data.message}</td></tr>`;
                }
            }
        })
        .catch(error => {
            console.error("Error loading machines:", error);
        });
}

document.addEventListener("DOMContentLoaded", function() {
    loadSupervisorTable();
});

//THIS FUNCTION HANDLES SUPERVISOR SEARCH
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchSupervisor');
    const machineTableBody = document.getElementById('SupervisorTablebody');

    // Filter Function
    function filterMachines() {
        const query = searchInput.value.toLowerCase().trim();
        const rows = machineTableBody.getElementsByTagName('tr');

        Array.from(rows).forEach(row => {
            // Get text from the first column (Name)
            const name = row.children[0]?.textContent.toLowerCase() || '';

            // Toggle visibility based on search match
            if (name.includes(query)) {
                row.style.display = ''; // Show row
            } else {
                row.style.display = 'none'; // Hide row
            }
        });
    }

    // Trigger filter live as user types
    searchInput.addEventListener('input', filterMachines);
});


/* ==========================================================================
   09. DELIVERY & OTHER UTILITIES
   ========================================================================== */

function showdeliveryToast() {
    const toast = document.getElementById('successdeliveryToast');
    if (toast) toast.classList.add('show');

    clearTimeout(window.toastTimeout);
    window.toastTimeout = setTimeout(() => {
        hidedeliveryToast();
    }, 5000);
}

function hidedeliveryToast() {
    const toast = document.getElementById('successdeliveryToast');
    if (toast) toast.classList.remove('show');
}

function handledeliverySubmit(e) {
    e.preventDefault();

    const btn = document.getElementById('submitBtn');
    const originalHTML = btn.innerHTML;

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Processing...';

    setTimeout(() => {
        showdeliveryToast();
        btn.disabled = false;
        btn.innerHTML = originalHTML;
    }, 800);
}

document.querySelectorAll('.radio-group-custom .radio-item input').forEach(radio => {
    radio.addEventListener('change', function() {
        const parent = this.closest('.radio-group-custom');
        parent.querySelectorAll('.radio-item span').forEach(span => {
            span.classList.remove('active');
        });
        this.closest('.radio-item').querySelector('span').classList.add('active');

        const statusText = document.querySelector('.summary-status .status-text');
        if (statusText) {
            statusText.textContent = this.value;
        }
    });
});


/* ==========================================================================
   10. LOGOUT MODAL & ACTIONS
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