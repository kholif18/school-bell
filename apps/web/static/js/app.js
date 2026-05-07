// =========================================================
// SCHOOL BELL DASHBOARD - SPLIT PANEL VERSION
// =========================================================

// =========================================================
// API SERVICES
// =========================================================

const API = {
    async request(url, options = {}) {
        try {
            const response = await fetch(url, options);
            const result = await response.json();
            if (!result.ok) {
                throw new Error(result.error || 'Request failed');
            }
            return result;
        } catch (error) {
            console.error(`API Error [${url}]:`, error);
            throw error;
        }
    },

    profiles: {
        getAll: () => API.request('/api/profiles'),
        create: (name, description = '', color = '#4CAF50') =>
            API.request('/api/profiles', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name,
                    description,
                    color
                })
            }),
        update: (id, data) =>
            API.request(`/api/profiles/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            }),
        delete: (id) => API.request(`/api/profiles/${id}`, {
            method: 'DELETE'
        }),
        activate: (id) => API.request(`/api/profiles/${id}/activate`, {
            method: 'POST'
        })
    },

    schedules: {
        getAll: (profileId = null) => {
            const url = profileId ? `/api/schedules?profile_id=${profileId}` : '/api/schedules';
            return API.request(url);
        },
        create: (data) =>
            API.request('/api/schedules', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            }),
        update: (id, data) =>
            API.request(`/api/schedules/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            }),
        delete: (id) => API.request(`/api/schedules/${id}`, {
            method: 'DELETE'
        }),
        toggle: (id) => API.request(`/api/schedules/${id}/toggle`, {
            method: 'POST'
        }),
        getAudioFiles: () => API.request('/api/schedules/audio-files')
    },

    system: {
        start: () => API.request('/api/start', {
            method: 'POST'
        }),
        stop: () => API.request('/api/stop', {
            method: 'POST'
        }),
        reload: () => API.request('/api/reload', {
            method: 'POST'
        }),
        testBell: (audioFile = null) =>
            API.request('/api/test-bell', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    audio_file: audioFile
                })
            }),
        getStatus: () => API.request('/api/status'),
        getHistory: (limit = 100) => API.request(`/api/history?limit=${limit}`)
    }
};

// =========================================================
// GLOBAL VARIABLES
// =========================================================

let currentSelectedProfile = null;
let currentSchedules = [];

// =========================================================
// MODAL MANAGER
// =========================================================

class ModalManager {
    static showProfileDialog(profile = null) {
        const isEdit = profile !== null;
        const title = isEdit ? 'Edit Profile' : 'New Profile';

        const modal = this.createModal(title, `
            <div class="form-group">
                <label>Profile Name *</label>
                <input type="text" id="profileName" value="${this.escapeHtml(profile && profile.name || '')}" placeholder="e.g., Sekolah Pagi">
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea id="profileDesc" rows="3" placeholder="Optional description">${this.escapeHtml(profile && profile.description || '')}</textarea>
            </div>
            <div class="form-group">
                <label>Color</label>
                <input type="color" id="profileColor" value="${profile && profile.color || '#4CAF50'}">
            </div>
        `, 'saveProfileBtn');

        const saveBtn = modal.querySelector('#saveProfileBtn');
        if (saveBtn) {
            saveBtn.onclick = async () => {
                const name = modal.querySelector('#profileName').value.trim();
                if (!name) {
                    alert('Profile name required');
                    return;
                }

                const data = {
                    name: name,
                    description: modal.querySelector('#profileDesc').value,
                    color: modal.querySelector('#profileColor').value
                };

                try {
                    const result = isEdit ?
                        await API.profiles.update(profile.id, data) :
                        await API.profiles.create(data.name, data.description, data.color);

                    if (result.ok) {
                        modal.remove();
                        await loadProfiles();
                        dashboard.showToast(isEdit ? 'Profile updated!' : 'Profile created!', 'success');
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            };
        }
    }

    static async showScheduleDialog(schedule = null) {
        const isEdit = schedule !== null;
        const title = isEdit ? 'Edit Schedule' : 'New Schedule';
        const dayNames = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'];

        if (!isEdit && !currentSelectedProfile) {
            dashboard.showToast('Please select a profile first', 'warning');
            return;
        }

        // Get audio files
        let audioFiles = [];
        try {
            const result = await API.schedules.getAudioFiles();
            if (result.ok && result.data) {
                audioFiles = result.data;
            }
        } catch (error) {
            console.error('Error loading audio files:', error);
        }

        const daysCheckboxes = dayNames.map((day, idx) => `
            <label class="day-checkbox">
                <input type="checkbox" value="${idx}" ${schedule && schedule.days_list && schedule.days_list.includes(idx) ? 'checked' : ''}>
                <span>${day}</span>
            </label>
        `).join('');

        const audioOptions = audioFiles.map(file => `
            <option value="${this.escapeHtml(file.path)}" ${schedule && schedule.audio_file === file.path ? 'selected' : ''}>
                ${this.escapeHtml(file.name)}
            </option>
        `).join('');

        const modal = this.createModal(title, `
            <div class="form-group">
                <label>Schedule Name *</label>
                <input type="text" id="scheduleName" value="${this.escapeHtml(schedule && schedule.name || '')}" placeholder="e.g., Bel Masuk">
            </div>
            <div class="form-group">
                <label>Time</label>
                <input type="time" id="scheduleTime" value="${schedule && schedule.bell_time || '07:00'}">
            </div>
            <div class="form-group">
                <label>Days</label>
                <div class="days-checkboxes" id="daysCheckboxes">${daysCheckboxes}</div>
            </div>
            <div class="form-group">
                <label>Audio File (Optional)</label>
                <select id="scheduleAudio" class="audio-select">
                    <option value="">🔔 Default Bell</option>
                    ${audioOptions}
                </select>
                <small>Select audio file from assets/audio directory</small>
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox" id="scheduleActive" ${schedule && schedule.is_active !== false ? 'checked' : 'checked'}>
                    Active
                </label>
            </div>
            ${!isEdit ? `<input type="hidden" id="profileId" value="${currentSelectedProfile.id}">` : ''}
        `, 'saveScheduleBtn');

        const saveBtn = modal.querySelector('#saveScheduleBtn');
        if (saveBtn) {
            saveBtn.onclick = async () => {
                const name = modal.querySelector('#scheduleName').value.trim();
                if (!name) {
                    alert('Schedule name required');
                    return;
                }

                const timeValue = modal.querySelector('#scheduleTime').value;
                const [hour, minute] = timeValue.split(':').map(Number);
                const days = Array.from(modal.querySelectorAll('#daysCheckboxes input:checked'))
                    .map(cb => parseInt(cb.value));

                const data = {
                    name: name,
                    hour: hour,
                    minute: minute,
                    days: days.length ? days : [0, 1, 2, 3, 4, 5],
                    audio_file: modal.querySelector('#scheduleAudio').value || null,
                    is_active: modal.querySelector('#scheduleActive').checked
                };

                if (!isEdit) {
                    data.profile_id = currentSelectedProfile.id;
                }

                try {
                    const result = isEdit ?
                        await API.schedules.update(schedule.id, data) :
                        await API.schedules.create(data);

                    if (result.ok) {
                        modal.remove();
                        await loadSchedules(currentSelectedProfile.id);
                        dashboard.showToast(isEdit ? 'Schedule updated!' : 'Schedule created!', 'success');
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            };
        }
    }

    static createModal(title, bodyHtml, saveButtonId = 'saveBtn') {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3>${this.escapeHtml(title)}</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">${bodyHtml}</div>
                <div class="modal-footer">
                    <button class="btn btn-secondary cancel-btn">Cancel</button>
                    <button class="btn btn-primary" id="${saveButtonId}">Save</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        const closeModal = () => modal.remove();
        const closeBtn = modal.querySelector('.modal-close');
        const cancelBtn = modal.querySelector('.cancel-btn');

        if (closeBtn) closeBtn.onclick = closeModal;
        if (cancelBtn) cancelBtn.onclick = closeModal;

        return modal;
    }

    static escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// =========================================================
// PROFILE FUNCTIONS
// =========================================================

async function loadProfiles() {
    try {
        const result = await API.profiles.getAll();
        const container = document.getElementById('profilesList');

        if (!container) return;

        if (result.ok && result.data && result.data.length > 0) {
            container.innerHTML = `
                <div class="profiles-list">
                    ${result.data.map(profile => `
                        <div class="profile-card ${currentSelectedProfile && currentSelectedProfile.id === profile.id ? 'selected' : ''}" 
                             data-profile-id="${profile.id}"
                             onclick="selectProfile(${profile.id})">
                            <div class="profile-card-header">
                                <div class="profile-color-dot" style="background: ${profile.color}"></div>
                                <div class="profile-name">${escapeHtml(profile.name)}</div>
                                <span class="profile-badge ${profile.is_active ? 'active' : 'inactive'}">
                                    ${profile.is_active ? 'ACTIVE' : 'INACTIVE'}
                                </span>
                            </div>
                            <div class="profile-stats">
                                📋 ${profile.schedule_count || 0} schedules
                            </div>
                            <div class="profile-actions">
                                ${!profile.is_active ? `
                                    <button onclick="event.stopPropagation(); activateProfile(${profile.id})" title="Activate">⭐ Activate</button>
                                ` : ''}
                                <button onclick="event.stopPropagation(); editProfile(${profile.id})" title="Edit">✏️</button>
                                <button onclick="event.stopPropagation(); deleteProfile(${profile.id})" title="Delete">🗑️</button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📁</div>
                    <h4>No Profiles</h4>
                    <p>Click + New to create a profile</p>
                </div>
            `;
        }

        // Auto-select first profile if none selected
        if (!currentSelectedProfile && result.data && result.data.length > 0) {
            await selectProfile(result.data[0].id);
        }

        // Update header with active profile
        await updateSystemStatus();

    } catch (error) {
        console.error('Error loading profiles:', error);
    }
}

async function selectProfile(profileId) {
    try {
        const result = await API.profiles.getAll();
        if (result.ok && result.data) {
            const profile = result.data.find(p => p.id === profileId);
            if (profile) {
                currentSelectedProfile = profile;
                await loadSchedules(profileId);
                await loadProfiles(); // Refresh to update selection highlight

                // Update panel title and warning
                const titleEl = document.getElementById('schedulesPanelTitle');
                const warningEl = document.getElementById('profileStatusWarning');

                if (titleEl) {
                    titleEl.innerHTML = `📋 SCHEDULES: ${escapeHtml(profile.name)}`;
                }

                if (warningEl) {
                    if (profile.is_active) {
                        warningEl.style.display = 'none';
                    } else {
                        warningEl.style.display = 'block';
                        warningEl.innerHTML = '⚠️ Profile INACTIVE - Schedules will NOT run';
                    }
                }
            }
        }
    } catch (error) {
        console.error('Error selecting profile:', error);
    }
}

async function activateProfile(profileId) {
    if (confirm('Activate this profile? All schedules will be reloaded.')) {
        try {
            await API.profiles.activate(profileId);
            await loadProfiles();
            if (currentSelectedProfile && currentSelectedProfile.id === profileId) {
                await selectProfile(profileId);
            }
            dashboard.showToast('Profile activated!', 'success');
        } catch (error) {
            dashboard.showToast('Error: ' + error.message, 'danger');
        }
    }
}

async function editProfile(profileId) {
    const result = await API.profiles.getAll();
    if (result.ok && result.data) {
        const profile = result.data.find(p => p.id === profileId);
        if (profile) {
            ModalManager.showProfileDialog(profile);
        }
    }
}

async function deleteProfile(profileId) {
    if (confirm('Delete this profile? All schedules in this profile will also be deleted!')) {
        try {
            await API.profiles.delete(profileId);
            if (currentSelectedProfile && currentSelectedProfile.id === profileId) {
                currentSelectedProfile = null;
                const schedulesContainer = document.getElementById('schedulesContainer');
                if (schedulesContainer) {
                    schedulesContainer.innerHTML = `
                        <div class="empty-state">
                            <div class="empty-icon">📅</div>
                            <h4>No schedules</h4>
                            <p>Select a profile or create a new schedule</p>
                        </div>
                    `;
                }
            }
            await loadProfiles();
            dashboard.showToast('Profile deleted!', 'warning');
        } catch (error) {
            dashboard.showToast('Error: ' + error.message, 'danger');
        }
    }
}

// =========================================================
// SCHEDULE FUNCTIONS
// =========================================================

async function loadSchedules(profileId) {
    if (!profileId) return;

    try {
        const result = await API.schedules.getAll(profileId);
        const container = document.getElementById('schedulesContainer');

        if (!container) return;

        if (result.ok && result.data && result.data.length > 0) {
            currentSchedules = result.data;
            renderSchedulesTable(currentSchedules);
        } else {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📅</div>
                    <h4>No schedules</h4>
                    <p>Click + Add Schedule to create one</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading schedules:', error);
        const container = document.getElementById('schedulesContainer');
        if (container) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">⚠️</div>
                    <h4>Error loading schedules</h4>
                    <p>Please try again</p>
                </div>
            `;
        }
    }
}

function renderSchedulesTable(schedules) {
    const container = document.getElementById('schedulesContainer');
    if (!container) return;

    const searchTerm = document.getElementById('scheduleSearch') ? .value.toLowerCase() || '';
    const statusFilter = document.getElementById('scheduleStatusFilter') ? .value || 'all';

    let filteredSchedules = [...schedules];

    // Apply search filter
    if (searchTerm) {
        filteredSchedules = filteredSchedules.filter(s =>
            s.name.toLowerCase().includes(searchTerm)
        );
    }

    // Apply status filter
    if (statusFilter === 'active') {
        filteredSchedules = filteredSchedules.filter(s => s.is_active);
    } else if (statusFilter === 'inactive') {
        filteredSchedules = filteredSchedules.filter(s => !s.is_active);
    }

    if (filteredSchedules.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🔍</div>
                <h4>No matching schedules</h4>
                <p>Try changing your search or filter</p>
            </div>
        `;
        return;
    }

    const dayNames = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'];

    container.innerHTML = `
        <table class="schedules-table">
            <thead>
                <tr>
                    <th>Nama</th>
                    <th>Jam</th>
                    <th>Hari</th>
                    <th>Status</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                ${filteredSchedules.map(schedule => `
                    <tr class="${!schedule.is_active ? 'inactive-row' : ''}">
                        <td>${escapeHtml(schedule.name)}</td>
                        <td><strong>${schedule.bell_time}</strong></td>
                        <td>${formatDays(schedule.days_list, dayNames)}</td>
                        <td>
                            <span class="badge ${schedule.is_active ? 'badge-success' : 'badge-danger'}">
                                ${schedule.is_active ? 'Active' : 'Inactive'}
                            </span>
                        </td>
                        <td>
                            <div class="action-buttons">
                                <button class="btn-icon" onclick="toggleSchedule(${schedule.id}, ${!schedule.is_active})" title="${schedule.is_active ? 'Disable' : 'Enable'}">
                                    ${schedule.is_active ? '🔘' : '⚪'}
                                </button>
                                <button class="btn-icon" onclick="editSchedule(${schedule.id})" title="Edit">✏️</button>
                                <button class="btn-icon" onclick="deleteSchedule(${schedule.id})" title="Delete">🗑️</button>
                            </div>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function formatDays(daysList, dayNames) {
    if (!daysList || daysList.length === 0) return 'None';
    if (daysList.length === 7) return 'Everyday';
    return daysList.map(d => dayNames[d]).join(', ');
}

async function editSchedule(scheduleId) {
    try {
        const result = await API.schedules.getAll(currentSelectedProfile ? .id);
        if (result.ok && result.data) {
            const schedule = result.data.find(s => s.id === scheduleId);
            if (schedule) {
                ModalManager.showScheduleDialog(schedule);
            }
        }
    } catch (error) {
        dashboard.showToast('Error loading schedule: ' + error.message, 'danger');
    }
}

async function deleteSchedule(scheduleId) {
    if (confirm('Delete this schedule?')) {
        try {
            await API.schedules.delete(scheduleId);
            await loadSchedules(currentSelectedProfile ? .id);
            dashboard.showToast('Schedule deleted!', 'warning');
        } catch (error) {
            dashboard.showToast('Error: ' + error.message, 'danger');
        }
    }
}

async function toggleSchedule(scheduleId, newStatus) {
    try {
        await API.schedules.toggle(scheduleId);
        await loadSchedules(currentSelectedProfile ? .id);
        dashboard.showToast('Schedule ' + (newStatus ? 'enabled' : 'disabled') + '!', 'info');
    } catch (error) {
        dashboard.showToast('Error: ' + error.message, 'danger');
    }
}

// =========================================================
// SYSTEM FUNCTIONS
// =========================================================

async function updateSystemStatus() {
    try {
        const result = await API.system.getStatus();
        if (result.ok) {
            const statusElement = document.getElementById('systemStatus');
            if (statusElement) {
                const dot = statusElement.querySelector('.status-dot');
                const text = statusElement.querySelector('.status-text');

                if (result.data.running) {
                    if (dot) dot.classList.add('running');
                    if (text) text.textContent = 'System Running';
                } else {
                    if (dot) dot.classList.remove('running');
                    if (text) text.textContent = 'System Stopped';
                }
            }

            // Update header active profile
            const profileName = result.data.active_profile_name || 'No Profile';
            const profileBadge = document.getElementById('profileHeaderBadge');
            if (profileBadge) {
                profileBadge.textContent = profileName;
            }
        }
    } catch (error) {
        console.error('Error updating system status:', error);
    }
}

function updateDateTime() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('id-ID');
    const dateStr = now.toLocaleDateString('id-ID', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    const timeEl = document.getElementById('currentTime');
    const dateEl = document.getElementById('currentDate');

    if (timeEl) timeEl.textContent = timeStr;
    if (dateEl) dateEl.textContent = dateStr;
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// =========================================================
// SYSTEM CONTROL
// =========================================================

const systemControl = {
    start: async () => {
        try {
            await API.system.start();
            await updateSystemStatus();
            dashboard.showToast('System started!', 'success');
        } catch (error) {
            dashboard.showToast('Error starting system: ' + error.message, 'danger');
        }
    },

    stop: async () => {
        try {
            await API.system.stop();
            await updateSystemStatus();
            dashboard.showToast('System stopped!', 'warning');
        } catch (error) {
            dashboard.showToast('Error stopping system: ' + error.message, 'danger');
        }
    },

    testBell: async () => {
        try {
            await API.system.testBell();
            dashboard.showToast('Test bell triggered!', 'success');
        } catch (error) {
            dashboard.showToast('Error testing bell: ' + error.message, 'danger');
        }
    },

    reload: async () => {
        try {
            await API.system.reload();
            await loadSchedules(currentSelectedProfile ? .id);
            dashboard.showToast('System reloaded!', 'success');
        } catch (error) {
            dashboard.showToast('Error reloading system: ' + error.message, 'danger');
        }
    }
};

// =========================================================
// DASHBOARD CLASS
// =========================================================

class SchoolBellDashboard {
    constructor() {
        this.refreshInterval = null;
        this.init();
    }

    async init() {
        await loadProfiles();
        await updateSystemStatus();
        this.startAutoRefresh();
        this.bindEvents();
        this.updateDateTime();
        setInterval(() => this.updateDateTime(), 1000);
    }

    bindEvents() {
        const searchInput = document.getElementById('scheduleSearch');
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                if (currentSchedules.length > 0) {
                    renderSchedulesTable(currentSchedules);
                }
            });
        }

        const statusFilter = document.getElementById('scheduleStatusFilter');
        if (statusFilter) {
            statusFilter.addEventListener('change', () => {
                if (currentSchedules.length > 0) {
                    renderSchedulesTable(currentSchedules);
                }
            });
        }
    }

    startAutoRefresh() {
        if (this.refreshInterval) clearInterval(this.refreshInterval);
        this.refreshInterval = setInterval(() => {
            if (currentSelectedProfile) {
                loadSchedules(currentSelectedProfile.id);
            }
            updateSystemStatus();
        }, 5000);
    }

    updateDateTime() {
        updateDateTime();
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// =========================================================
// INITIALIZATION
// =========================================================

let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new SchoolBellDashboard();
});

// Make functions globally available
window.selectProfile = selectProfile;
window.activateProfile = activateProfile;
window.editProfile = editProfile;
window.deleteProfile = deleteProfile;
window.editSchedule = editSchedule;
window.deleteSchedule = deleteSchedule;
window.toggleSchedule = toggleSchedule;
window.systemControl = systemControl;
window.ModalManager = ModalManager;