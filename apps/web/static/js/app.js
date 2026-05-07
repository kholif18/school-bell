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
            const text = await response.text();

            let result;

            try {
                result = JSON.parse(text);
            } catch (e) {
                console.error('Invalid JSON:', text);
                throw new Error('Server returned invalid JSON');
            }

            if (!result.ok) {
                throw new Error(result.error || 'Request failed');
            }
            return result;
        } catch (error) {
            console.error('API Error [' + url + ']:', error);
            throw error;
        }
    },

    profiles: {
        getAll: function () {
            return API.request('/api/profiles');
        },
        create: function (name, description, color) {
            description = description || '';
            color = color || '#4CAF50';
            return API.request('/api/profiles', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    description: description,
                    color: color
                })
            });
        },
        update: function (id, data) {
            return API.request('/api/profiles/' + id, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
        },
        delete: function (id) {
            return API.request('/api/profiles/' + id, {
                method: 'DELETE'
            });
        },
        activate: function (id) {
            return API.request('/api/profiles/' + id + '/activate', {
                method: 'POST'
            });
        }
    },

    schedules: {
        getAll: function (profileId) {
            var url = profileId ? '/api/schedules?profile_id=' + profileId : '/api/schedules';
            return API.request(url);
        },
        create: function (data) {
            return API.request('/api/schedules', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
        },
        update: function (id, data) {
            return API.request('/api/schedules/' + id, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
        },
        delete: function (id) {
            return API.request('/api/schedules/' + id, {
                method: 'DELETE'
            });
        },
        toggle: function (id) {
            return API.request('/api/schedules/' + id + '/toggle', {
                method: 'POST'
            });
        },
        getAudioFiles: function () {
            return API.request('/api/schedules/audio-files');
        }
    },

    system: {
        start: function () {
            return API.request('/api/start', {
                method: 'POST'
            });
        },
        stop: function () {
            return API.request('/api/stop', {
                method: 'POST'
            });
        },
        reload: function () {
            return API.request('/api/reload', {
                method: 'POST'
            });
        },
        testBell: function (audioFile) {
            audioFile = audioFile || null;
            return API.request('/api/test-bell', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    audio_file: audioFile
                })
            });
        },
        stopBell: function () {
            return API.request('/api/stop-bell', {
                method: 'POST'
            });
        },
        getStatus: function () {
            return API.request('/api/status');
        },
        getHistory: function (limit) {
            limit = limit || 100;
            return API.request('/api/history?limit=' + limit);
        }
    }
};

// =========================================================
// GLOBAL VARIABLES
// =========================================================

var currentSelectedProfile = null;
var currentSchedules = [];

// =========================================================
// HELPER FUNCTIONS
// =========================================================

function escapeHtml(text) {
    if (!text) return '';
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDays(daysList, dayNames) {
    if (!daysList || daysList.length === 0) return 'None';
    if (daysList.length === 7) return 'Everyday';
    var result = '';
    for (var i = 0; i < daysList.length; i++) {
        if (i > 0) result += ', ';
        result += dayNames[daysList[i]];
    }
    return result;
}

function showToast(message, type) {
    type = type || 'info';
    var toast = document.createElement('div');
    toast.className = 'toast toast-' + type;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(function () {
        toast.classList.add('show');
    }, 10);

    setTimeout(function () {
        toast.classList.remove('show');
        setTimeout(function () {
            toast.remove();
        }, 300);
    }, 3000);
}

// =========================================================
// PROFILE FUNCTIONS
// =========================================================

function loadProfiles() {
    API.profiles.getAll()
        .then(function (result) {
            var container = document.getElementById('profilesList');
            if (!container) return;

            if (result.ok && result.data && result.data.length > 0) {
                var html = '<div class="profiles-list">';
                for (var i = 0; i < result.data.length; i++) {
                    var profile = result.data[i];
                    var isSelected = currentSelectedProfile && currentSelectedProfile.id === profile.id;
                    html += '<div class="profile-card ' + (isSelected ? 'selected' : '') + '" data-profile-id="' + profile.id + '" onclick="selectProfile(' + profile.id + ')">';
                    html += '<div class="profile-card-header">';
                    html += '<div class="profile-color-dot" style="background: ' + profile.color + '"></div>';
                    html += '<div class="profile-name">' + escapeHtml(profile.name) + '</div>';
                    html += '<span class="profile-badge ' + (profile.is_active ? 'active' : 'inactive') + '">';
                    html += profile.is_active ? 'ACTIVE' : 'INACTIVE';
                    html += '</span>';
                    html += '</div>';
                    html += '<div class="profile-stats">📋 ' + (profile.schedule_count || 0) + ' schedules</div>';
                    html += '<div class="profile-actions">';
                    if (!profile.is_active) {
                        html += '<button onclick="event.stopPropagation(); activateProfile(' + profile.id + ')" title="Activate">⭐ Activate</button>';
                    }
                    html += '<button onclick="event.stopPropagation(); editProfile(' + profile.id + ')" title="Edit">✏️</button>';
                    html += '<button onclick="event.stopPropagation(); deleteProfile(' + profile.id + ')" title="Delete">🗑️</button>';
                    html += '</div>';
                    html += '</div>';
                }
                html += '</div>';
                container.innerHTML = html;
            } else {
                container.innerHTML = '<div class="empty-state"><div class="empty-icon">📁</div><h4>No Profiles</h4><p>Click + New to create a profile</p></div>';
            }

            // Auto-select first profile if none selected
            if (!currentSelectedProfile && result.data && result.data.length > 0) {
                selectProfile(result.data[0].id);
            }

            var activeProfile = null;

            for (var x = 0; x < result.data.length; x++) {
                if (result.data[x].is_active) {
                    activeProfile = result.data[x];
                    break;
                }
            }

            var activeProfileElement =
                document.getElementById('activeProfileName');

            if (activeProfileElement) {
                activeProfileElement.textContent =
                    activeProfile ? activeProfile.name : 'None';
            }

            updateSystemStatus();
        })
        .catch(function (error) {
            console.error('Error loading profiles:', error);
        });
}

function selectProfile(profileId) {
    API.profiles.getAll()
        .then(function (result) {
            if (result.ok && result.data) {
                var profile = null;
                for (var i = 0; i < result.data.length; i++) {
                    if (result.data[i].id === profileId) {
                        profile = result.data[i];
                        break;
                    }
                }
                if (profile) {
                    currentSelectedProfile = profile;
                    loadSchedules(profileId);
                    loadProfiles(); // Refresh to update selection highlight

                    var titleEl = document.getElementById('schedulesPanelTitle');
                    var warningEl = document.getElementById('profileStatusWarning');

                    if (titleEl) {
                        titleEl.innerHTML = '📋 SCHEDULES: ' + escapeHtml(profile.name);
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
        })
        .catch(function (error) {
            console.error('Error selecting profile:', error);
        });
}

function activateProfile(profileId) {

    Swal.fire({
        title: 'Activate Profile?',
        text: 'All schedules will be reloaded',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Activate',
        cancelButtonText: 'Cancel',
        confirmButtonColor: '#4CAF50'
    }).then(function (result) {

        if (!result.isConfirmed) return;

        API.profiles.activate(profileId)
            .then(function () {
                return loadProfiles();
            })
            .then(function () {

                if (
                    currentSelectedProfile &&
                    currentSelectedProfile.id === profileId
                ) {
                    return selectProfile(profileId);
                }

            })
            .then(function () {
                showToast('Profile activated!', 'success');
            })
            .catch(function (error) {
                showToast('Error: ' + error.message, 'danger');
            });

    });
}

function editProfile(profileId) {
    API.profiles.getAll()
        .then(function (result) {
            if (result.ok && result.data) {
                var profile = null;
                for (var i = 0; i < result.data.length; i++) {
                    if (result.data[i].id === profileId) {
                        profile = result.data[i];
                        break;
                    }
                }
                if (profile) {
                    ModalManager.showProfileDialog(profile);
                }
            }
        })
        .catch(function (error) {
            showToast('Error loading profile: ' + error.message, 'danger');
        });
}

function deleteProfile(profileId) {
    Swal.fire({
        title: 'Delete Profile?',
        text: 'All schedules in this profile will also be deleted!',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, Delete',
        cancelButtonText: 'Cancel',
        confirmButtonColor: '#d33'
    }).then(function (result) {

        if (!result.isConfirmed) return;

        API.profiles.delete(profileId)
            .then(function () {

                if (
                    currentSelectedProfile &&
                    currentSelectedProfile.id === profileId
                ) {
                    currentSelectedProfile = null;

                    var schedulesContainer =
                        document.getElementById('schedulesContainer');

                    if (schedulesContainer) {
                        schedulesContainer.innerHTML =
                            '<div class="empty-state">' +
                            '<div class="empty-icon">📅</div>' +
                            '<h4>No schedules</h4>' +
                            '<p>Select a profile or create a new schedule</p>' +
                            '</div>';
                    }
                }

                return loadProfiles();
            })
            .then(function () {
                showToast('Profile deleted!', 'warning');
            })
            .catch(function (error) {
                showToast('Error: ' + error.message, 'danger');
            });

    });
}

// =========================================================
// SCHEDULE FUNCTIONS
// =========================================================

function loadSchedules(profileId) {
    if (!profileId) return;

    API.schedules.getAll(profileId)
        .then(function (result) {
            var container = document.getElementById('schedulesContainer');
            if (!container) return;

            if (result.ok && result.data && result.data.length > 0) {
                currentSchedules = result.data;
                renderSchedulesTable(currentSchedules);
                updateUpcomingBell();
            } else {
                container.innerHTML = '<div class="empty-state"><div class="empty-icon">📅</div><h4>No schedules</h4><p>Click + Add Schedule to create one</p></div>';
            }
        })
        .catch(function (error) {
            console.error('Error loading schedules:', error);
            var container = document.getElementById('schedulesContainer');
            if (container) {
                container.innerHTML = '<div class="empty-state"><div class="empty-icon">⚠️</div><h4>Error loading schedules</h4><p>Please try again</p></div>';
            }
        });
}

function updateUpcomingBell() {
    var timeEl = document.getElementById('upcomingBellTime');
    var nameEl = document.getElementById('upcomingBellName');

    if (!timeEl || !nameEl) return;

    if (!currentSchedules || currentSchedules.length === 0) {
        timeEl.textContent = '--:--';
        nameEl.textContent = 'No Schedule';
        return;
    }

    var now = new Date();
    var currentDay = now.getDay();

    // convert Minggu=0 JS menjadi Minggu=6 sistem kamu
    currentDay = currentDay === 0 ? 6 : currentDay - 1;

    var currentMinutes =
        now.getHours() * 60 + now.getMinutes();

    var nextSchedule = null;
    var nextMinutes = null;

    for (var i = 0; i < currentSchedules.length; i++) {
        var s = currentSchedules[i];

        if (!s.is_active) continue;

        if (!s.days_list ||
            s.days_list.indexOf(currentDay) === -1) {
            continue;
        }

        var parts = s.bell_time.split(':');
        var minutes =
            parseInt(parts[0]) * 60 +
            parseInt(parts[1]);

        if (minutes >= currentMinutes) {
            if (
                nextMinutes === null ||
                minutes < nextMinutes
            ) {
                nextMinutes = minutes;
                nextSchedule = s;
            }
        }
    }

    if (nextSchedule) {
        timeEl.textContent = nextSchedule.bell_time;
        nameEl.textContent = nextSchedule.name;
    } else {
        timeEl.textContent = '--:--';
        nameEl.textContent = 'No More Today';
    }
}

function renderSchedulesTable(schedules) {
    var container = document.getElementById('schedulesContainer');
    if (!container) return;

    var searchInput = document.getElementById('scheduleSearch');
    var statusFilter = document.getElementById('scheduleStatusFilter');
    var searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
    var statusFilterValue = statusFilter ? statusFilter.value : 'all';

    var filteredSchedules = schedules.slice(); // copy array

    // Apply search filter
    if (searchTerm) {
        filteredSchedules = filteredSchedules.filter(function (s) {
            return s.name.toLowerCase().indexOf(searchTerm) !== -1;
        });
    }

    // Apply status filter
    if (statusFilterValue === 'active') {
        filteredSchedules = filteredSchedules.filter(function (s) {
            return s.is_active;
        });
    } else if (statusFilterValue === 'inactive') {
        filteredSchedules = filteredSchedules.filter(function (s) {
            return !s.is_active;
        });
    }

    if (filteredSchedules.length === 0) {
        container.innerHTML = '<div class="empty-state"><div class="empty-icon">🔍</div><h4>No matching schedules</h4><p>Try changing your search or filter</p></div>';
        return;
    }

    var dayNames = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'];
    var html = '<table class="schedules-table"><thead><tr>';
    html += '<th>Nama</th><th>Jam</th><th>Hari</th><th>Status</th><th>Action</th>';
    html += '</tr></thead><tbody>';

    for (var i = 0; i < filteredSchedules.length; i++) {
        var schedule = filteredSchedules[i];
        var rowClass = '';

        if (!schedule.is_active) {
            rowClass += ' inactive-row';
        }

        var upcomingTime =
            document.getElementById('upcomingBellTime');

        var upcomingName =
            document.getElementById('upcomingBellName');

        if (
            upcomingTime &&
            upcomingName &&
            upcomingTime.textContent === schedule.bell_time &&
            upcomingName.textContent === schedule.name
        ) {
            rowClass += ' upcoming-row';
        }
        html += '<tr class="' + rowClass + '">';
        html += '<td>' + escapeHtml(schedule.name) + '</td>';
        html += '<td><strong>' + schedule.bell_time + '</strong></td>';
        html += '<td>' + formatDays(schedule.days_list, dayNames) + '</td>';
        html += '<td><span class="badge ' + (schedule.is_active ? 'badge-success' : 'badge-danger') + '">' + (schedule.is_active ? 'Active' : 'Inactive') + '</span></td>';
        html += '<td><div class="action-buttons">';
        html += '<button class="btn-icon" onclick="testScheduleSound(' + schedule.id + ')" title="Test Sound">▶️</button>';
        html += '<button class="btn-icon" onclick="toggleSchedule(' + schedule.id + ', ' + (!schedule.is_active) + ')" title="' + (schedule.is_active ? 'Disable' : 'Enable') + '">' + (schedule.is_active ? '🔘' : '⚪') + '</button>';
        html += '<button class="btn-icon" onclick="editSchedule(' + schedule.id + ')" title="Edit">✏️</button>';
        html += '<button class="btn-icon" onclick="deleteSchedule(' + schedule.id + ')" title="Delete">🗑️</button>';
        html += '</div></td>';
        html += '</tr>';
    }

    html += '</tbody></table>';
    container.innerHTML = html;
}

function editSchedule(scheduleId) {
    if (!currentSelectedProfile) return;

    API.schedules.getAll(currentSelectedProfile.id)
        .then(function (result) {
            if (result.ok && result.data) {
                var schedule = null;
                for (var i = 0; i < result.data.length; i++) {
                    if (result.data[i].id === scheduleId) {
                        schedule = result.data[i];
                        break;
                    }
                }
                if (schedule) {
                    ModalManager.showScheduleDialog(schedule);
                }
            }
        })
        .catch(function (error) {
            showToast('Error loading schedule: ' + error.message, 'danger');
        });
}

function testScheduleSound(scheduleId) {

    var schedule = null;

    for (var i = 0; i < currentSchedules.length; i++) {
        if (currentSchedules[i].id === scheduleId) {
            schedule = currentSchedules[i];
            break;
        }
    }

    if (!schedule) {
        showToast('Schedule not found', 'danger');
        return;
    }

    API.system.testBell(schedule.audio_file)
        .then(function () {
            showToast(
                'Testing sound: ' + schedule.name,
                'success'
            );
        })
        .catch(function (error) {
            showToast(
                'Error testing sound: ' + error.message,
                'danger'
            );
        });
}

function deleteSchedule(scheduleId) {

    Swal.fire({
        title: 'Delete Schedule?',
        text: 'This action cannot be undone',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, Delete',
        cancelButtonText: 'Cancel',
        confirmButtonColor: '#d33'
    }).then(function (result) {

        if (!result.isConfirmed) return;

        API.schedules.delete(scheduleId)
            .then(function () {

                if (currentSelectedProfile) {
                    return loadSchedules(currentSelectedProfile.id);
                }

            })
            .then(function () {
                showToast('Schedule deleted!', 'warning');
            })
            .catch(function (error) {
                showToast('Error: ' + error.message, 'danger');
            });

    });
}

function toggleSchedule(scheduleId, newStatus) {
    API.schedules.toggle(scheduleId)
        .then(function () {
            if (currentSelectedProfile) {
                return loadSchedules(currentSelectedProfile.id);
            }
        })
        .then(function () {
            showToast('Schedule ' + (newStatus ? 'enabled' : 'disabled') + '!', 'info');
        })
        .catch(function (error) {
            showToast('Error: ' + error.message, 'danger');
        });
}

// =========================================================
// MODAL MANAGER
// =========================================================

var ModalManager = {
    showProfileDialog: function (profile) {
        var isEdit = profile !== null;
        var title = isEdit ? 'Edit Profile' : 'New Profile';

        var profileName = profile && profile.name || '';
        var profileDesc = profile && profile.description || '';
        var profileColor = profile && profile.color || '#4CAF50';

        var modal = this.createModal(title, `
            <div class="form-group">
                <label>Profile Name *</label>
                <input type="text" id="profileName" value="` + this.escapeHtml(profileName) + `" placeholder="e.g., Sekolah Pagi">
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea id="profileDesc" rows="3" placeholder="Optional description">` + this.escapeHtml(profileDesc) + `</textarea>
            </div>
            <div class="form-group">
                <label>Color</label>
                <input type="color"
                    id="profileColor"
                    class="color-picker"
                    value="` + profileColor + `">
            </div>
        `, 'saveProfileBtn');

        var saveBtn = modal.querySelector('#saveProfileBtn');
        if (saveBtn) {
            saveBtn.onclick = function () {
                var name = modal.querySelector('#profileName').value.trim();
                if (!name) {
                    alert('Profile name required');
                    return;
                }

                var data = {
                    name: name,
                    description: modal.querySelector('#profileDesc').value,
                    color: modal.querySelector('#profileColor').value
                };

                var promise = isEdit ? API.profiles.update(profile.id, data) : API.profiles.create(data.name, data.description, data.color);

                promise.then(function (result) {
                    if (result.ok) {
                        modal.remove();
                        loadProfiles();
                        showToast(isEdit ? 'Profile updated!' : 'Profile created!', 'success');
                    }
                }).catch(function (error) {
                    alert('Error: ' + error.message);
                });
            };
        }
    },

    showScheduleDialog: function (schedule) {
        var isEdit = schedule !== null;
        var title = isEdit ? 'Edit Schedule' : 'New Schedule';
        var dayNames = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'];

        if (!isEdit && !currentSelectedProfile) {
            showToast('Please select a profile first', 'warning');
            return;
        }

        var self = this;
        API.schedules.getAudioFiles()
            .then(function (audioResult) {
                var audioFiles = [];
                if (audioResult.ok && audioResult.data) {
                    audioFiles = audioResult.data;
                }

                var daysCheckboxes = '';
                for (var i = 0; i < dayNames.length; i++) {
                    var isChecked = schedule && schedule.days_list && schedule.days_list.indexOf(i) !== -1;
                    daysCheckboxes += '<label class="day-checkbox"><input type="checkbox" value="' + i + '"' + (isChecked ? ' checked' : '') + '><span>' + dayNames[i] + '</span></label>';
                }

                var audioOptions = '<option value="">🔔 Default Bell</option>';
                for (var j = 0; j < audioFiles.length; j++) {
                    var file = audioFiles[j];
                    var isSelected = schedule && schedule.audio_file === file.path;
                    audioOptions += '<option value="' + self.escapeHtml(file.path) + '"' + (isSelected ? ' selected' : '') + '>' + self.escapeHtml(file.name) + '</option>';
                }

                var scheduleName = schedule && schedule.name || '';
                var scheduleTime = schedule && schedule.bell_time || '07:00';
                var isActive = schedule ? schedule.is_active !== false : true;

                var modal = self.createModal(title, `
                    <div class="form-group">
                        <label>Schedule Name *</label>
                        <input type="text" id="scheduleName" value="` + self.escapeHtml(scheduleName) + `" placeholder="e.g., Bel Masuk">
                    </div>
                    <div class="form-group">
                        <label>Time</label>
                        <input type="time" id="scheduleTime" value="` + scheduleTime + `">
                    </div>
                    <div class="form-group">
                        <label>Days</label>
                        <div class="days-preset-buttons">
                        <button type="button" class="btn btn-secondary btn-small"
                            onclick="setDaysPreset([0,1,2,3,4,5])">Senin - Sabtu</button>

                        <button type="button" class="btn btn-secondary btn-small"
                            onclick="setDaysPreset([0,1,2,3,4])">Senin - Jumat</button>

                        <button type="button" class="btn btn-secondary btn-small" 
                            onclick="setDaysPreset([5,6])">Sabtu - Minggu</button>

                        <button type="button" class="btn btn-secondary btn-small"
                            onclick="setDaysPreset([0,1,2,3,4,5,6])">Semua </button> 
                    </div>

                        <div class="days-checkboxes" id="daysCheckboxes">
                            ` + daysCheckboxes + `
                        </div></div>
                    <div class="form-group">
                        <label>Audio File (Optional)</label>
                        <select id="scheduleAudio" class="audio-select">` + audioOptions + `</select>
                        <small>Select audio file from assets/audio directory</small>
                    </div>
                    <div class="form-group">
                        <div class="checkbox-inline" >
                            <input type = "checkbox"
                                id="scheduleActive"
                                ` + (isActive ? 'checked' : '') + `>
                            <label for="scheduleActive">Active</label>
                        </div>
                    </div>
                    ` + (!isEdit ? '<input type="hidden" id="profileId" value="' + currentSelectedProfile.id + '">' : '') + `
                `, 'saveScheduleBtn');

                var saveBtn = modal.querySelector('#saveScheduleBtn');
                if (saveBtn) {
                    saveBtn.onclick = function () {
                        var name = modal.querySelector('#scheduleName').value.trim();
                        if (!name) {
                            alert('Schedule name required');
                            return;
                        }

                        var timeValue = modal.querySelector('#scheduleTime').value;
                        var timeParts = timeValue.split(':');
                        var hour = parseInt(timeParts[0]);
                        var minute = parseInt(timeParts[1]);

                        var checkboxes = modal.querySelectorAll('#daysCheckboxes input:checked');
                        var days = [];
                        for (var k = 0; k < checkboxes.length; k++) {
                            days.push(parseInt(checkboxes[k].value));
                        }

                        var data = {
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

                        var promise = isEdit ? API.schedules.update(schedule.id, data) : API.schedules.create(data);

                        promise.then(function (result) {
                            if (result.ok) {
                                modal.remove();
                                if (currentSelectedProfile) {
                                    loadSchedules(currentSelectedProfile.id);
                                }
                                showToast(isEdit ? 'Schedule updated!' : 'Schedule created!', 'success');
                            }
                        }).catch(function (error) {
                            alert('Error: ' + error.message);
                        });
                    };
                }
            })
            .catch(function (error) {
                console.error('Error loading audio files:', error);
            });
    },
    
    createModal: function (title, bodyHtml, saveButtonId) {
        saveButtonId = saveButtonId || 'saveBtn';
        var modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3>` + this.escapeHtml(title) + `</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">` + bodyHtml + `</div>
                <div class="modal-footer">
                    <button class="btn btn-secondary cancel-btn">Cancel</button>
                    <button class="btn btn-primary" id="` + saveButtonId + `">Save</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        var closeModal = function () {
            modal.remove();
        };
        var closeBtn = modal.querySelector('.modal-close');
        var cancelBtn = modal.querySelector('.cancel-btn');

        if (closeBtn) closeBtn.onclick = closeModal;
        if (cancelBtn) cancelBtn.onclick = closeModal;

        return modal;
    },

    escapeHtml: function (text) {
        if (!text) return '';
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// =========================================================
// SYSTEM FUNCTIONS
// =========================================================
function setDaysPreset(days) {
    var checkboxes = document.querySelectorAll('#daysCheckboxes input[type="checkbox"]');

    for (var i = 0; i < checkboxes.length; i++) {
        var value = parseInt(checkboxes[i].value);
        checkboxes[i].checked = days.indexOf(value) !== -1;
    }
}

function updateSystemStatus() {
    API.system.getStatus()
        .then(function (result) {
            if (result.ok) {
                var statusElement = document.getElementById('systemStatus');
                if (statusElement) {
                    var dot = statusElement.querySelector('.status-dot');
                    var text = statusElement.querySelector('.status-text');

                    if (result.data.running) {
                        if (dot) dot.classList.add('running');
                        if (text) text.textContent = 'System Running';
                    } else {
                        if (dot) dot.classList.remove('running');
                        if (text) text.textContent = 'System Stopped';
                    }
                }
            }
        })
        .catch(function (error) {
            console.error('Error updating system status:', error);
        });
}

function updateDateTime() {
    var now = new Date();
    var timeStr = now.toLocaleTimeString('id-ID');
    var dateStr = now.toLocaleDateString('id-ID', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    var timeEl = document.getElementById('currentTime');
    var dateEl = document.getElementById('currentDate');

    if (timeEl) timeEl.textContent = timeStr;
    if (dateEl) dateEl.textContent = dateStr;
}

// =========================================================
// SYSTEM CONTROL
// =========================================================

var systemControl = {
    start: function () {
        API.system.start()
            .then(function () {
                updateSystemStatus();
                showToast('System started!', 'success');
            })
            .catch(function (error) {
                showToast('Error starting system: ' + error.message, 'danger');
            });
    },

    stop: function () {
        API.system.stop()
            .then(function () {
                updateSystemStatus();
                showToast('System stopped!', 'warning');
            })
            .catch(function (error) {
                showToast('Error stopping system: ' + error.message, 'danger');
            });
    },

    testBell: function () {
        API.system.testBell()
            .then(function () {
                showToast('Test bell triggered!', 'success');
            })
            .catch(function (error) {
                showToast('Error testing bell: ' + error.message, 'danger');
            });
    },

    stopBell: function () {
        API.system.stopBell()
            .then(function () {
                showToast('Bell stopped!', 'warning');
            })
            .catch(function (error) {
                showToast('Error stopping bell: ' + error.message, 'danger');
            });
    },

    reload: function () {
        API.system.reload()
            .then(function () {
                if (currentSelectedProfile) {
                    return loadSchedules(currentSelectedProfile.id);
                }
            })
            .then(function () {
                showToast('System reloaded!', 'success');
            })
            .catch(function (error) {
                showToast('Error reloading system: ' + error.message, 'danger');
            });
    }
};

// =========================================================
// DASHBOARD CLASS
// =========================================================

var dashboard = {
    refreshInterval: null,

    init: function () {
        loadProfiles();
        updateSystemStatus();
        this.startAutoRefresh();
        this.bindEvents();
        updateDateTime();
        setInterval(function () {
            updateDateTime();
        }, 1000);
    },

    bindEvents: function () {
        var searchInput = document.getElementById('scheduleSearch');
        if (searchInput) {
            searchInput.addEventListener('input', function () {
                if (currentSchedules.length > 0) {
                    renderSchedulesTable(currentSchedules);
                    updateUpcomingBell();
                }
            });
        }

        var statusFilter = document.getElementById('scheduleStatusFilter');
        if (statusFilter) {
            statusFilter.addEventListener('change', function () {
                if (currentSchedules.length > 0) {
                    renderSchedulesTable(currentSchedules);
                    updateUpcomingBell();
                }
            });
        }
    },

    startAutoRefresh: function () {
        var self = this;
        if (this.refreshInterval) clearInterval(this.refreshInterval);
        this.refreshInterval = setInterval(function () {
            if (currentSelectedProfile) {
                loadSchedules(currentSelectedProfile.id);
            }
            updateSystemStatus();
        }, 5000);
    },

    showToast: function (message, type) {
        showToast(message, type);
    }
};

// =========================================================
// INITIALIZATION
// =========================================================

document.addEventListener('DOMContentLoaded', function () {
    dashboard.init();
});