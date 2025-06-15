// Enhanced JavaScript with animations and better UX

// Utility functions
const Utils = {
    // Debounce function for performance
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Animate counter
    animateCounter: (element, start, end, duration) => {
        const startTime = performance.now();
        const animate = (currentTime) => {
            const elapsedTime = currentTime - startTime;
            const progress = Math.min(elapsedTime / duration, 1);
            const currentValue = Math.floor(progress * (end - start) + start);
            element.textContent = currentValue.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        requestAnimationFrame(animate);
    },

    // Format currency
    formatCurrency: (amount) => {
        return new Intl.NumberFormat('en-PK', {
            style: 'currency',
            currency: 'PKR',
            minimumFractionDigits: 0
        }).format(amount);
    },

    // Validate URL
    isValidUrl: (url) => {
        try {
            new URL(url);
            return true;
        } catch (error) {
            return false;
        }
    },

    // Copy to clipboard
    copyToClipboard: async (text) => {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            return false;
        }
    }
};

// Toast notification system
const ToastManager = {
    show: (message, type = 'success', duration = 5000) => {
        const toast = document.getElementById('notificationToast');
        const toastInstance = new bootstrap.Toast(toast, { delay: duration });
        const toastTitle = document.getElementById('toastTitle');
        const toastMessage = document.getElementById('toastMessage');
        const toastIcon = document.getElementById('toastIcon');

        // Remove existing classes
        toast.classList.remove('success', 'error', 'warning', 'info');
        
        // Configuration for different toast types
        const configs = {
            success: { 
                title: 'Success', 
                icon: 'fas fa-check-circle',
                bgClass: 'bg-success'
            },
            error: { 
                title: 'Error', 
                icon: 'fas fa-exclamation-circle',
                bgClass: 'bg-danger'
            },
            warning: { 
                title: 'Warning', 
                icon: 'fas fa-exclamation-triangle',
                bgClass: 'bg-warning'
            },
            info: { 
                title: 'Info', 
                icon: 'fas fa-info-circle',
                bgClass: 'bg-info'
            }
        };
        
        const config = configs[type] || configs.info;
        
        // Apply styling and content
        toast.classList.add(type);
        toastTitle.textContent = config.title;
        toastIcon.className = config.icon + ' me-2';
        toastMessage.textContent = message;

        // Add sound effect (optional)
        if (type === 'success') {
            // You can add a success sound here
        }

        toastInstance.show();
    }
};

// Statistics manager
const StatsManager = {
    update: (data) => {
        const statsContainer = document.getElementById('statsContainer');
        const totalBusesEl = document.getElementById('totalBuses');
        const avgPriceEl = document.getElementById('avgPrice');
        const totalRoutesEl = document.getElementById('totalRoutes');

        if (data.length > 0) {
            // Calculate statistics
            const prices = data.map(bus => {
                const price = bus.price.replace(/[^\d]/g, '');
                return parseInt(price) || 0;
            }).filter(price => price > 0);

            const avgPriceValue = prices.length > 0 ? 
                Math.round(prices.reduce((a, b) => a + b, 0) / prices.length) : 0;

            const uniqueRoutes = new Set(data.map(bus => 
                `${bus.departure.city_code}-${bus.arrival.city_code}`
            )).size;

            // Animate counters
            Utils.animateCounter(totalBusesEl, 0, data.length, 1000);
            Utils.animateCounter(avgPriceEl, 0, avgPriceValue, 1200);
            Utils.animateCounter(totalRoutesEl, 0, uniqueRoutes, 800);

            // Update price with proper formatting
            setTimeout(() => {
                avgPriceEl.textContent = `₹${avgPriceValue.toLocaleString()}`;
            }, 1200);

            // Show stats container with animation
            statsContainer.classList.remove('d-none');
            statsContainer.style.animation = 'slideInUp 0.6s ease-out';
        }
    }
};

// Results display manager
const ResultsManager = {
    display: (data) => {
        const resultsCard = document.getElementById('resultsCard');
        const resultsTable = document.getElementById('resultsTable');
        const resultCount = document.getElementById('resultCount');

        // Clear previous results
        resultsTable.innerHTML = '';

        // Update count badge with animation
        resultCount.textContent = `${data.length} buses found`;
        resultCount.className = data.length > 0 ? 'badge bg-success' : 'badge bg-warning';

        // Add loading skeleton while rendering
        this.showSkeleton(resultsTable, 3);

        // Render results after a brief delay for better UX
        setTimeout(() => {
            resultsTable.innerHTML = '';
            this.renderBuses(data, resultsTable);
        }, 500);

        // Show results card
        resultsCard.classList.remove('d-none');
        
        // Update statistics
        StatsManager.update(data);
    },

    showSkeleton: (container, rows) => {
        for (let i = 0; i < rows; i++) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><div class="skeleton" style="height: 40px; border-radius: 8px;"></div></td>
                <td><div class="skeleton" style="height: 20px; border-radius: 4px;"></div></td>
                <td><div class="skeleton" style="height: 30px; border-radius: 6px;"></div></td>
                <td><div class="skeleton" style="height: 20px; border-radius: 4px;"></div></td>
                <td><div class="skeleton" style="height: 20px; border-radius: 4px;"></div></td>
                <td><div class="skeleton" style="height: 25px; border-radius: 5px;"></div></td>
                <td><div class="skeleton" style="height: 20px; border-radius: 4px;"></div></td>
                <td><div class="skeleton" style="height: 35px; border-radius: 8px;"></div></td>
            `;
            container.appendChild(row);
        }
    },

    renderBuses: (data, container) => {
        data.forEach((bus, index) => {
            const row = document.createElement('tr');
            row.style.animationDelay = `${index * 0.1}s`;
            row.style.animation = 'fadeInUp 0.5s ease-out forwards';
            row.style.opacity = '0';
            
            // Format facilities
            const facilities = bus.facility_images.slice(0, 3).map(img => 
                `<img src="${img}" alt="facility" style="width: 20px; height: 20px; margin: 0 2px; border-radius: 4px; transition: transform 0.3s ease;" 
                     onmouseover="this.style.transform='scale(1.2)'" 
                     onmouseout="this.style.transform='scale(1)'">`
            ).join('');

            // Create interactive elements
            const copyButton = `<button class="btn btn-sm btn-outline-secondary ms-1" 
                                       onclick="copyBusInfo('${bus.bus_name}', '${bus.departure.full_name}', '${bus.arrival.full_name}', '${bus.price}')"
                                       title="Copy bus info">
                                    <i class="fas fa-copy"></i>
                                </button>`;

            row.innerHTML = `
                <td>
                    <div class="d-flex align-items-center">
                        ${bus.logo_url ? `<img src="${bus.logo_url}" alt="logo" class="bus-logo me-3">` : ''}
                        <div>
                            <div class="fw-bold text-primary">${bus.bus_name || 'N/A'}</div>
                            <small class="text-muted">${bus.bus_type || 'Standard'}</small>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="badge bg-info">${bus.bus_type || 'Standard'}</span>
                </td>
                <td>
                    <div class="route-info">
                        <div class="fw-bold">
                            <span class="text-primary">${bus.departure.city_code || 'N/A'}</span> 
                            <i class="fas fa-arrow-right mx-2 text-muted"></i> 
                            <span class="text-success">${bus.arrival.city_code || 'N/A'}</span>
                        </div>
                        <small class="text-muted">${bus.departure.full_name || 'N/A'} to ${bus.arrival.full_name || 'N/A'}</small>
                    </div>
                </td>
                <td>
                    <div class="time-info">
                        <i class="fas fa-clock text-primary me-1"></i>
                        <span class="fw-bold">${bus.departure_time || 'N/A'}</span>
                    </div>
                </td>
                <td>
                    <div class="date-info">
                        <i class="fas fa-calendar text-success me-1"></i>
                        <span>${bus.date || 'N/A'}</span>
                    </div>
                </td>
                <td>
                    <div class="price-info">
                        <span class="fw-bold text-success fs-5">${bus.price || 'N/A'}</span>
                    </div>
                </td>
                <td>
                    <div class="rewards-info">
                        <i class="fas fa-star text-warning me-1"></i>
                        <span class="text-warning fw-bold">${bus.rewards || '0 points'}</span>
                    </div>
                </td>
                <td>
                    <div class="action-buttons">
                        <a href="${bus.booking_url}" target="_blank" class="btn btn-sm btn-primary">
                            <i class="fas fa-external-link-alt me-1"></i>Book Now
                        </a>
                        ${copyButton}
                        ${facilities ? `<div class="mt-1">${facilities}</div>` : ''}
                    </div>
                </td>
            `;
            container.appendChild(row);

            // Trigger animation
            setTimeout(() => {
                row.style.opacity = '1';
            }, index * 100);
        });
    }
};

// Copy bus information
// Copy bus information
function copyBusInfo(busName, departure, arrival, price) {
    const info = `${busName}\n${departure} → ${arrival}\nPrice: ${price}`;
    
    Utils.copyToClipboard(info).then(success => {
        if (success) {
            ToastManager.show('Bus information copied to clipboard!', 'success');
        } else {
            ToastManager.show('Failed to copy bus information', 'error');
        }
    });
}

// Main scraping function
function scrapeData() {
    const htmlContent = document.getElementById('htmlContent').value;
    const baseUrl = document.getElementById('baseUrl').value;
    const button = document.getElementById('scrapeButton');
    const spinner = document.getElementById('loadingSpinner');
    const playIcon = document.getElementById('playIcon');
    const buttonText = document.getElementById('buttonText');
    const resultsCard = document.getElementById('resultsCard');
    const statsContainer = document.getElementById('statsContainer');

    // Validation
    if (!htmlContent.trim()) {
        ToastManager.show('Please enter HTML content to scrape. Copy the HTML from BookMe.pk search results page.', 'error');
        return;
    }

    if (!baseUrl.trim()) {
        ToastManager.show('Please enter a valid booking URL.', 'error');
        return;
    }

    if (!Utils.isValidUrl(baseUrl)) {
        ToastManager.show('Please enter a valid URL (e.g., https://bookme.pk/bus/search-results).', 'error');
        return;
    }

    // Show loading state with animation
    button.disabled = true;
    spinner.classList.remove('d-none');
    playIcon.classList.add('d-none');
    buttonText.textContent = 'Scraping...';
    button.style.animation = 'pulse 1s infinite';
    
    // Hide previous results
    resultsCard.classList.add('d-none');
    statsContainer.classList.add('d-none');

    // Simulate API call (replace with actual fetch in production)
    setTimeout(() => {
        try {
            ToastManager.show('Starting data extraction...', 'info');
            
            // In a real implementation, you would make an API call here:
            /*
            const response = await fetch('/scrape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `html_content=${encodeURIComponent(htmlContent)}&base_url=${encodeURIComponent(baseUrl)}`
            });
            const result = await response.json();
            */
            
            // For demo purposes, we'll use sample data
            const sampleData = generateSampleData();
            
            if (sampleData && sampleData.length > 0) {
                ToastManager.show(`Successfully scraped ${sampleData.length} buses!`, 'success');
                ResultsManager.display(sampleData);
                
                // Scroll to results
                setTimeout(() => {
                    resultsCard.scrollIntoView({ behavior: 'smooth' });
                }, 500);
            } else {
                ToastManager.show('No bus data found in the provided HTML content. Please check the HTML structure.', 'warning');
            }
        } catch (error) {
            console.error('Scraping error:', error);
            ToastManager.show('An error occurred while scraping data.', 'error');
        } finally {
            // Reset loading state
            button.disabled = false;
            spinner.classList.add('d-none');
            playIcon.classList.remove('d-none');
            buttonText.textContent = 'Start Scraping';
            button.style.animation = '';
        }
    }, 1500); // Simulate network delay
}

// Generate sample data for demonstration
function generateSampleData() {
    const cities = [
        { city_code: 'KHI', full_name: 'Karachi' },
        { city_code: 'LHE', full_name: 'Lahore' },
        { city_code: 'ISB', full_name: 'Islamabad' },
        { city_code: 'PEW', full_name: 'Peshawar' },
        { city_code: 'UET', full_name: 'Quetta' }
    ];
    
    const busCompanies = [
        { name: 'Daewoo Express', logo: 'https://via.placeholder.com/40?text=Daewoo', type: 'Luxury' },
        { name: 'Faisal Movers', logo: 'https://via.placeholder.com/40?text=Faisal', type: 'Business' },
        { name: 'Skyways', logo: 'https://via.placeholder.com/40?text=Skyways', type: 'Economy' },
        { name: 'Niazi Express', logo: 'https://via.placeholder.com/40?text=Niazi', type: 'Standard' }
    ];
    
    const facilities = [
        'https://via.placeholder.com/20?text=AC',
        'https://via.placeholder.com/20?text=TV',
        'https://via.placeholder.com/20?text=WIFI',
        'https://via.placeholder.com/20?text=WC'
    ];
    
    const data = [];
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    for (let i = 0; i < 8; i++) {
        const departureCity = cities[Math.floor(Math.random() * cities.length)];
        let arrivalCity;
        do {
            arrivalCity = cities[Math.floor(Math.random() * cities.length)];
        } while (arrivalCity.city_code === departureCity.city_code);
        
        const bus = busCompanies[Math.floor(Math.random() * busCompanies.length)];
        
        data.push({
            bus_name: bus.name,
            bus_type: bus.type,
            logo_url: bus.logo,
            departure: { ...departureCity },
            arrival: { ...arrivalCity },
            departure_time: `${Math.floor(Math.random() * 12) + 1}:${Math.random() > 0.5 ? '00' : '30'} ${Math.random() > 0.5 ? 'AM' : 'PM'}`,
            date: Math.random() > 0.5 ? 
                today.toLocaleDateString('en-PK', { day: 'numeric', month: 'short', year: 'numeric' }) : 
                tomorrow.toLocaleDateString('en-PK', { day: 'numeric', month: 'short', year: 'numeric' }),
            price: `₹${Math.floor(Math.random() * 5000) + 1000}`,
            rewards: `${Math.floor(Math.random() * 100)} points`,
            booking_url: 'https://bookme.pk/bus/booking',
            facility_images: facilities.slice(0, Math.floor(Math.random() * 3) + 1)
        });
    }
    
    return data;
}

// Load sample data for testing
function loadSampleData() {
    const sampleHtml = `<div class="text-nowrap small"><span class="fw-semibold text-dark">Departure: </span> 13 Jun 2025</div>
<div class="my-3 text-reset card detail-card overflow-hidden">
    <div class="align-items-center p-2 px-3 px-lg-4 row">
        <div class="col-12">
            <div class="d-flex align-items-center justify-content-between">
                <h5 class="mb-0 font-weight-600">Daewoo Express <br class="d-md-none">
                    <span class="mb-0 font-weight-400 text-gray-500 fs-6 small">Luxury</span>
                </h5>
            </div>
        </div>
    </div>
</div>`;
    
    document.getElementById('htmlContent').value = sampleHtml;
    ToastManager.show('Sample data loaded! You can now test the scraper.', 'info');
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Add sample data button to the page
    const cardBody = document.querySelector('.card-body');
    const sampleButton = document.createElement('button');
    sampleButton.type = 'button';
    sampleButton.className = 'btn btn-outline-secondary btn-sm mb-3';
    sampleButton.innerHTML = '<i class="fas fa-flask me-1"></i> Load Sample Data';
    sampleButton.onclick = loadSampleData;
    
    const textarea = document.getElementById('htmlContent');
    textarea.parentNode.insertBefore(sampleButton, textarea);

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            scrapeData();
        }
    });

    // Add auto-resize to textarea
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 400) + 'px';
    });
});
