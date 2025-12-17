# T-024: Quick Action Shortcuts

## AI Coding Brief
**Role**: Full-Stack Developer
**Objective**: Implement quick action shortcuts for common tasks
**Related Story**: S-006 (Staff Dashboard)

## Constraints
**Allowed File Paths**:
- /apps/dashboard/views.py
- /templates/dashboard/*
- /templates/components/quick_actions.html
- /static/js/quick_actions.js

## Deliverables
- [ ] Quick action buttons on dashboard
- [ ] Modal forms for quick create
- [ ] Keyboard shortcuts
- [ ] Search-anywhere functionality
- [ ] Recent items quick access

## Technical Specifications

### Quick Action Component
```html
<!-- templates/components/quick_actions.html -->
<div class="quick-actions">
    <!-- Floating Action Button (Mobile) -->
    <div class="fixed bottom-6 right-6 md:hidden z-50">
        <button id="fab-toggle"
                class="w-14 h-14 rounded-full bg-blue-600 text-white shadow-lg
                       flex items-center justify-center hover:bg-blue-700
                       focus:outline-none focus:ring-2 focus:ring-blue-500">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
        </button>

        <!-- FAB Menu -->
        <div id="fab-menu" class="hidden absolute bottom-16 right-0 space-y-2">
            <a href="{% url 'reservation_create' %}"
               class="flex items-center justify-end space-x-2">
                <span class="bg-gray-800 text-white text-sm px-2 py-1 rounded">New Reservation</span>
                <span class="w-10 h-10 rounded-full bg-green-500 flex items-center justify-center text-white">
                    📅
                </span>
            </a>
            <a href="{% url 'customer_create' %}"
               class="flex items-center justify-end space-x-2">
                <span class="bg-gray-800 text-white text-sm px-2 py-1 rounded">Add Customer</span>
                <span class="w-10 h-10 rounded-full bg-purple-500 flex items-center justify-center text-white">
                    👤
                </span>
            </a>
            <a href="{% url 'vehicle_create' %}"
               class="flex items-center justify-end space-x-2">
                <span class="bg-gray-800 text-white text-sm px-2 py-1 rounded">Add Vehicle</span>
                <span class="w-10 h-10 rounded-full bg-orange-500 flex items-center justify-center text-white">
                    🚗
                </span>
            </a>
        </div>
    </div>

    <!-- Command Palette (Desktop) -->
    <div id="command-palette"
         class="hidden fixed inset-0 z-50 overflow-y-auto"
         aria-labelledby="modal-title" role="dialog" aria-modal="true">
        <div class="flex items-start justify-center min-h-screen pt-20 px-4">
            <!-- Backdrop -->
            <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
                 id="palette-backdrop"></div>

            <!-- Panel -->
            <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-xl transform transition-all">
                <!-- Search Input -->
                <div class="flex items-center px-4 border-b">
                    <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                    </svg>
                    <input type="text" id="command-input"
                           class="w-full px-4 py-4 text-lg focus:outline-none"
                           placeholder="Search or type a command..."
                           autocomplete="off">
                    <kbd class="px-2 py-1 text-xs bg-gray-100 rounded">ESC</kbd>
                </div>

                <!-- Results -->
                <div id="command-results" class="max-h-96 overflow-y-auto p-2">
                    <!-- Quick Actions -->
                    <div class="px-2 py-1 text-xs font-medium text-gray-500 uppercase">
                        Quick Actions
                    </div>
                    <div class="space-y-1">
                        <button class="command-item w-full flex items-center px-3 py-2 rounded hover:bg-gray-100"
                                data-action="new-reservation">
                            <span class="w-8 h-8 flex items-center justify-center bg-green-100 rounded mr-3">📅</span>
                            <span class="flex-1 text-left">New Reservation</span>
                            <kbd class="text-xs text-gray-400">Alt+N</kbd>
                        </button>
                        <button class="command-item w-full flex items-center px-3 py-2 rounded hover:bg-gray-100"
                                data-action="new-customer">
                            <span class="w-8 h-8 flex items-center justify-center bg-purple-100 rounded mr-3">👤</span>
                            <span class="flex-1 text-left">Add Customer</span>
                            <kbd class="text-xs text-gray-400">Alt+C</kbd>
                        </button>
                        <button class="command-item w-full flex items-center px-3 py-2 rounded hover:bg-gray-100"
                                data-action="view-calendar">
                            <span class="w-8 h-8 flex items-center justify-center bg-blue-100 rounded mr-3">📆</span>
                            <span class="flex-1 text-left">View Calendar</span>
                            <kbd class="text-xs text-gray-400">Alt+K</kbd>
                        </button>
                    </div>

                    <!-- Recent Items -->
                    <div class="mt-4 px-2 py-1 text-xs font-medium text-gray-500 uppercase">
                        Recent
                    </div>
                    <div id="recent-items" class="space-y-1">
                        <!-- Populated by JavaScript -->
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
```

### JavaScript for Quick Actions
```javascript
// static/js/quick_actions.js

class QuickActions {
    constructor() {
        this.palette = document.getElementById('command-palette');
        this.input = document.getElementById('command-input');
        this.results = document.getElementById('command-results');
        this.recentItems = document.getElementById('recent-items');
        this.fabToggle = document.getElementById('fab-toggle');
        this.fabMenu = document.getElementById('fab-menu');

        this.actions = {
            'new-reservation': '/reservations/create/',
            'new-customer': '/customers/create/',
            'new-vehicle': '/vehicles/create/',
            'view-calendar': '/calendar/',
            'view-dashboard': '/',
        };

        this.init();
    }

    init() {
        // Keyboard shortcut to open palette (Cmd/Ctrl + K)
        document.addEventListener('keydown', (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                this.togglePalette();
            }

            // Quick action shortcuts
            if (e.altKey) {
                switch(e.key.toLowerCase()) {
                    case 'n':
                        e.preventDefault();
                        window.location.href = this.actions['new-reservation'];
                        break;
                    case 'c':
                        e.preventDefault();
                        window.location.href = this.actions['new-customer'];
                        break;
                    case 'k':
                        e.preventDefault();
                        window.location.href = this.actions['view-calendar'];
                        break;
                }
            }

            // Close on Escape
            if (e.key === 'Escape' && this.palette && !this.palette.classList.contains('hidden')) {
                this.closePalette();
            }
        });

        // FAB toggle
        if (this.fabToggle) {
            this.fabToggle.addEventListener('click', () => {
                this.fabMenu.classList.toggle('hidden');
            });
        }

        // Backdrop click to close
        const backdrop = document.getElementById('palette-backdrop');
        if (backdrop) {
            backdrop.addEventListener('click', () => this.closePalette());
        }

        // Command input handling
        if (this.input) {
            this.input.addEventListener('input', (e) => this.handleSearch(e.target.value));
        }

        // Action buttons
        document.querySelectorAll('.command-item').forEach(item => {
            item.addEventListener('click', () => {
                const action = item.dataset.action;
                if (this.actions[action]) {
                    window.location.href = this.actions[action];
                }
            });
        });

        // Load recent items
        this.loadRecentItems();
    }

    togglePalette() {
        if (this.palette.classList.contains('hidden')) {
            this.openPalette();
        } else {
            this.closePalette();
        }
    }

    openPalette() {
        this.palette.classList.remove('hidden');
        this.input.focus();
        this.input.value = '';
    }

    closePalette() {
        this.palette.classList.add('hidden');
    }

    handleSearch(query) {
        if (query.length < 2) {
            this.showDefaultResults();
            return;
        }

        // Search API
        fetch(`/api/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => this.displaySearchResults(data))
            .catch(err => console.error('Search error:', err));
    }

    displaySearchResults(data) {
        const html = [];

        if (data.customers && data.customers.length) {
            html.push('<div class="px-2 py-1 text-xs font-medium text-gray-500 uppercase">Customers</div>');
            data.customers.forEach(c => {
                html.push(`
                    <a href="/customers/${c.id}/" class="flex items-center px-3 py-2 rounded hover:bg-gray-100">
                        <span class="w-8 h-8 flex items-center justify-center bg-purple-100 rounded mr-3">👤</span>
                        <span class="flex-1">${c.name}</span>
                        <span class="text-xs text-gray-400">${c.email}</span>
                    </a>
                `);
            });
        }

        if (data.reservations && data.reservations.length) {
            html.push('<div class="mt-2 px-2 py-1 text-xs font-medium text-gray-500 uppercase">Reservations</div>');
            data.reservations.forEach(r => {
                html.push(`
                    <a href="/reservations/${r.id}/" class="flex items-center px-3 py-2 rounded hover:bg-gray-100">
                        <span class="w-8 h-8 flex items-center justify-center bg-green-100 rounded mr-3">📅</span>
                        <span class="flex-1">#${r.confirmation_number}</span>
                        <span class="text-xs text-gray-400">${r.customer}</span>
                    </a>
                `);
            });
        }

        if (data.vehicles && data.vehicles.length) {
            html.push('<div class="mt-2 px-2 py-1 text-xs font-medium text-gray-500 uppercase">Vehicles</div>');
            data.vehicles.forEach(v => {
                html.push(`
                    <a href="/vehicles/${v.id}/" class="flex items-center px-3 py-2 rounded hover:bg-gray-100">
                        <span class="w-8 h-8 flex items-center justify-center bg-orange-100 rounded mr-3">🚗</span>
                        <span class="flex-1">${v.name}</span>
                        <span class="text-xs text-gray-400">${v.plate}</span>
                    </a>
                `);
            });
        }

        if (html.length === 0) {
            html.push('<div class="px-3 py-8 text-center text-gray-500">No results found</div>');
        }

        this.results.innerHTML = html.join('');
    }

    showDefaultResults() {
        // Reset to default quick actions view
        location.reload(); // Simple approach; could be more sophisticated
    }

    loadRecentItems() {
        // Load from localStorage
        const recent = JSON.parse(localStorage.getItem('recentItems') || '[]');

        if (recent.length && this.recentItems) {
            const html = recent.slice(0, 5).map(item => `
                <a href="${item.url}" class="flex items-center px-3 py-2 rounded hover:bg-gray-100">
                    <span class="w-8 h-8 flex items-center justify-center bg-gray-100 rounded mr-3">
                        ${item.icon}
                    </span>
                    <span class="flex-1 text-left">${item.title}</span>
                    <span class="text-xs text-gray-400">${item.type}</span>
                </a>
            `).join('');

            this.recentItems.innerHTML = html;
        }
    }

    static trackVisit(type, id, title, icon) {
        const recent = JSON.parse(localStorage.getItem('recentItems') || '[]');

        // Remove if already exists
        const filtered = recent.filter(item => !(item.type === type && item.id === id));

        // Add to front
        filtered.unshift({
            type,
            id,
            title,
            icon,
            url: `/${type}s/${id}/`,
            timestamp: Date.now()
        });

        // Keep only last 20
        localStorage.setItem('recentItems', JSON.stringify(filtered.slice(0, 20)));
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.quickActions = new QuickActions();
});
```

### Search API Endpoint
```python
# apps/dashboard/views.py

from django.http import JsonResponse
from django.db.models import Q

class GlobalSearchView(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('q', '').strip()

        if len(query) < 2:
            return JsonResponse({'error': 'Query too short'}, status=400)

        results = {
            'customers': [],
            'reservations': [],
            'vehicles': [],
        }

        # Search customers
        customers = Customer.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )[:5]
        results['customers'] = [
            {'id': c.id, 'name': c.full_name, 'email': c.email}
            for c in customers
        ]

        # Search reservations
        reservations = Reservation.objects.filter(
            Q(confirmation_number__icontains=query) |
            Q(customer__first_name__icontains=query) |
            Q(customer__last_name__icontains=query)
        )[:5]
        results['reservations'] = [
            {'id': r.id, 'confirmation_number': r.confirmation_number,
             'customer': r.customer.full_name}
            for r in reservations
        ]

        # Search vehicles
        vehicles = Vehicle.objects.filter(
            Q(license_plate__icontains=query) |
            Q(make__icontains=query) |
            Q(model__icontains=query) |
            Q(vin__icontains=query)
        )[:5]
        results['vehicles'] = [
            {'id': v.id, 'name': str(v), 'plate': v.license_plate}
            for v in vehicles
        ]

        return JsonResponse(results)
```

## Definition of Done
- [ ] Quick action buttons on dashboard
- [ ] Command palette opens with Ctrl/Cmd+K
- [ ] Keyboard shortcuts work (Alt+N, Alt+C, etc.)
- [ ] Global search finds customers, reservations, vehicles
- [ ] Recent items tracked and displayed
- [ ] Mobile FAB menu works
- [ ] Tests written and passing (>95% coverage)
