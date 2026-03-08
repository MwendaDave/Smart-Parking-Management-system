const API_URL = 'http://localhost:5000/api';
let map, markers = [], selectedSlot = null;

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    initMap();
    loadParkingSlots();
});

function checkAuth() {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    if (!token || !user) {
        window.location.href = 'login.html';
        return;
    }
    document.getElementById('user-name').textContent = `Welcome, ${JSON.parse(user).full_name}`;
}

function initMap() {
    map = L.map('map').setView([-1.2921, 36.8219], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
}

async function loadParkingSlots(location = '') {
    showLoading(true);
    try {
        const res = await fetch(`${API_URL}/parking/slots?status=available&location=${location}`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const data = await res.json();
        if (data.success) {
            displaySlots(data.data);
            updateMap(data.data);
            localStorage.setItem('cached_slots', JSON.stringify(data.data));
        }
    } catch (err) {
        console.error(err);
        const cached = localStorage.getItem('cached_slots');
        if (cached) displaySlots(JSON.parse(cached));
    } finally {
        showLoading(false);
    }
}

function displaySlots(slots) {
    const container = document.getElementById('parking-list');
    container.innerHTML = slots.length ? '' : '<p class="loading">No slots available</p>';
    
    slots.forEach(slot => {
        const card = document.createElement('div');
        card.className = `parking-card ${slot.status}`;
        card.innerHTML = `
            <div class="slot-header">
                <span class="slot-number">Slot ${slot.slot_number}</span>
                <span class="status-badge ${slot.status}">${slot.status}</span>
            </div>
            <div class="location">📍 ${slot.location}</div>
            <div class="rate">KES ${slot.hourly_rate}/hour</div>
            <button class="btn-reserve" ${slot.status !== 'available' ? 'disabled' : ''}
                onclick="openModal(${slot.slot_id}, '${slot.slot_number}', ${slot.hourly_rate})">
                ${slot.status === 'available' ? 'Reserve' : 'Unavailable'}
            </button>
        `;
        container.appendChild(card);
    });
}

function updateMap(slots) {
    markers.forEach(m => map.removeLayer(m));
    markers = [];
    slots.forEach((slot, i) => {
        const lat = -1.2921 + (Math.random() - 0.5) * 0.02;
        const lng = 36.8219 + (Math.random() - 0.5) * 0.02;
        const marker = L.marker([lat, lng]).addTo(map);
        marker.bindPopup(`<b>Slot ${slot.slot_number}</b><br>${slot.location}<br>KES ${slot.hourly_rate}/hr`);
        markers.push(marker);
    });
}

function searchParking() {
    loadParkingSlots(document.getElementById('location-search').value);
}

function openModal(slotId, number, rate) {
    selectedSlot = { slotId, number, rate };
    document.getElementById('reservation-details').innerHTML = `
        <p><strong>Slot:</strong> ${number}</p>
        <p><strong>Rate:</strong> KES ${rate}/hour</p>
        <p><strong>Est. Cost:</strong> KES <span id="est-cost">${rate}</span></p>
    `;
    document.getElementById('duration').addEventListener('input', (e) => {
        document.getElementById('est-cost').textContent = rate * (parseInt(e.target.value) || 1);
    });
    document.getElementById('reservation-modal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('reservation-modal').classList.add('hidden');
    selectedSlot = null;
}

async function confirmReservation() {
    if (!selectedSlot) return;
    const duration = parseInt(document.getElementById('duration').value) || 1;
    
    try {
        const res = await fetch(`${API_URL}/reservations/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ slot_id: selectedSlot.slotId, duration })
        });
        const data = await res.json();
        
        if (data.success) {
            alert(`✅ Reserved! ID: ${data.reservation_id}\nCost: KES ${data.total_cost}`);
            localStorage.setItem(`res_${data.reservation_id}`, JSON.stringify(data));
            closeModal();
            loadParkingSlots();
            window.location.href = `qr.html?res_id=${data.reservation_id}&qr=${encodeURIComponent(data.qr_code)}`;
        } else {
            showError(data.error || 'Reservation failed');
        }
    } catch (err) {
        showError('Network error. Please try again.');
    }
}

function showLoading(show) {
    document.getElementById('loading').classList.toggle('hidden', !show);
}

function showError(msg) {
    const el = document.getElementById('error-message');
    el.textContent = msg;
    el.classList.remove('hidden');
    setTimeout(() => el.classList.add('hidden'), 5000);
}

function logout() {
    localStorage.clear();
    window.location.href = 'login.html';
}