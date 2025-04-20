document.addEventListener('DOMContentLoaded', function() {
    // Handle password visibility toggle
    document.querySelectorAll('.btn-outline-secondary').forEach(button => {
        button.addEventListener('click', function() {
            const input = this.previousElementSibling;
            if (input.type === 'password') {
                input.type = 'text';
                this.textContent = 'Hide';
            } else {
                input.type = 'password';
                this.textContent = 'Show';
            }
        });
    });

    // Handle user management settings form submission
    const userManagementForm = document.querySelector('#users form');
    if (userManagementForm) {
        userManagementForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = {
                require_approval: document.getElementById('requireApproval').checked,
                approval_notification: document.querySelector('select[name="approval_notification"]').value,
                password_min_length: parseInt(document.querySelector('input[name="password_min_length"]').value),
                require_uppercase: document.getElementById('requireUppercase').checked,
                require_lowercase: document.getElementById('requireLowercase').checked,
                require_number: document.getElementById('requireNumber').checked,
                require_special: document.getElementById('requireSpecial').checked,
                password_expiry_days: parseInt(document.querySelector('input[name="password_expiry_days"]').value),
                enable_lockout: document.getElementById('enableLockout').checked,
                lockout_attempts: parseInt(document.querySelector('input[name="lockout_attempts"]').value),
                lockout_duration: parseInt(document.querySelector('input[name="lockout_duration"]').value)
            };

            try {
                const response = await fetch('/admin/settings/user-management', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                    },
                    body: JSON.stringify(formData)
                });
                
                if (response.ok) {
                    showAlert('success', 'User management settings updated successfully');
                } else {
                    showAlert('danger', 'Failed to update user management settings');
                }
            } catch (error) {
                showAlert('danger', 'An error occurred while updating settings');
            }
        });
    }

    // Handle system configuration form submission
    const systemConfigForm = document.querySelector('#system form');
    if (systemConfigForm) {
        systemConfigForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = {
                smtp_server: document.querySelector('input[name="smtp_server"]').value,
                smtp_port: parseInt(document.querySelector('input[name="smtp_port"]').value),
                smtp_username: document.querySelector('input[name="smtp_username"]').value,
                smtp_password: document.querySelector('input[name="smtp_password"]').value,
                use_tls: document.getElementById('useTLS').checked,
                anthropic_api_key: document.querySelector('input[name="anthropic_api_key"]').value,
                openai_api_key: document.querySelector('input[name="openai_api_key"]').value
            };

            try {
                const response = await fetch('/admin/settings/system', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                    },
                    body: JSON.stringify(formData)
                });
                
                if (response.ok) {
                    showAlert('success', 'System settings updated successfully');
                } else {
                    showAlert('danger', 'Failed to update system settings');
                }
            } catch (error) {
                showAlert('danger', 'An error occurred while updating settings');
            }
        });
    }

    // Handle role creation
    const addRoleForm = document.querySelector('#addRoleModal form');
    if (addRoleForm) {
        addRoleForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = {
                name: document.querySelector('input[name="role_name"]').value,
                description: document.querySelector('textarea[name="role_description"]').value,
                permissions: Array.from(document.querySelectorAll('input[name="permissions"]:checked')).map(cb => cb.value)
            };

            try {
                const response = await fetch('/admin/roles', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                    },
                    body: JSON.stringify(formData)
                });
                
                if (response.ok) {
                    const result = await response.json();
                    showAlert('success', 'Role created successfully');
                    location.reload(); // Refresh to show new role
                } else {
                    showAlert('danger', 'Failed to create role');
                }
            } catch (error) {
                showAlert('danger', 'An error occurred while creating role');
            }
        });
    }

    // Handle API key generation
    const generateApiKeyBtn = document.querySelector('#generateApiKey');
    if (generateApiKeyBtn) {
        generateApiKeyBtn.addEventListener('click', async function() {
            try {
                const response = await fetch('/admin/api-keys', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                    }
                });
                
                if (response.ok) {
                    const result = await response.json();
                    showAlert('success', 'API key generated successfully');
                    location.reload(); // Refresh to show new API key
                } else {
                    showAlert('danger', 'Failed to generate API key');
                }
            } catch (error) {
                showAlert('danger', 'An error occurred while generating API key');
            }
        });
    }

    // Handle webhook creation
    const addWebhookBtn = document.querySelector('#addWebhook');
    if (addWebhookBtn) {
        addWebhookBtn.addEventListener('click', function() {
            // Show webhook creation modal
            const modal = new bootstrap.Modal(document.getElementById('addWebhookModal'));
            modal.show();
        });
    }

    // Utility function to show alerts
    function showAlert(type, message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}); 