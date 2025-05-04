// Ensure the DOM is fully loaded before running scripts
document.addEventListener('DOMContentLoaded', () => {
  console.log("LearnSphere scripts initialized.");

  // --- Dark/Light Mode Toggle ---
  const themeToggleBtn = document.getElementById('theme-toggle');
  const htmlElement = document.documentElement;

  const setTheme = (isDark) => {
      // Add or remove the 'dark' class on the root HTML element
      if (isDark) {
          htmlElement.classList.add('dark');
          htmlElement.classList.remove('light'); // Ensure 'light' is removed
          localStorage.setItem('color-theme', 'dark'); // Store preference
      } else {
          htmlElement.classList.add('light'); // Ensure 'light' is added
          htmlElement.classList.remove('dark'); // Ensure 'dark' is removed
          localStorage.setItem('color-theme', 'light'); // Store preference
      }

      // Optional: Update icon/text within the toggle button if they exist
      const themeToggleDarkIcon = document.getElementById('theme-toggle-dark-icon');
      const themeToggleLightIcon = document.getElementById('theme-toggle-light-icon');
      const themeText = document.getElementById('theme-text'); // Assuming you might have a text label

      if (themeToggleDarkIcon && themeToggleLightIcon) {
          if (isDark) {
              themeToggleLightIcon.classList.remove('hidden');
              themeToggleDarkIcon.classList.add('hidden');
          } else {
              themeToggleDarkIcon.classList.remove('hidden');
              themeToggleLightIcon.classList.add('hidden');
          }
      }

      if (themeText) {
           themeText.textContent = isDark ? 'Light Mode' : 'Dark Mode';
      }
  };

  // Check initial theme preference on load
  const storedTheme = localStorage.getItem('color-theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

  if (storedTheme) {
      // If theme is stored, use it
      setTheme(storedTheme === 'dark');
  } else {
      // If no theme is stored, use system preference
      setTheme(prefersDark);
  }

  // Listen for toggle button click
  if (themeToggleBtn) {
      themeToggleBtn.addEventListener('click', () => {
          const isCurrentlyDark = htmlElement.classList.contains('dark');
          setTheme(!isCurrentlyDark); // Toggle the theme

          // Optional: Add button animation on click
          themeToggleBtn.classList.add('animate-scale-up');
          setTimeout(() => {
              themeToggleBtn.classList.remove('animate-scale-up');
          }, 400); // Duration should match CSS animation duration
      });
  }

  // Listen for system theme changes (optional)
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      // Only update if the user hasn't explicitly set a theme preference
      if (!localStorage.getItem('color-theme')) {
          setTheme(e.matches);
      }
  });


  // --- Mobile Menu Toggle (Main Navigation) ---
  const mobileMenuButton = document.getElementById('mobile-menu-button');
  const mobileMenu = document.getElementById('mobile-menu');

  if (mobileMenuButton && mobileMenu) {
      mobileMenuButton.addEventListener('click', () => {
          mobileMenu.classList.toggle('hidden');
          // Optional: Add animation class for opening
          mobileMenu.classList.toggle('animate-fade-in'); // Assuming animate-fade-in is defined

          // Optional: Prevent scrolling when menu is open
          if (!mobileMenu.classList.contains('hidden')) {
               document.body.classList.add('overflow-hidden');
          } else {
               document.body.classList.remove('overflow-hidden');
          }
      });

      // Close menu on outside click or link click
      document.addEventListener('click', (event) => {
           const isClickInsideMenu = mobileMenu.contains(event.target);
           const isClickOnButton = mobileMenuButton.contains(event.target);
           const isClickOnLink = event.target.tagName === 'A' && mobileMenu.contains(event.target);

           if (!isClickInsideMenu && !isClickOnButton && !mobileMenu.classList.contains('hidden')) {
               mobileMenu.classList.add('hidden');
               document.body.classList.remove('overflow-hidden'); // Restore scrolling
           } else if (isClickOnLink) {
               // Automatically close menu when a link is clicked
               mobileMenu.classList.add('hidden');
               document.body.classList.remove('overflow-hidden'); // Restore scrolling
           }
      });
  }


  // --- Profile Sidebar Toggle (for Profile Page - Mobile) ---
  // Note: This functionality is typically for a profile page, not the homepage.
  // Including here based on the provided code, but ensure it's only on profile.html
  const profileSidebarToggleBtn = document.getElementById('profile-sidebar-toggle');
  const profileSidebar = document.getElementById('profile-sidebar');
  const profileSidebarOverlay = document.getElementById('profile-sidebar-overlay');

  // Function to open the profile sidebar (mobile)
  const openProfileSidebar = () => {
       if (profileSidebar && profileSidebarOverlay) {
           profileSidebar.classList.remove('-translate-x-full');
           profileSidebar.classList.add('translate-x-0');
           profileSidebarOverlay.classList.remove('hidden');
            // Prevent body scroll when sidebar is open
            document.body.classList.add('overflow-hidden');
       }
  };

  // Function to close the profile sidebar (mobile)
  const closeProfileSidebar = () => {
      if (profileSidebar && profileSidebarOverlay) {
           profileSidebar.classList.add('-translate-x-full');
           profileSidebar.classList.remove('translate-x-0');
           profileSidebarOverlay.classList.add('hidden');
            // Restore body scroll
           document.body.classList.remove('overflow-hidden');
       }
  };

  // Listen for profile sidebar toggle button click (mobile)
  if (profileSidebarToggleBtn) { // Ensure the button exists on this page
      profileSidebarToggleBtn.addEventListener('click', () => {
          // Check if it's currently hidden on mobile (based on transform class)
           if (profileSidebar && profileSidebar.classList.contains('-translate-x-full')) {
               openProfileSidebar();
           } else {
               closeProfileSidebar();
           }
      });
  }

  // Listen for clicks on the overlay to close the sidebar (mobile)
  // This is the intended "click outside" behavior for a fixed mobile sidebar
  if (profileSidebarOverlay) { // Ensure the overlay exists
      profileSidebarOverlay.addEventListener('click', () => {
          closeProfileSidebar();
      });
  }


  // --- Profile Tabs/Sidebar Navigation Functionality (for Profile Page) ---
  // Note: This functionality is typically for a profile page, not the homepage.
  // Including here based on the provided code.
   const profileTabs = document.querySelectorAll('.profile-tab'); // Horizontal tabs (from earlier version)
   const sidebarLinks = document.querySelectorAll('.sidebar-link'); // Sidebar links
  const contentBlocks = document.querySelectorAll('.profile-content-block');
  const profileContentArea = document.getElementById('profile-content');

  // Function to show content block based on data-tab attribute
  const showContent = (tabId) => {
      contentBlocks.forEach(block => {
          if (block.id === `${tabId}-content`) {
              block.classList.remove('hidden');
              // Restore display property based on initial classes (grid, flex, block)
               if (block.classList.contains('grid')) {
                   block.style.display = 'grid';
               } else if (block.classList.contains('flex')) {
                   block.style.display = 'flex';
               } else {
                   block.style.display = 'block'; // Default to block
               }

          } else {
              block.classList.add('hidden');
              block.style.display = 'none'; // Ensure it's truly hidden
          }
      });
  };

  // Function to set active style for EITHER tabs or sidebar links
  const setActiveStyle = (activeElement) => {
      // Remove active class from all horizontal tabs
       if (profileTabs) {
           profileTabs.forEach(tab => {
               tab.classList.remove('active-tab');
                // Assuming active-tab manages primary color and border-bottom
           });
       }
      // Remove active class from all sidebar links
      if (sidebarLinks) {
          sidebarLinks.forEach(link => {
              link.classList.remove('active-link'); // Assuming active-link manages background and color
          });
      }

      // Add active class to the clicked element
      activeElement.classList.add(activeElement.classList.contains('profile-tab') ? 'active-tab' : 'active-link');
  };


  // Add click listeners to horizontal tabs (if they exist)
  if (profileTabs) {
      profileTabs.forEach(tab => {
          tab.addEventListener('click', () => {
              const tabId = tab.dataset.tab;
              showContent(tabId);
              setActiveStyle(tab);
          });
      });
  }


  // Add click listeners to sidebar links (if they exist)
  if (sidebarLinks) {
      sidebarLinks.forEach(link => {
          link.addEventListener('click', (event) => {
              event.preventDefault(); // Prevent default link behavior

              const tabId = link.dataset.tab;

              // Special handling for 'logout'
              if (tabId === 'logout') {
                   // In a real app, this would trigger a logout action or modal
                   // For this example, we'll just switch to the logout content block
                   showContent(tabId);
                   setActiveStyle(link);
                   // Optionally, close the mobile sidebar after clicking logout
                   if (window.innerWidth < 768) {
                        closeProfileSidebar(); // Use the profile sidebar close function
                   }
                   return; // Stop further execution for logout
              }

              showContent(tabId);
              setActiveStyle(link);

              // Close the mobile sidebar after clicking a link
               if (window.innerWidth < 768) { // Adjust breakpoint as needed (md in Tailwind)
                   closeProfileSidebar(); // Use the profile sidebar close function
                   // Optional: Scroll to the content area or top of the page on mobile
                   // if(profileContentArea) profileContentArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
               }
          });
      });
  }


  // Set the initial active element and content (e.g., the first tab or sidebar link)
  // Prioritize sidebar link if it exists, otherwise use tab
  const initialElement = document.querySelector('.sidebar-link') || document.querySelector('.profile-tab');
  if (initialElement) {
      const initialTabId = initialElement.dataset.tab;
      setActiveStyle(initialElement);
      showContent(initialTabId);
  }


  // --- Scroll Animations ---
  const scrollAnimationsObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
          if (entry.isIntersecting) {
              entry.target.classList.add('animate-fade-in');
              scrollAnimationsObserver.unobserve(entry.target); // Unobserve once animated
          }
      });
  }, { threshold: 0.1 }); // Adjust threshold as needed

  document.querySelectorAll('.scroll-animate').forEach(el => scrollAnimationsObserver.observe(el));


  // --- Image Lazy Loading ---
  const lazyImages = [].slice.call(document.querySelectorAll('img.lazy'));

  if ('IntersectionObserver' in window) {
      let lazyImageObserver = new IntersectionObserver(function(entries) {
          entries.forEach(function(entry) {
              if (entry.isIntersecting && entry.target.dataset.src) { // Check for data-src
                  let lazyImage = entry.target;
                  lazyImage.src = lazyImage.dataset.src;
                  lazyImage.classList.remove('lazy'); // Remove lazy class once loaded
                  lazyImageObserver.unobserve(lazyImage);
              }
          });
      });

      lazyImages.forEach(function(lazyImage) {
          lazyImageObserver.observe(lazyImage);
      });
  } else {
      // Fallback for browsers that don't support IntersectionObserver
      lazyImages.forEach(function(lazyImage) {
           if (lazyImage.dataset.src) {
              lazyImage.src = lazyImage.dataset.src;
           }
      });
  }

  // --- Static Drag and Drop Representation (for Categories in Settings) ---
  // Note: This is purely for visual representation and does NOT implement actual drag/drop functionality.
  // Implementing drag and drop requires significant JavaScript logic.
  // The HTML elements have `draggable="true"` and cursor styles for visual cues.

});


window.handleGoogleSignIn = async function() {
    clearMessages(); // Clear previous messages
    try {
        showStatus('Signing in with Google...');
        const result = await signInWithPopup(fbAuth, googleProvider);
        const user = result.user;
        console.log('Google Sign-in successful:', user); // Check browser console for this message

        // Get ID token
        const idToken = await user.getIdToken();
        console.log('Obtained ID Token:', idToken); // Check browser console if token is obtained

        // Send ID token to backend
        const success = await sendIdTokenToBackend(idToken, '/auth/google', { id_token: idToken }); // Pass payload explicitly

         if (success) {
             // Redirect to profile page after successful backend processing
             window.location.href = '/profile';
         } else {
             // Handle backend error after successful Firebase Google sign-in
             // The sendIdTokenToBackend function already shows the error message
             // No need to show another here unless specific client-side handling is needed
         }

    } catch (error) {
        console.error('Google Sign-in error:', error); // Check browser console for the original error
        // Handle specific error codes, e.g., popup closed by user
        if (error.code === 'auth/popup-closed-by-user') {
             showError('Google Sign-in popup was closed.');
        } else {
             showError(`Google Sign-in failed: ${error.message}`); // This is the message you are seeing
        }
    }
}

// The sendIdTokenToBackend function should look something like this (from previous code):
const sendIdTokenToBackend = async (idToken, endpoint, bodyPayload = {}) => { // Added bodyPayload parameter
    try {
        const resp = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${idToken}` // Still good practice to send in header
            },
            body: JSON.stringify(bodyPayload) // Use the passed payload
        });

        if (!resp.ok) {
            const errorData = await resp.json();
            console.error(`Backend error from ${endpoint}:`, errorData); // Log backend error
            showError(`Backend error: ${errorData.detail || resp.statusText}`);
            return false; // Indicate failure
        }

        console.log(`ID token sent to backend endpoint ${endpoint} successfully.`);
        return true; // Indicate success

    } catch (err) {
        console.error(`Error sending ID token to backend ${endpoint}:`, err);
        showError(`Failed to communicate with the server: ${err.message}`);
        return false; // Indicate failure
    }
};