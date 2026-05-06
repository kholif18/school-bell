// =========================================================
// SCHOOL BELL DASHBOARD - MAIN APPLICATION
// =========================================================

// =========================================================
// API SERVICES
// =========================================================

const API = {
    // Generic fetch wrapper
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

    // Profile APIs
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

    // Schedule APIs
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
        })
    },

    // System APIs
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
// UI COMPONENTS
// =========================================================

class ModalManager {
    static showProfileDialog(profile = null) {
        const isEdit = profile !== null;
        const title = isEdit ? 'Edit Profile' : 'New Profile';

        const modal = this.createModal(title, `
            <div class="form-group">
                <label>Profile Name *</label>
                <input type="text" id="profileName" value="${this.escapeHtml(profile?.name || '')}" placeholder="e.g., Sekolah Pagi">
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea id="profileDesc" rows="3" placeholder="Optional description">${this.escapeHtml(profile?.description || '')}</textarea>
            </div>
            <div class="form-group">
                <label>Color</label>
                <input type="color" id="profileColor" value="${profile?.color || '#4CAF50'}">
            </div>
        `);

        modal.querySelector('#saveProfileBtn').onclick = async () => {
            const name = modal.querySelector('#profileName').value.trim();
            if (!name) {
                this.showAlert('Profile name required');
                return;
            }

            const data = {
                name,
                description: modal.querySelector('#profileDesc').value,
                color: modal.querySelector('#profileColor').value
            };

            try {
                const result = isEdit ?
                    await API.profiles.update(profile.id, data) :
                    await API.profiles.create(data.name, data.description, data.color);

                if (result.ok) {
                    modal.remove();
                    dashboard.loadProfiles();
                    dashboard.showToast(isEdit ? 'Profile updated!' : 'Profile created!', 'success');
                }
            } catch (error) {
                this.showAlert('Error: ' + error.message);
            }
        };
    }

    static showScheduleDialog(schedule = null, profileId = null) {
        const isEdit = schedule !== null;
        const title = isEdit ? 'Edit Schedule' : 'New Schedule';
        const dayNames = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'];

        const daysCheckboxes = dayNames.map((day, idx) => `
            <label class="day-checkbox">
                <input type="checkbox" value="${idx}" ${schedule?.days_list?.includes(idx) ? 'checked' : ''}>
                <span>${day}</span>
            </label>
        `).join('');

        const modal = this.createModal(title, `
            <div class="form-group">
                <label>Schedule Name *</label>
                <input type="text" id="scheduleName" value="${this.escapeHtml(schedule?.name || '')}" placeholder="e.g., Bel Masuk">
            </div>
            <div class="form-group">
                <label>Time</label>
                <input type="time" id="scheduleTime" value="${schedule?.bell_time || '07:00'}">
            </div>
            <div class="form-group">
                <label>Days</label>
                <div class="days-checkboxes" id="daysCheckboxes">${daysCheckboxes}</div>
            </div>
            <div class="form-group">
                <label>Audio File (Optional)</label>
                <input type="text" id="scheduleAudio" value="${this.escapeHtml(schedule?.audio_file || '')}" placeholder="path/to/audio.mp3">
                <small>Leave empty for default bell</small>
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox" id="scheduleActive" ${schedule?.is_active !== false ? 'checked' : ''}>
                    Active
                </label>
            </div>
        `);

        modal.querySelector('#saveScheduleBtn').onclick = async () => {
            const name = modal.querySelector('#scheduleName').value.trim();
            if (!name) {
                this.showAlert('Schedule name required');
                return;
            }

            const timeValue = modal.querySelector('#scheduleTime').value;
            const [hour, minute] = timeValue.split(':').map(Number);
            const days = Array.from(modal.querySelectorAll('#daysCheckboxes input:checked'))
                .map(cb => parseInt(cb.value));

            const data = {
                name,
                hour,
                minute,
                days,
                audio_file: modal.querySelector('#scheduleAudio').value || null,
                is_active: modal.querySelector('#scheduleActive').checked
            };

            if (!isEdit && profileId) {
                data.profile_id = profileId;
            }

            try {
                const result = isEdit ?
                    await API.schedules.update(schedule.id, data) :
                    await API.schedules.create(data);

                if (result.ok) {
                    modal.remove();
                    dashboard.loadSchedules();
                    dashboard.loadStatus();
                    dashboard.showToast(isEdit ? 'Schedule updated!' : 'Schedule created!', 'success');
                }
            } catch (error) {
                this.showAlert('Error: ' + error.message);
            }
        };
    }

    static createModal(title, bodyHtml) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">${bodyHtml}</div>
                <div class="modal-footer">
                    <button class="btn btn-secondary cancel-btn">Cancel</button>
                    <button class="btn btn-primary" id="saveProfileBtn">Save</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        const closeModal = () => modal.remove();
        modal.querySelector('.modal-close').onclick = closeModal;
        modal.querySelector('.cancel-btn').onclick = closeModal;

        return modal;
    }

    static escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    static showAlert(message) {
        alert(message);
    }
}

// =========================================================
// DASHBOARD CLASS
// =========================================================

class SchoolBellDashboard {
    constructor() {
        this.refreshInterval = null;
        this.dayNames = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'];
        this.init();
    }

    init() {
        this.loadStatus();
        this.startAutoRefresh();
        this.bindEvents();
        this.updateDateTime();
        setInterval(() => this.updateDateTime(), 1000);
    }

    bindEvents() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchPage(item.dataset.page);
            });
        });

        // Refresh interval change
        const intervalInput = document.getElementById('refreshInterval');
        if (intervalInput) {
            intervalInput.addEventListener('change', () => this.restartAutoRefresh());
        }
    }

    switchPage(page) {
        this.currentPage = page;

        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.page === page);
        });

        document.querySelectorAll('.page').forEach(p => {
            p.classList.toggle('active', p.id === `${page}Page`);
        });

        const titles = {
            dashboard: {
                title: 'Dashboard',
                subtitle: 'Overview sistem sekolah'
            },
            schedules: {
                title: 'Jadwal Bel',
                subtitle: 'Kelola jadwal bel sekolah'
            },
            profiles: {
                title: 'Profiles',
                subtitle: 'Kelola profile jadwal'
            },
            history: {
                title: 'Riwayat',
                subtitle: 'Log bel yang telah berbunyi'
            },
            settings: {
                title: 'Settings',
                subtitle: 'Pengaturan sistem'
            }
        };

        const titleInfo = titles[page] || titles.dashboard;
        document.getElementById('pageTitle').textContent = titleInfo.title;
        document.getElementById('pageSubtitle').textContent = titleInfo.subtitle;

        this.loadPageData(page);
    }

    async loadPageData(page) {
        const loaders = {
            schedules: () => this.loadSchedules(),
            profiles: () => this.loadProfiles(),
            history: () => this.loadHistory()
        };

        if (loaders[page]) {
            await loaders[page]();
        }
    }

    async loadStatus() {
        try {
            const result = await API.system.getStatus();
            if (result.ok) {
                this.updateDashboard(result.data);
                this.updateSystemStatus(result.data.running);
            }
        } catch (error) {
            console.error('Error loading status:', error);
        }
    }

    updateDashboard(data) {
        // Update stats
        document.getElementById('totalSchedules').textContent = data.active_jobs || 0;
        document.getElementById('activeSchedules').textContent = data.active_jobs || 0;
        document.getElementById('activeProfile').textContent = data.active_profile_name || '-';

        // Update next bell
        if (data.next_bell) {
            const nextTime = new Date(data.next_bell);
            const timeStr = nextTime.toLocaleTimeString('id-ID', {
                hour: '2-digit',
                minute: '2-digit'
            });
            document.getElementById('nextBellTime').textContent = timeStr;
            document.getElementById('nextBellLarge').textContent = timeStr;
            document.getElementById('nextBellName').textContent = data.next_bell_name || 'Bell';

            // Update countdown
            const now = new Date();
            const diff = Math.floor((nextTime - now) / 1000);
            if (diff > 0) {
                const hours = Math.floor(diff / 3600);
                const minutes = Math.floor((diff % 3600) / 60);
                const seconds = diff % 60;
                let countdownText = '';
                if (hours > 0) countdownText = `${hours}h ${minutes}m`;
                else if (minutes > 0) countdownText = `${minutes}m ${seconds}s`;
                else countdownText = `${seconds}s`;
                document.getElementById('countdown').textContent = countdownText;
            } else {
                document.getElementById('countdown').textContent = 'Now!';
            }
        } else {
            document.getElementById('nextBellTime').textContent = '--:--';
            document.getElementById('nextBellLarge').textContent = '--:--';
            document.getElementById('nextBellName').textContent = 'No schedule';
            document.getElementById('countdown').textContent = '-';
        }
    }

    updateSystemStatus(running) {
        const statusElement = document.getElementById('systemStatus');
        const dot = statusElement.querySelector('.status-dot');
        const text = statusElement.querySelector('.status-text');

        if (running) {
            dot.classList.add('running');
            text.textContent = 'System Running';
        } else {
            dot.classList.remove('running');
            text.textContent = 'System Stopped';
        }
    }

    async loadProfiles() {
        try {
            const result = await API.profiles.getAll();
            const tbody = document.getElementById('profilesBody');

            if (result.ok && result.data?.length) {
                tbody.innerHTML = result.data.map(profile => `
                    <tr class="${profile.is_active ? 'active-profile' : ''}">
                        <td>
                            <span class="profile-color" style="background: ${profile.color}"></span>
                            ${this.escapeHtml(profile.name)}
                            ${profile.is_active ? '<span class="badge badge-success ml-2">ACTIVE</span>' : ''}
                        </td>
                        <td>${this.escapeHtml(profile.description || '-')}</td>
                        <td>${profile.schedule_count || 0}</td>
                        <td>
                            <div class="action-buttons">
                                ${!profile.is_active ? `
                                    <button class="btn-icon btn-activate" onclick="dashboard.activateProfile(${profile.id})" title="Activate">✅</button>
                                ` : ''}
                                <button class="btn-icon btn-edit" onclick="dashboard.editProfile(${profile.id})" title="Edit">✏️</button>
                                <button class="btn-icon btn-delete" onclick="dashboard.deleteProfile(${profile.id})" title="Delete">🗑️</button>
                            </div>
                        </td>
                    </tr>
                `).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="4" class="text-center">No profiles found. Click + New Profile to create one.</td></tr>';
            }
        } catch (error) {
            console.error('Error loading profiles:', error);
        }
    }

    async loadSchedules() {
        try {
            const result = await API.schedules.getAll();
            const tbody = document.getElementById('schedulesBody');

            if (result.ok && result.data?.length) {
                tbody.innerHTML = result.data.map(schedule => `
                    <tr>
                        <td>${this.escapeHtml(schedule.name)}</td>
                        <td><strong>${schedule.bell_time}</strong></td>
                        <td>${this.formatDays(schedule.days_list)}</td>
                        <td>
                            <span class="badge ${schedule.is_active ? 'badge-success' : 'badge-danger'}">
                                ${schedule.is_active ? 'Active' : 'Inactive'}
                            </span>
                        </td>
                        <td>
                            <div class="action-buttons">
                                <button class="btn-icon btn-toggle" onclick="dashboard.toggleSchedule(${schedule.id}, ${!schedule.is_active})" title="${schedule.is_active ? 'Disable' : 'Enable'}">
                                    ${schedule.is_active ? '🔘' : '⚪'}
                                </button>
                                <button class="btn-icon btn-edit" onclick="dashboard.editSchedule(${schedule.id})" title="Edit">✏️</button>
                                <button class="btn-icon btn-delete" onclick="dashboard.deleteSchedule(${schedule.id})" title="Delete">🗑️</button>
                            </div>
                        </td>
                    </tr>
                `).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">No schedules found. Click + Add Schedule to create one.</td></tr>';
            }
        } catch (error) {
            console.error('Error loading schedules:', error);
        }
    }

    async loadHistory() {
        try {
            const result = await API.system.getHistory(50);
            const tbody = document.getElementById('historyBody');

            if (result.ok && result.data?.length) {
                tbody.innerHTML = result.data.map(history => `
                    <tr>
                        <td>${new Date(history.rang_at).toLocaleString('id-ID')}</td>
                        <td>${this.escapeHtml(history.schedule_name || '-')}</td>
                        <td>${this.escapeHtml(history.profile_name || '-')}</td>
                        <td><span class="badge badge-success">${history.status || 'Success'}</span></td>
                    </tr>
                `).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="4" class="text-center">No history found</td></tr>';
            }
        } catch (error) {
            console.error('Error loading history:', error);
        }
    }

    formatDays(daysList) {
        if (!daysList?.length) return 'None';
        if (daysList.length === 7) return 'Everyday';
        return daysList.map(d => this.dayNames[d]).join(', ');
    }

    async activateProfile(profileId) {
        if (confirm('Activate this profile? All schedules will be reloaded.')) {
            try {
                await API.profiles.activate(profileId);
                await this.loadProfiles();
                await this.loadStatus();
                this.showToast('Profile activated!', 'success');
            } catch (error) {
                this.showToast('Error: ' + error.message, 'danger');
            }
        }
    }

    async editProfile(profileId) {
        try {
            const result = await API.profiles.getAll();
            const profile = result.data?.find(p => p.id === profileId);
            if (profile) {
                ModalManager.showProfileDialog(profile);
            }
        } catch (error) {
            this.showToast('Error loading profile: ' + error.message, 'danger');
        }
    }

    async deleteProfile(profileId) {
        if (confirm('Delete this profile? All schedules in this profile will also be deleted!')) {
            try {
                await API.profiles.delete(profileId);
                await this.loadProfiles();
                await this.loadStatus();
                this.showToast('Profile deleted!', 'warning');
            } catch (error) {
                this.showToast('Error: ' + error.message, 'danger');
            }
        }
    }

    async editSchedule(scheduleId) {
        try {
            const result = await API.schedules.getAll();
            const schedule = result.data?.find(s => s.id === scheduleId);
            if (schedule) {
                ModalManager.showScheduleDialog(schedule);
            }
        } catch (error) {
            this.showToast('Error loading schedule: ' + error.message, 'danger');
        }
    }

    async deleteSchedule(scheduleId) {
        if (confirm('Delete this schedule?')) {
            try {
                await API.schedules.delete(scheduleId);
                await this.loadSchedules();
                await this.loadStatus();
                this.showToast('Schedule deleted!', 'warning');
            } catch (error) {
                this.showToast('Error: ' + error.message, 'danger');
            }
        }
    }

    async toggleSchedule(scheduleId, newStatus) {
        try {
            await API.schedules.toggle(scheduleId);
            await this.loadSchedules();
            await this.loadStatus();
            this.showToast(`Schedule ${newStatus ? 'enabled' : 'disabled'}!`, 'info');
        } catch (error) {
            this.showToast('Error: ' + error.message, 'danger');
        }
    }

    updateDateTime() {
        const now = new Date();
        const timeStr = now.toLocaleTimeString('id-ID');
        const dateStr = now.toLocaleDateString('id-ID', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        document.getElementById('currentTime').textContent = timeStr;
        document.getElementById('currentDate').textContent = dateStr;
    }

    startAutoRefresh() {
        const interval = parseInt(document.getElementById('refreshInterval')?.value || 2) * 1000;
        if (this.refreshInterval) clearInterval(this.refreshInterval);
        this.refreshInterval = setInterval(() => this.loadStatus(), interval);
    }

    restartAutoRefresh() {
        this.startAutoRefresh();
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

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// =========================================================
// SYSTEM CONTROL
// =========================================================

const systemControl = {
    start: async () => {
        try {
            await API.system.start();
            dashboard.loadStatus();
        } catch (error) {
            dashboard.showToast('Error starting system: ' + error.message, 'danger');
        }
    },

    stop: async () => {
        try {
            await API.system.stop();
            dashboard.loadStatus();
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
            dashboard.loadStatus();
            dashboard.showToast('System reloaded!', 'success');
        } catch (error) {
            dashboard.showToast('Error reloading system: ' + error.message, 'danger');
        }
    }
};

// =========================================================
// INITIALIZATION
// =========================================================

let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new SchoolBellDashboard();
});