
//static/js/auth.js
// Parse JWT payload
function parseJwt(token) {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64)
      .split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
      .join(''));
    return JSON.parse(jsonPayload);
  }
  
  // Toggle Sign In / Sign Up forms
  document.getElementById('toggle-signin').addEventListener('click', () => {
    document.getElementById('signin-form').classList.remove('hidden');
    document.getElementById('signup-form').classList.add('hidden');
    document.getElementById('toggle-signin').classList.replace('text-gray-400','text-gray-600');
    document.getElementById('toggle-signup').classList.replace('text-gray-600','text-gray-400');
  });
  document.getElementById('toggle-signup').addEventListener('click', () => {
    document.getElementById('signup-form').classList.remove('hidden');
    document.getElementById('signin-form').classList.add('hidden');
    document.getElementById('toggle-signup').classList.replace('text-gray-400','text-gray-600');
    document.getElementById('toggle-signin').classList.replace('text-gray-600','text-gray-400');
  });
  
  // Initialize Google Sign-In on page load
  window.onload = function() {
    google.accounts.id.initialize({
      client_id: '433799197630-t1i525mej4v7p1hecnl8e0to714e5vl0.apps.googleusercontent.com',
      callback: handleCredentialResponse
    });
    google.accounts.id.renderButton(
      document.getElementById('g_id_signin'),
      { theme: 'outline', size: 'large', text: 'signin_with' }
    );
    google.accounts.id.prompt(); // optional one-tap
  };
  
  // Handle the Google One-Tap / button response
  async function handleCredentialResponse(response) {
    const payload = parseJwt(response.credential);
  
    // Show user info in UI
    document.getElementById('user-name').textContent = payload.name;
    document.getElementById('user-email').textContent = payload.email;
    document.getElementById('profile-pic').src = payload.picture;
    document.getElementById('user-info').classList.remove('hidden');
  
    // Send the ID token to backend for verification + session
    try {
      const res = await fetch('/auth/verify-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_token_str: response.credential })
      });
      if (!res.ok) throw new Error('Token verification failed');
      const userInfo = await res.json();
      console.log('Server verified user:', userInfo);
      // TODO: you could redirect or set a cookie here
    } catch (err) {
      console.error(err);
      alert('Authentication failed on server');
    }
  }
  
  // GitHub OAuth stub
  document.getElementById('github-signin').addEventListener('click', () => {
    window.location.href = 'https://github.com/login/oauth/authorize?client_id=YOUR_GITHUB_CLIENT_ID&scope=user:email';
  });
  