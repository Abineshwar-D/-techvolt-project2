 document.getElementById('togglePassword').addEventListener('click', function() {
            const passwordInput = document.getElementById('password');
            const icon = this.querySelector('i');

            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.remove('bi-eye');
                icon.classList.add('bi-eye-slash');
            } else {
                passwordInput.type = 'password';
                icon.classList.remove('bi-eye-slash');
                icon.classList.add('bi-eye');
            }
        });

        // Form Submission with Loading Animation
//        document.getElementById('loginForm').addEventListener('submit', function(e) {
//
//            const btn = document.getElementById('loginBtn');
//            const originalContent = btn.innerHTML;
//
//            // Show loading state
//            btn.innerHTML = '<span class="animate-spin"><i class="bi bi-arrow-repeat"></i></span> Authenticating...';
//            btn.disabled = true;
//
//            // Simulate API call
//            setTimeout(() => {
//        this.submit();   // Submit the form to login.py
//    }, 1500);
//        });

        // Input focus effects
        document.querySelectorAll('.input-group-custom input').forEach(input => {
            input.addEventListener('focus', function() {
                this.closest('.input-group-custom').style.boxShadow = '0 2px 8px rgba(0,0,0,0.05)';
            });
            input.addEventListener('blur', function() {
                this.closest('.input-group-custom').style.boxShadow = 'none';
            });
        });