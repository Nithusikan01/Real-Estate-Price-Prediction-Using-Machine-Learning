const API_BASE_URL = '/api';

// Check API status on page load
async function checkApiStatus() {
    const statusEl = document.getElementById('apiStatus');
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        if (response.ok) {
            statusEl.className = 'api-status online';
            statusEl.textContent = '✅ API Connected';
            statusEl.style.display = 'block';
            setTimeout(() => {
                statusEl.style.display = 'none';
            }, 3000);
        } else {
            throw new Error('API not responding');
        }
    } catch (error) {
        statusEl.className = 'api-status offline';
        statusEl.textContent = '❌ API Offline - Please start the Flask server';
        statusEl.style.display = 'block';
    }
}

// Format price with commas and currency
function formatPrice(price) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(price);
}

// Show loading state
function setLoading(isLoading) {
    const btn = document.getElementById('predictBtn');
    const btnText = document.getElementById('btnText');
    const loading = document.getElementById('loading');
    
    if (isLoading) {
        btn.disabled = true;
        btnText.style.opacity = '0';
        loading.style.display = 'block';
    } else {
        btn.disabled = false;
        btnText.style.opacity = '1';
        loading.style.display = 'none';
    }
}

// Show result
function showResult(message, isError = false, price = null) {
    const resultEl = document.getElementById('result');
    resultEl.className = `result ${isError ? 'error' : 'success'}`;
    
    if (price && !isError) {
        resultEl.innerHTML = `
            <div>🎉 Estimated Property Value</div>
            <div class="price-display">${formatPrice(price)}</div>
            <div style="margin-top: 10px; font-size: 0.9rem; opacity: 0.9;">
                *Estimate based on provided features
            </div>
        `;
    } else {
        resultEl.innerHTML = `<div>${isError ? '❌' : '✅'} ${message}</div>`;
    }
    
    resultEl.style.display = 'block';
    
    // Auto-hide success messages after 10 seconds
    if (!isError) {
        setTimeout(() => {
            resultEl.style.display = 'none';
        }, 10000);
    }
}

// Handle form submission
document.getElementById('predictionForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    setLoading(true);
    
    try {
        // Collect form data
        const formData = new FormData(e.target);
        
        // Create input array in the exact order expected by the model
        const inputFeatures = [
            parseInt(formData.get('area')),           // area
            parseInt(formData.get('bedrooms')),       // bedrooms
            parseInt(formData.get('bathrooms')),      // bathrooms
            parseInt(formData.get('stories')),        // stories
            formData.get('mainroad'),                 // mainroad
            formData.get('guestroom'),                // guestroom
            formData.get('basement'),                 // basement
            formData.get('hotwaterheating'),          // hotwaterheating
            formData.get('airconditioning'),          // airconditioning
            parseInt(formData.get('parking')),        // parking
            formData.get('prefarea'),                 // prefarea
            formData.get('furnishingstatus')          // furnishingstatus
        ];

        // Make API request
        const response = await fetch(`${API_BASE_URL}/get_predicted_price`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                input: inputFeatures
            })
        });

        const data = await response.json();

        if (response.ok && data.estimated_price) {
            showResult('', false, data.estimated_price);
        } else {
            showResult(data.error || 'Prediction failed', true);
        }

    } catch (error) {
        console.error('Error:', error);
        showResult('Network error - please check if the API server is running', true);
    } finally {
        setLoading(false);
    }
});

// Add input animations
document.querySelectorAll('input, select').forEach(input => {
    input.addEventListener('focus', function() {
        this.parentElement.style.transform = 'translateY(-2px)';
    });
    
    input.addEventListener('blur', function() {
        this.parentElement.style.transform = 'translateY(0)';
    });
});

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    checkApiStatus();
    
    // Add sample values matching your example input
    // [7420, 4, 2, 3, "yes", "no", "no", "no", "yes", 2, "yes", "furnished"]
    document.getElementById('area').value = '7420';
    document.getElementById('bedrooms').value = '4';
    document.getElementById('bathrooms').value = '2';
    document.getElementById('stories').value = '3';
    document.getElementById('mainroad').value = 'yes';
    document.getElementById('guestroom').value = 'no';
    document.getElementById('basement').value = 'no';
    document.getElementById('hotwaterheating').value = 'no';
    document.getElementById('airconditioning').value = 'yes';
    document.getElementById('parking').value = '2';
    document.getElementById('prefarea').value = 'yes';
    document.getElementById('furnishingstatus').value = 'furnished';
});
