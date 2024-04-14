
function applyToCampaign(event, campaignId) {
    event.preventDefault();

    fetch('/apply_campaign', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': '{{ csrf_token() }}'  // Ensure CSRF token is included if CSRF protection is enabled
        },
        body: `campaign_id=${campaignId}`
    })
    .then(response => response.json())
    .then(data => {
        showNotification(data.message);
    })
    .catch(error => console.error('Error:', error));
}

function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    document.body.appendChild(notification);

    // Add the 'show' class to make the notification visible
    notification.classList.add('show');

    // Remove the notification after 4 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        document.body.removeChild(notification);
    }, 4000);
}

