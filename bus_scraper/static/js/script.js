function showToast(message, isSuccess = true) {
    const toast = document.getElementById('notificationToast');
    const toastInstance = new bootstrap.Toast(toast);
    const toastHeader = document.getElementById('toastHeader');
    const toastTitle = document.getElementById('toastTitle');
    const toastMessage = document.getElementById('toastMessage');

    toast.classList.remove('success', 'error');
    toast.classList.add(isSuccess ? 'success' : 'error');
    toastTitle.textContent = isSuccess ? 'Success' : 'Error';
    toastMessage.textContent = message;

    toastInstance.show();
}

function isValidUrl(url) {
    try {
        new URL(url);
        return true;
    } catch (error) {
        return false;
    }
}

function displayResults(data) {
    const resultsCard = document.getElementById('resultsCard');
    const resultsTable = document.getElementById('resultsTable');
    const resultCount = document.getElementById('resultCount');

    // Clear previous results
    resultsTable.innerHTML = '';

    // Update count badge
    resultCount.textContent = `${data.length} buses found`;

    // Add each bus to the table
    data.forEach(bus => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                ${bus.logo_url ? `<img src="${bus.logo_url}" alt="logo" class="bus-logo me-2">` : ''}
                ${bus.bus_name}
            </td>
            <td>${bus.bus_type}</td>
            <td>${bus.departure.full_name}</td>
            <td>${bus.arrival.full_name}</td>
            <td>${bus.departure_time}</td>
            <td>${bus.price}</td>
            <td>${bus.rewards}</td>
            <td><a href="${bus.booking_url}" target="_blank">Book Now</a></td>
        `;
        resultsTable.appendChild(row);
    });

    // Show results card
    resultsCard.classList.remove('d-none');
}

async function scrapeData() {
    const htmlContent = document.getElementById('htmlContent').value;
    const baseUrl = document.getElementById('baseUrl').value;
    const button = document.getElementById('scrapeButton');
    const spinner = document.getElementById('loadingSpinner');
    const resultsCard = document.getElementById('resultsCard');

    // Validate inputs
    if (!htmlContent.trim()) {
        showToast('Please enter HTML content to scrape.', false);
        return;
    }

    if (!baseUrl.trim()) {
        showToast('Please enter a valid booking URL.', false);
        return;
    }

    if (!isValidUrl(baseUrl)) {
        showToast('Please enter a valid URL (e.g., https://example.com).', false);
        return;
    }

    // Show loading state
    button.disabled = true;
    spinner.classList.remove('d-none');
    resultsCard.classList.add('d-none');

    try {
        const response = await fetch('/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `html_content=${encodeURIComponent(htmlContent)}&base_url=${encodeURIComponent(baseUrl)}`
        });

        const result = await response.json();

        if (result.status === 'success') {
            if (result.data && result.data.length > 0) {
                showToast(result.message, true);
                displayResults(result.data);
            } else {
                showToast('No bus data found in the provided HTML content.', false);
            }
        } else {
            showToast(result.message, false);
        }
    } catch (error) {
        showToast('An error occurred while scraping data.', false);
    } finally {
        // Reset loading state
        button.disabled = false;
        spinner.classList.add('d-none');
    }
}