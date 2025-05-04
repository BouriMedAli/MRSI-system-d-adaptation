// static/js/auth.js

/**
 * Displays status messages on the authentication page.
 * @param {string} message The message to display.
 * @param {boolean} [isError=false] If true, styles the message as an error.
 */
function showStatus(message, isError = false) {
  const statusElement = document.getElementById('auth-status');
  if (statusElement) {
      statusElement.textContent = message;
      statusElement.className = `mt-4 text-center text-sm h-5 ${isError ? 'text-red-600' : 'text-green-600'}`;
  } else {
      console.log("Status element not found.");
  }
}

/**
* Initializes the Google Sign-In client and renders the button.
*/
function initializeGoogleSignIn() {
  if (typeof google === 'undefined' || !google.accounts || !google.accounts.id) {
      console.error("Google Identity Services script not loaded yet or failed to load.");
      showStatus("Error initializing Google Sign-In.", true);
      // Optionally retry after a delay
      // setTimeout(initializeGoogleSignIn, 1000);
      return;
  }

   if (!GOOGLE_CLIENT_ID) {
      console.error("Google Client ID is not set in the JavaScript environment.");
      showStatus("Configuration error: Google Client ID missing.", true);
      return;
  }

  try {
      google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: handleCredentialResponse,
          context: "signin",
          // ux_mode: "popup", // Or "redirect"
          // auto_select: true, // Be careful with auto_select, can be intrusive
      });

      const gsiButtonContainer = document.getElementById('g_id_signin');
      if (gsiButtonContainer) {
          google.accounts.id.renderButton(
              gsiButtonContainer,
              { theme: 'outline', size: 'large', text: 'signin_with', shape: 'rectangular', logo_alignment: 'left' }
          );
      } else {
           console.error("Google Sign-In button container ('g_id_signin') not found.");
           showStatus("UI error: Could not display Google button.", true);
      }

      // Optional: Display the One Tap prompt
      // google.accounts.id.prompt((notification) => {
      //     if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
      //         console.log("One Tap prompt was not displayed or was skipped:", notification.getNotDisplayedReason());
      //     } else {
      //          console.log("One Tap prompt displayed.");
      //     }
      // });

  } catch (error) {
      console.error("Error initializing Google Sign-In:", error);
      showStatus("Initialization error for Google Sign-In.", true);
  }
}

/**
* Handles the credential response from Google Sign-In (button or One Tap).
* Sends the ID token to the backend for verification and session creation.
* @param {object} response The credential response object from Google.
*/
async function handleCredentialResponse(response) {
  console.log("ID token received from Google.");
  showStatus("Verifying identity...");

  if (!response || !response.credential) {
      console.error("Invalid credential response received from Google:", response);
      showStatus("Authentication failed: Invalid response.", true);
      return;
  }

  try {
      const backendResponse = await fetch('/auth/verify-token', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
          },
          // Ensure the token is sent correctly nested in the JSON body
          body: JSON.stringify({ id_token_str: response.credential })
      });

      // Check if response is OK (status 200-299)
      if (backendResponse.ok) {
          const result = await backendResponse.json();
          console.log('Backend verification successful:', result);
          showStatus("Sign in successful! Redirecting...");

          // --- Redirect after successful login ---
          // Check if there's a 'next' URL parameter to redirect back to where the user was heading
          const urlParams = new URLSearchParams(window.location.search);
          const nextUrl = urlParams.get('next') || '/'; // Default to homepage '/' if no 'next' param

          // Perform the redirect
          window.location.href = nextUrl;
          // ----------------------------------------

      } else {
          // Handle backend errors (e.g., 401 Unauthorized, 500 Server Error)
          let errorDetail = `Server error ${backendResponse.status}`;
          try {
              const errorJson = await backendResponse.json();
              errorDetail = errorJson.detail || errorDetail; // Use detail from FastAPI's HTTPException if available
          } catch (e) {
              // If parsing JSON fails or no JSON body
               errorDetail = `${errorDetail}: ${backendResponse.statusText}`;
               console.warn("Could not parse error response body.");
          }
          console.error('Backend token verification failed:', errorDetail);
          showStatus(`Authentication failed: ${errorDetail}`, true);
      }
  } catch (networkError) {
      // Handle network errors (e.g., backend server down)
      console.error('Network error during token verification:', networkError);
      showStatus(`Network error: ${networkError.message}. Please try again.`, true);
  }
}

// Initialize Google Sign-In when the window loads.
// Using DOMContentLoaded might be slightly faster if CSS/images are slow,
// but window.onload ensures external scripts like GSI are likely loaded.
window.onload = initializeGoogleSignIn;