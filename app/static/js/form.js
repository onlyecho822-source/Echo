// Form submission handler for EchoDispute
document.getElementById('disputeForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const submitBtn = document.getElementById('submitBtn');
    const originalText = submitBtn.textContent;

    // Validate bureaus
    const bureauCheckboxes = document.querySelectorAll('input[name^="bureau_"]:checked');
    if (bureauCheckboxes.length === 0) {
        alert('Please select at least one credit bureau.');
        return;
    }

    // Disable button and show loading
    submitBtn.disabled = true;
    submitBtn.textContent = 'Processing...';
    submitBtn.classList.add('opacity-75');

    // Collect form data
    const formData = {
        firstName: document.getElementById('firstName').value,
        lastName: document.getElementById('lastName').value,
        email: document.getElementById('email').value,
        address: document.getElementById('address').value,
        city: document.getElementById('city').value,
        state: document.getElementById('state').value,
        zip: document.getElementById('zip').value,
        ssn: document.getElementById('ssn').value,
        dob: document.getElementById('dob').value,
        disputeType: document.getElementById('disputeType').value,
        creditorName: document.getElementById('creditorName').value,
        accountNumber: document.getElementById('accountNumber').value,
        errorDetails: document.getElementById('errorDetails').value,
        bureaus: Array.from(bureauCheckboxes).map(cb => cb.value)
    };

    try {
        // Send to backend
        const response = await fetch('/api/create-checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.checkout_url) {
            // Redirect to Stripe Checkout
            window.location.href = data.checkout_url;
        } else {
            throw new Error('Failed to create checkout session');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again or contact support.');
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
        submitBtn.classList.remove('opacity-75');
    }
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
