// Form validation for signup
document.addEventListener('DOMContentLoaded', function() {
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            
            if (password !== confirmPassword) {
                e.preventDefault();
                alert('Passwords do not match!');
                return false;
            }
            
            if (password.length < 6) {
                e.preventDefault();
                alert('Password must be at least 6 characters long!');
                return false;
            }
        });
    }
    
    // File upload validation
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            const fileInput = document.getElementById('file');
            const expiryDays = document.getElementById('expiry_days').value;
            
            if (!fileInput.files || fileInput.files.length === 0) {
                e.preventDefault();
                alert('Please select a file to upload!');
                return false;
            }
            
            if (!expiryDays || parseInt(expiryDays) < 1) {
                e.preventDefault();
                alert('Please specify a valid expiry time (at least 1 day)!');
                return false;
            }
            
            // Check file size (16MB limit)
            const file = fileInput.files[0];
            const maxSize = 16 * 1024 * 1024; // 16MB
            if (file.size > maxSize) {
                e.preventDefault();
                alert('File size exceeds 16MB limit!');
                return false;
            }
        });
    }
    
    // Login form validation
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (!email || !password) {
                e.preventDefault();
                alert('Please fill in all fields!');
                return false;
            }
        });
    }
});

