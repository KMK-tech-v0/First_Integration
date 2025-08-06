// Base URL for your Flask API
const API_BASE_URL = 'http://localhost:5000'; // Ensure this matches your Flask app's port
// SQL Server Instance: DESKTOP-17P73P0\SQLEXPRESS

// Global error handler for unhandled promise rejections
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);

    // Check if it's a fetch-related error
    if (event.reason && event.reason.name === 'TypeError' &&
        (event.reason.message.includes('fetch') ||
         event.reason.message.includes('Failed to fetch') ||
         event.reason.message.includes('NetworkError'))) {

        console.log('Network error detected globally, ensuring demo mode is enabled');

        // Prevent the default error handling
        event.preventDefault();

        // Enable demo mode if not already enabled
        if (!localStorage.getItem('demo_mode')) {
            localStorage.setItem('demo_mode', 'true');
            localStorage.setItem('demo_username', 'demo_user');

            // Show a user-friendly message
            showAuthMessage('Backend server not available. Running in demo mode.', 'warning');
        }
    }
});

// Global variables for material and service info, fetched once
let allMaterialInfo = [];
let allServiceInfo = [];
let currentEditReportTransNum = null; // To store trans_num of the report being edited
let deletedPhotoIds = []; // To store IDs of photos marked for deletion
let newPhotos = []; // To store new photo files for upload
let addMapInstance = null; // Leaflet map instance for add form
let editMapInstance = null; // Leaflet map instance for edit modal
let largeMapInstance = null; // Leaflet map instance for the large map modal
let largeMapMarker = null; // Marker for the large map modal
// Add these variables at the top with other global variables
let currentInventoryData = []; // To store the original inventory data
let filteredInventoryData = []; // To store filtered data

// Safe fetch wrapper that handles network errors gracefully
async function safeFetch(url, options = {}) {
    try {
        const response = await fetch(url, options);
        return response;
    } catch (error) {
        console.error('Fetch error:', error);

        // Check if it's a network-related error
        if (error.name === 'TypeError' &&
            (error.message.includes('fetch') ||
             error.message.includes('Failed to fetch') ||
             error.message.includes('NetworkError') ||
             error.message.includes('network'))) {

            // Enable demo mode if not already enabled
            if (!localStorage.getItem('demo_mode')) {
                localStorage.setItem('demo_mode', 'true');
                localStorage.setItem('demo_username', 'demo_user');
                console.log('Network error detected, enabling demo mode');
            }

            // Re-throw with a more specific error
            const networkError = new Error('Backend server not available');
            networkError.name = 'NetworkError';
            networkError.originalError = error;
            throw networkError;
        }

        // Re-throw other errors as-is
        throw error;
    }
}

// Utility function to show messages (for general app messages)
function showMessage(message, type = 'success') {
    const messageBox = document.getElementById('messageBox');
    messageBox.textContent = message;
    messageBox.className = `message-box ${type}`; // Reset classes and add new ones
    messageBox.style.display = 'block';
    setTimeout(() => {
        messageBox.style.display = 'none';
    }, 3000); // Hide after 3 seconds
}

// Utility function to show messages (for authentication specific messages)
function showAuthMessage(message, type = 'info') {
    const messageBox = document.getElementById('messageBoxAuth');
    messageBox.textContent = message;
    messageBox.className = `p-3 mb-4 rounded-md text-sm ${
        type === 'success' ? 'bg-green-100 text-green-800' :
        type === 'error' ? 'bg-red-100 text-red-800' :
        type === 'warning' ? 'bg-yellow-100 text-yellow-800' :
        'bg-blue-100 text-blue-800'
    }`;
    messageBox.classList.remove('hidden');
    setTimeout(() => {
        messageBox.classList.add('hidden');
    }, 5000); // Hide after 5 seconds
}

// Function to get authorization headers for protected routes
function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    if (token) {
        return {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json' // Default for JSON payloads
        };
    }
    return {};
}

// Function to check authentication status and manage UI visibility
async function checkAuth() {
    const token = localStorage.getItem('access_token');
    const demoMode = localStorage.getItem('demo_mode');
    const demoUsername = localStorage.getItem('demo_username');
    const authContainer = document.getElementById('authContainer');
    const appContent = document.getElementById('appContent');
    const loggedInUserSpan = document.getElementById('loggedInUser');
    const navLinksAfterLogin = document.querySelectorAll('.login-nav .nav-link');

    if (token) {
        // Check if we're in demo mode (backend not available)
        if (demoMode === 'true') {
            // Demo mode - skip backend validation
            loggedInUserSpan.textContent = `Demo Mode - Logged in as: ${demoUsername || 'User'} (Backend not connected)`;
            authContainer.classList.add('hidden');
            appContent.classList.remove('hidden');
            document.body.style.paddingTop = '108px';

            // Show demo banner
            document.getElementById('demoBanner').classList.remove('hidden');

            // Enable navigation links
            navLinksAfterLogin.forEach(link => {
                if (!link.dataset.featureStatus || link.dataset.featureStatus !== 'unavailable') {
                    link.classList.remove('disabled-link');
                    link.style.pointerEvents = 'auto';
                }
            });

            // Show the first tab
            document.querySelector('.tab-button[data-tab="faultReports"]').click();
            return;
        }

        try {
            // Attempt to access a protected route to validate the token
            const response = await safeFetch(`${API_BASE_URL}/protected`, {
                method: 'GET',
                headers: getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                loggedInUserSpan.textContent = `Logged in as: ${data.logged_in_as}`;
                authContainer.classList.add('hidden');
                appContent.classList.remove('hidden');
                // Adjust body padding for fixed header when appContent is visible
                document.body.style.paddingTop = '108px';
                // If already logged in, fetch initial data
                document.querySelector('.tab-button[data-tab="faultReports"]').click();

                // Enable navigation links after login
                navLinksAfterLogin.forEach(link => {
                    if (!link.dataset.featureStatus || link.dataset.featureStatus !== 'unavailable') {
                        link.classList.remove('disabled-link');
                        link.style.pointerEvents = 'auto'; // Re-enable pointer events
                    }
                });

            } else {
                // Token invalid or expired
                console.error("Token validation failed:", response.status);
                clearAuthData();
                showAuthMessage('Your session has expired or is invalid. Please log in again.', 'warning');
                resetToLoginState(authContainer, appContent, navLinksAfterLogin);
            }
        } catch (error) {
            console.error('Error validating token:', error);

            // If it's a network error, try demo mode - improved error detection
            if (error.name === 'TypeError' &&
                (error.message.includes('fetch') ||
                 error.message.includes('Failed to fetch') ||
                 error.message.includes('NetworkError') ||
                 error.message.includes('network'))) {
                console.log('Backend not available, switching to demo mode');
                localStorage.setItem('demo_mode', 'true');
                localStorage.setItem('demo_username', 'demo_user');
                checkAuth(); // Retry with demo mode
                return;
            }

            clearAuthData();
            showAuthMessage('Could not connect to authentication server. Please try again.', 'error');
            resetToLoginState(authContainer, appContent, navLinksAfterLogin);
        }
    } else {
        resetToLoginState(authContainer, appContent, navLinksAfterLogin);
    }
}

// Helper function to clear authentication data
function clearAuthData() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('demo_mode');
    localStorage.removeItem('demo_username');
}

// Helper function to reset to login state
function resetToLoginState(authContainer, appContent, navLinksAfterLogin) {
    authContainer.classList.remove('hidden');
    appContent.classList.add('hidden');
    document.body.style.paddingTop = '0'; // Reset padding

    // Hide demo banner
    document.getElementById('demoBanner').classList.add('hidden');

    // Disable navigation links if not logged in
    navLinksAfterLogin.forEach(link => {
        link.classList.add('disabled-link');
        link.style.pointerEvents = 'none'; // Disable pointer events
    });
}

// Handle login/registration form submission
document.getElementById('authForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const authSubmitBtn = document.getElementById('authSubmitBtn');
    const authTitle = document.getElementById('authTitle');

    const username = usernameInput.value;
    const password = passwordInput.value;

    // Basic validation
    if (!username || !password) {
        showAuthMessage('Please enter both username and password.', 'error');
        return;
    }

    authSubmitBtn.disabled = true;
    authSubmitBtn.textContent = 'Processing...';

    const endpoint = authTitle.textContent === 'Login' ? '/login' : '/register';

    try {
        const response = await safeFetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            if (endpoint === '/login') {
                localStorage.setItem('access_token', data.access_token);
                showAuthMessage('Login successful!', 'success');
                checkAuth(); // Re-check auth to show app content
            } else { // Registration successful
                showAuthMessage('Registration successful! Please log in.', 'success');
                authTitle.textContent = 'Login'; // Switch to login form
                document.getElementById('toggleAuthMode').textContent = 'Register here';
            }
        } else {
            showAuthMessage(data.msg || data.error || 'Authentication failed.', 'error');
        }
    } catch (error) {
        console.error('Authentication error:', error);

        // Handle network errors (no backend server) - improved error detection
        if (error.name === 'TypeError' &&
            (error.message.includes('fetch') ||
             error.message.includes('Failed to fetch') ||
             error.message.includes('NetworkError') ||
             error.message.includes('network'))) {
            handleOfflineAuth(username, password, endpoint, authTitle);
        } else {
            showAuthMessage('Network error or server unreachable.', 'error');
        }
    } finally {
        authSubmitBtn.disabled = false;
        authSubmitBtn.textContent = authTitle.textContent === 'Login' ? 'Login' : 'Register';
    }
});

// Handle authentication when backend is not available (demo mode)
function handleOfflineAuth(username, password, endpoint, authTitle) {
    if (endpoint === '/login') {
        // Demo login - accept any username/password
        if (username.length >= 3 && password.length >= 3) {
            // Generate a mock JWT token
            const mockToken = btoa(JSON.stringify({
                username: username,
                role: username === 'admin' ? 'admin' : 'user',
                exp: Date.now() + (24 * 60 * 60 * 1000) // 24 hours
            }));

            localStorage.setItem('access_token', mockToken);
            localStorage.setItem('demo_mode', 'true');
            localStorage.setItem('demo_username', username);

            showAuthMessage('Demo Login Successful! (Backend not connected)', 'success');
            checkAuth();
        } else {
            showAuthMessage('Username and password must be at least 3 characters long.', 'error');
        }
    } else {
        // Demo registration
        if (username.length >= 3 && password.length >= 6) {
            showAuthMessage('Demo Registration Successful! Please log in. (Backend not connected)', 'success');
            authTitle.textContent = 'Login';
            document.getElementById('toggleAuthMode').textContent = 'Register here';
        } else {
            showAuthMessage('Username must be 3+ chars, password must be 6+ chars.', 'error');
        }
    }
}

// Handle logout
document.getElementById('logoutBtn').addEventListener('click', () => {
    clearAuthData();
    showAuthMessage('Logged out successfully.', 'info');
    checkAuth(); // Re-check auth to show login form
});

// Toggle between login and register modes
document.getElementById('toggleAuthMode').addEventListener('click', (event) => {
    event.preventDefault();
    const authTitle = document.getElementById('authTitle');
    const authSubmitBtn = document.getElementById('authSubmitBtn');
    if (authTitle.textContent === 'Login') {
        authTitle.textContent = 'Register';
        authSubmitBtn.textContent = 'Register';
        event.target.textContent = 'Login here';
    } else {
        authTitle.textContent = 'Login';
        authSubmitBtn.textContent = 'Login';
        event.target.textContent = 'Register here';
    }
});


// Function to format datetime-local input value to ISO string
function formatDatetimeLocalToISO(datetimeLocalString) {
    if (!datetimeLocalString) return null;
    // Append ':00' for seconds if not present, and 'Z' for UTC if not specified
    // Assuming input is local time, we'll send it as is for backend to parse
    return datetimeLocalString + ':00'; // Add seconds part
}

// Function to format ISO string to datetime-local input value
function formatISOToDatetimeLocal(isoString) {
    if (!isoString) return '';
    try {
        // Remove Z and milliseconds if present, then take YYYY-MM-DDTHH:MM
        return isoString.substring(0, 16);
    } catch (e) {
        console.error("Error formatting ISO string to datetime-local:", e);
        return '';
    }
}

// Function to calculate duration string
function calculateDuration(raisedTimeStr, clearedTimeStr) {
    if (!raisedTimeStr || !clearedTimeStr) return 'N/A';
    try {
        const raised = new Date(raisedTimeStr);
        const cleared = new Date(clearedTimeStr);
        if (cleared < raised) return "Invalid Time";

        const diffSeconds = Math.floor((cleared - raised) / 1000);
        const hours = Math.floor(diffSeconds / 3600);
        const minutes = Math.floor((diffSeconds % 3600) / 60);
        const seconds = diffSeconds % 60;

        return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    } catch (e) {
        console.error("Error calculating duration:", e);
        return 'N/A';
    }
}

// --- Tab Switching Logic ---
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.add('hidden'));

        button.classList.add('active');
        const targetTab = button.dataset.tab;
        document.getElementById(targetTab).classList.remove('hidden');

        // Load data for the active tab
        if (targetTab === 'faultReports') {
            fetchAllReports();
        } else if (targetTab === 'materialInventory') {
            fetchMaterialInventory();
        } else if (targetTab === 'materialInfo') {
            fetchMaterialInfo();
        } else if (targetTab === 'serviceInfo') {
            fetchServiceInfo();
        } else if (targetTab === 'userManagement') { // NEW: User Management tab
            fetchUsers();
        }
    });
});

// --- Map Initialization and Handling ---
function initMap(mapId, latInputId, longInputId, initialLat = 16.8, initialLong = 96.1) {
    const mapElement = document.getElementById(mapId);
    if (!mapElement) return null; // Map element might not be in the DOM yet

    // Check if a map instance already exists for this element and remove it
    if (mapElement._leaflet_id) {
        const existingMap = mapElement._leaflet_id;
        for (let i in mapElement._leaflet_fb_events) {
            mapElement._leaflet_fb_events[i].off();
        }
        mapElement._leaflet_id = null;
        // L.map(mapId).remove(); // This line might cause issues if not called on the map instance
    }

    const map = L.map(mapId).setView([initialLat, initialLong], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    let marker = L.marker([initialLat, initialLong]).addTo(map);

    const latInput = document.getElementById(latInputId);
    const longInput = document.getElementById(longInputId);

    // Set initial values in inputs
    latInput.value = initialLat;
    longInput.value = initialLong;

    map.on('click', function(e) {
        const { lat, lng } = e.latlng;
        marker.setLatLng([lat, lng]);
        latInput.value = lat.toFixed(6);
        longInput.value = lng.toFixed(6);

        // Open large map modal on map click
        showLargeMapModal(lat, lng, latInput, longInput);
    });

    // Update marker if input values change
    latInput.addEventListener('change', () => {
        const lat = parseFloat(latInput.value);
        const lng = parseFloat(longInput.value);
        if (!isNaN(lat) && !isNaN(lng)) {
            marker.setLatLng([lat, lng]);
            map.setView([lat, lng]);
        }
    });

    longInput.addEventListener('change', () => {
        const lat = parseFloat(longInput.value);
        const lng = parseFloat(longInput.value);
        if (!isNaN(lat) && !isNaN(lng)) {
            marker.setLatLng([lat, lng]);
            map.setView([lat, lng]);
        }
    });
    return { map, marker }; // Return both map and marker
}

// --- Large Map Modal Logic ---
const largeMapModal = document.getElementById('largeMapModal');
const closeLargeMapModalBtn = document.getElementById('closeLargeMapModalBtn');

closeLargeMapModalBtn.addEventListener('click', () => {
    largeMapModal.classList.add('hidden');
    if (largeMapInstance) {
        largeMapInstance.remove(); // Clean up map instance
        largeMapInstance = null;
        largeMapMarker = null;
    }
});

function showLargeMapModal(lat, lng, latInput, longInput) {
    largeMapModal.classList.remove('hidden');
    // Ensure the map container is visible before initializing the map
    setTimeout(() => {
        if (largeMapInstance) largeMapInstance.remove(); // Remove previous instance if any

        largeMapInstance = L.map('largeMapModalMap').setView([lat, lng], 16);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(largeMapInstance);

        largeMapMarker = L.marker([lat, lng]).addTo(largeMapInstance);

        largeMapInstance.on('click', function(e) {
            const { lat: newLat, lng: newLng } = e.latlng;
            largeMapMarker.setLatLng([newLat, newLng]);
            latInput.value = newLat.toFixed(6);
            longInput.value = newLng.toFixed(6);
            // Update the smaller map as well if it's the add/edit form map
            if (latInput.id === 'locationLat' && addMapInstance && addMapInstance.marker) {
                addMapInstance.marker.setLatLng([newLat, newLng]);
                addMapInstance.map.setView([newLat, newLng]);
            } else if (latInput.id === 'editLocationLat' && editMapInstance && editMapInstance.marker) {
                editMapInstance.marker.setLatLng([newLat, newLng]);
                editMapInstance.map.setView([newLat, newLng]);
            }
        });
        largeMapInstance.invalidateSize(); // Invalidate size after modal becomes visible
    }, 50); // Small delay to ensure modal is rendered
}


// --- Photo Upload Logic ---
const photoUploadInput = document.getElementById('photoUpload');
const photoPreviewContainer = document.getElementById('photoPreviewContainer');

photoUploadInput.addEventListener('change', (event) => {
    handlePhotoUpload(event.target.files, photoPreviewContainer);
});

function handlePhotoUpload(files, previewContainer, isEdit = false, existingPhoto = null) {
    Array.from(files).forEach(file => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const previewItem = document.createElement('div');
            previewItem.classList.add('photo-preview-item');

            const img = document.createElement('img');
            img.src = e.target.result;
            previewItem.appendChild(img);

            const removeButton = document.createElement('span');
            removeButton.classList.add('remove-photo-button');
            removeButton.innerHTML = '&times;';
            removeButton.addEventListener('click', () => {
                previewContainer.removeChild(previewItem);
                if (isEdit && existingPhoto && existingPhoto.id) {
                    deletedPhotoIds.push(existingPhoto.id);
                } else {
                    // Remove from newPhotos array for add/edit form
                    const index = newPhotos.findIndex(p => p.file === file);
                    if (index > -1) {
                        newPhotos.splice(index, 1);
                    }
                }
            });
            previewItem.appendChild(removeButton);

            const labelInput = document.createElement('input');
            labelInput.type = 'text';
            labelInput.placeholder = 'Label';
            labelInput.classList.add('photo-label', 'absolute', 'bottom-0', 'left-0', 'right-0', 'bg-gray-800', 'bg-opacity-75', 'text-white', 'text-xs', 'p-1', 'text-center', 'w-full', 'border-none', 'rounded-b-md');
            labelInput.addEventListener('click', (e) => e.stopPropagation()); // Prevent click from propagating to parent
            labelInput.addEventListener('change', () => {
                if (isEdit && existingPhoto) {
                    existingPhoto.label = labelInput.value;
                } else {
                    const photoEntry = newPhotos.find(p => p.file === file);
                    if (photoEntry) photoEntry.label = labelInput.value;
                }
            });
            previewItem.appendChild(labelInput);

            if (isEdit && existingPhoto) {
                labelInput.value = existingPhoto.label || '';
                previewItem.dataset.photoId = existingPhoto.id; // Store ID for existing photos
                previewItem.dataset.isExisting = 'true';
            } else {
                // For new photos, add to newPhotos array
                newPhotos.push({ file: file, label: '' });
            }

            previewContainer.appendChild(previewItem);
        };
        reader.readAsDataURL(file);
    });
}

// --- Dynamic Material/Service Input Fields ---
const materialsUsedContainer = document.getElementById('materialsUsedContainer');
const addMaterialBtn = document.getElementById('addMaterialBtn');
const servicesUsedContainer = document.getElementById('servicesUsedContainer');
const addServiceBtn = document.getElementById('addServiceBtn');

function addMaterialField(container, material = {}, isEdit = false) {
    const materialDiv = document.createElement('div');
    // Adjusted classes for narrower fields and better alignment
    materialDiv.classList.add('flex', 'flex-col', 'sm:flex-row', 'items-center', 'gap-2', 'p-2', 'bg-gray-50', 'rounded-md', 'shadow-sm');
    materialDiv.dataset.id = material.id || ''; // Store ID for existing materials

    let materialOptions = allMaterialInfo.map(m => `<option value="${m.material_code}" ${material.material_code === m.material_code ? 'selected' : ''}>${m.material_name} (${m.material_code})</option>`).join('');

    materialDiv.innerHTML = `
        <select class="material-code-select flex-grow sm:w-1/2 rounded-md shadow-sm input-field p-2" required>
            <option value="">Select Material</option>
            ${materialOptions}
        </select>
        <span class="material-uom text-sm text-gray-600 sm:w-1/6 text-center">${material.uom || 'UoM'}</span>
        <input type="number" step="0.01" placeholder="Usage" value="${material.material_usage || ''}" class="material-usage-input sm:w-1/4 rounded-md shadow-sm input-field p-2" required>
        <button type="button" class="remove-material-btn text-danger-color hover:text-red-700 p-2 rounded-full">
            <i class="fas fa-trash"></i>
        </button>
    `;
    container.appendChild(materialDiv);

    const selectElement = materialDiv.querySelector('.material-code-select');
    const usageInput = materialDiv.querySelector('.material-usage-input');
    const uomSpan = materialDiv.querySelector('.material-uom');

    // Set initial values for existing materials
    if (material.material_code) {
        selectElement.value = material.material_code;
        usageInput.value = material.material_usage;
    }

    // Update material name/type/uom when material code changes
    selectElement.addEventListener('change', () => {
        const selectedMaterial = allMaterialInfo.find(m => m.material_code === selectElement.value);
        if (selectedMaterial) {
            materialDiv.dataset.materialName = selectedMaterial.material_name;
            materialDiv.dataset.materialType = selectedMaterial.material_type;
            materialDiv.dataset.uom = selectedMaterial.uom;
            uomSpan.textContent = selectedMaterial.uom;
        } else {
            materialDiv.dataset.materialName = '';
            materialDiv.dataset.materialType = '';
            materialDiv.dataset.uom = '';
            uomSpan.textContent = 'UoM';
        }
    });

    // Trigger change to set initial data attributes and UoM for existing materials
    if (material.material_code) {
        const selectedMaterial = allMaterialInfo.find(m => m.material_code === material.material_code);
        if (selectedMaterial) {
            materialDiv.dataset.materialName = selectedMaterial.material_name;
            materialDiv.dataset.materialType = selectedMaterial.material_type;
            materialDiv.dataset.uom = selectedMaterial.uom;
            uomSpan.textContent = selectedMaterial.uom;
        }
    }

    materialDiv.querySelector('.remove-material-btn').addEventListener('click', () => {
        container.removeChild(materialDiv);
    });
}

function addServiceField(container, service = {}, isEdit = false) {
    const serviceDiv = document.createElement('div');
    // Adjusted classes for narrower fields and better alignment
    serviceDiv.classList.add('flex', 'flex-col', 'sm:flex-row', 'items-center', 'gap-2', 'p-2', 'bg-gray-50', 'rounded-md', 'shadow-sm');
    serviceDiv.dataset.id = service.id || ''; // Store ID for existing services

    let serviceOptions = allServiceInfo.map(s => `<option value="${s.service_code}" ${service.service_code === s.service_code ? 'selected' : ''}>${s.service_name} (${s.service_code})</option>`).join('');

    serviceDiv.innerHTML = `
        <select class="service-code-select flex-grow sm:w-1/2 rounded-md shadow-sm input-field p-2" required>
            <option value="">Select Service</option>
            ${serviceOptions}
        </select>
        <span class="service-uom text-sm text-gray-600 sm:w-1/6 text-center">${service.uom || 'UoM'}</span>
        <input type="number" step="0.01" placeholder="Usage" value="${service.service_usage || ''}" class="service-usage-input sm:w-1/4 rounded-md shadow-sm input-field p-2" required>
        <button type="button" class="remove-service-btn text-danger-color hover:text-red-700 p-2 rounded-full">
            <i class="fas fa-trash"></i>
        </button>
    `;
    container.appendChild(serviceDiv);

    const selectElement = serviceDiv.querySelector('.service-code-select');
    const usageInput = serviceDiv.querySelector('.service-usage-input');
    const uomSpan = serviceDiv.querySelector('.service-uom');

    // Set initial values for existing services
    if (service.service_code) {
        selectElement.value = service.service_code;
    }

    // Update service name/type/uom when service code changes
    selectElement.addEventListener('change', () => {
        const selectedService = allServiceInfo.find(s => s.service_code === selectElement.value);
        if (selectedService) {
            serviceDiv.dataset.serviceName = selectedService.service_name;
            serviceDiv.dataset.serviceType = selectedService.service_type;
            serviceDiv.dataset.uom = selectedService.uom;
            uomSpan.textContent = selectedService.uom;
        } else {
            serviceDiv.dataset.serviceName = '';
            serviceDiv.dataset.serviceType = '';
            serviceDiv.dataset.uom = '';
            uomSpan.textContent = 'UoM';
        }
    });

    // Trigger change to set initial data attributes and UoM for existing services
    if (service.service_code) {
        const selectedService = allServiceInfo.find(s => s.service_code === service.service_code);
        if (selectedService) {
            serviceDiv.dataset.serviceName = selectedService.service_name;
            serviceDiv.dataset.serviceType = selectedService.service_type;
            serviceDiv.dataset.uom = selectedService.uom;
            uomSpan.textContent = selectedService.uom;
        }
    }

    serviceDiv.querySelector('.remove-service-btn').addEventListener('click', () => {
        container.removeChild(serviceDiv);
    });
}

addMaterialBtn.addEventListener('click', () => addMaterialField(materialsUsedContainer));
addServiceBtn.addEventListener('click', () => addServiceField(servicesUsedContainer));

// --- Fetch Dropdown Data (Materials & Services) ---
async function fetchMaterialInfoForDropdown() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/materials_info`, {
            headers: getAuthHeaders()
        });
        if (response.status === 401) {
            showAuthMessage('Session expired. Please log in again.', 'error');
            localStorage.removeItem('access_token');
            checkAuth();
            throw new Error('Unauthorized');
        }
        if (!response.ok) throw new Error('Failed to fetch material info');
        allMaterialInfo = await response.json();
    } catch (error) {
        console.error("Error fetching material info for dropdown:", error);
        if (error.message !== 'Unauthorized') {
            showMessage("ပစ္စည်းအချက်အလက်များ ရယူရာတွင် အမှားဖြစ်���ည်", "error");
        }
    }
}

async function fetchServiceInfoForDropdown() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/services_info`, {
            headers: getAuthHeaders()
        });
        if (response.status === 401) {
            showAuthMessage('Session expired. Please log in again.', 'error');
            localStorage.removeItem('access_token');
            checkAuth();
            throw new Error('Unauthorized');
        }
        if (!response.ok) throw new Error('Failed to fetch service info');
        allServiceInfo = await response.json();
    } catch (error) {
        console.error("Error fetching service info for dropdown:", error);
        if (error.message !== 'Unauthorized') {
            showMessage("ဝန်ဆောင်မှုအချက်အလက်များ ရယူရာတွင် အမှားဖြစ်သည်", "error");
        }
    }
}

// --- Demo Functions (backend simulation) ---
async function fetchAllReports() {
    const reportsTableBody = document.getElementById('reportsTableBody');
    reportsTableBody.innerHTML = `
        <tr><td colspan="9" class="text-center py-8">
            <div class="flex flex-col items-center">
                <i class="fas fa-server text-4xl text-gray-400 mb-4"></i>
                <h3 class="text-lg font-semibold text-gray-600 mb-2">Demo Mode - No Backend Connected</h3>
                <p class="text-gray-500 mb-4">This is a frontend demonstration. To see real data:</p>
                <div class="text-sm text-gray-400">
                    <p>1. Set up SQL Server database using provided scripts</p>
                    <p>2. Implement backend API server</p>
                    <p>3. Connect frontend to your API endpoint</p>
                </div>
            </div>
        </td></tr>
    `;
}

async function fetchMaterialInventory() {
    const materialInventoryTableBody = document.getElementById('materialInventoryTableBody');
    materialInventoryTableBody.innerHTML = `
        <tr><td colspan="12" class="text-center py-8">
            <div class="flex flex-col items-center">
                <i class="fas fa-warehouse text-4xl text-gray-400 mb-4"></i>
                <h3 class="text-lg font-semibold text-gray-600 mb-2">Demo Mode - Material Inventory</h3>
                <p class="text-gray-500 mb-2">Backend API required for real inventory data</p>
                <p class="text-sm text-gray-400">Database schema and sample data available in SQL scripts</p>
            </div>
        </td></tr>
    `;
}

async function fetchMaterialInfo() {
    const materialInfoTableBody = document.getElementById('materialInfoTableBody');
    materialInfoTableBody.innerHTML = `
        <tr><td colspan="8" class="text-center py-8">
            <div class="flex flex-col items-center">
                <i class="fas fa-box-open text-4xl text-gray-400 mb-4"></i>
                <h3 class="text-lg font-semibold text-gray-600 mb-2">Demo Mode - Material Information</h3>
                <p class="text-gray-500 mb-2">Sample materials available in database setup</p>
                <p class="text-sm text-gray-400">Includes fiber cables, connectors, and equipment</p>
            </div>
        </td></tr>
    `;
}

async function fetchServiceInfo() {
    const serviceInfoTableBody = document.getElementById('serviceInfoTableBody');
    serviceInfoTableBody.innerHTML = `
        <tr><td colspan="8" class="text-center py-8">
            <div class="flex flex-col items-center">
                <i class="fas fa-tools text-4xl text-gray-400 mb-4"></i>
                <h3 class="text-lg font-semibold text-gray-600 mb-2">Demo Mode - Service Information</h3>
                <p class="text-gray-500 mb-2">Sample services available in database setup</p>
                <p class="text-sm text-gray-400">Includes installation, testing, and maintenance services</p>
            </div>
        </td></tr>
    `;
}

async function fetchUsers() {
    const usersTableBody = document.getElementById('usersTableBody');
    usersTableBody.innerHTML = `
        <tr><td colspan="4" class="text-center py-8">
            <div class="flex flex-col items-center">
                <i class="fas fa-users-cog text-4xl text-gray-400 mb-4"></i>
                <h3 class="text-lg font-semibold text-gray-600 mb-2">Demo Mode - User Management</h3>
                <p class="text-gray-500 mb-2">Backend API required for user management</p>
                <p class="text-sm text-gray-400">Database includes admin user and role-based access</p>
            </div>
        </td></tr>
    `;
}

// --- Initialize the Application ---
document.addEventListener('DOMContentLoaded', () => {
    checkAuth(); // Check authentication status on page load

    // Initialize map for the add form
    addMapInstance = initMap('map', 'locationLat', 'locationLong');

    // Set current datetime for raised_time if the field exists
    const raisedTimeInput = document.getElementById('raisedTime');
    if (raisedTimeInput) {
        const now = new Date();
        // Convert to local datetime string in format YYYY-MM-DDTHH:MM
        const localDatetime = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
        raisedTimeInput.value = localDatetime;
    }

    // Set current datetime for cleared_time if the field exists
    const clearedTimeInput = document.getElementById('clearedTime');
    if (clearedTimeInput) {
        clearedTimeInput.min = raisedTimeInput.value; // Set min to raised time
    }

    // Update cleared_time min when raised_time changes
    if (raisedTimeInput && clearedTimeInput) {
        raisedTimeInput.addEventListener('change', () => {
            clearedTimeInput.min = raisedTimeInput.value;
        });
    }

    // Navigation dropdown toggle functionality
    document.querySelectorAll('.nav-dropdown-toggle').forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = toggle.dataset.target;
            const dropdown = document.getElementById(targetId);
            dropdown.classList.toggle('hidden');

            // Toggle active class on the toggle button
            toggle.classList.toggle('active');

            // Close other dropdowns when opening a new one
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                if (menu.id !== targetId && !menu.classList.contains('hidden')) {
                    menu.classList.add('hidden');
                    // Remove active class from other toggles
                    const otherToggle = document.querySelector(`.nav-dropdown-toggle[data-target="${menu.id}"]`);
                    if (otherToggle) otherToggle.classList.remove('active');
                }
            });
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.nav-item')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.classList.add('hidden');
            });
            document.querySelectorAll('.nav-dropdown-toggle').forEach(toggle => {
                toggle.classList.remove('active');
            });
        }
    });

    // Navigation link click handlers
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            if (link.classList.contains('disabled-link')) {
                e.preventDefault();
                return;
            }

            // Handle navigation based on link ID
            const linkId = link.id;
            if (linkId === 'navFiberReports') {
                document.querySelector('.tab-button[data-tab="faultReports"]').click();
            } else if (linkId === 'navMaterialInventory') {
                document.querySelector('.tab-button[data-tab="materialInventory"]').click();
            } else if (linkId === 'navMaterialInfo') {
                document.querySelector('.tab-button[data-tab="materialInfo"]').click();
            } else if (linkId === 'navServiceInfo') {
                document.querySelector('.tab-button[data-tab="serviceInfo"]').click();
            }
        });
    });
});

// Mock form submission to show functionality
document.getElementById('reportForm').addEventListener('submit', (e) => {
    e.preventDefault();
    showMessage('✅ Fault report would be saved to database (Demo Mode - Connect backend to enable)', 'success');
});

document.getElementById('materialInfoForm').addEventListener('submit', (e) => {
    e.preventDefault();
    showMessage('✅ Material information would be saved to database (Demo Mode - Connect backend to enable)', 'success');
    e.target.reset();
});

document.getElementById('serviceInfoForm').addEventListener('submit', (e) => {
    e.preventDefault();
    showMessage('✅ Service information would be saved to database (Demo Mode - Connect backend to enable)', 'success');
    e.target.reset();
});

document.getElementById('userForm').addEventListener('submit', (e) => {
    e.preventDefault();
    showMessage('✅ User account would be created/updated (Demo Mode - Connect backend to enable)', 'success');
    e.target.reset();
});
