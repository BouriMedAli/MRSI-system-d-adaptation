# Git Branching Guide

This guide explains how to create a new branch in a Git repository and work on it without affecting the main branch.

## Steps to Create and Work on a New Branch

1. Clone the Repository (if not already cloned)
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Ensure You Are on the main Branch
   ```bash
   git checkout main
   ```

3. Pull the Latest Changes from main
   ```bash
   git pull origin main
   ```

4. Create and Switch to a New Branch
   ```bash
   git checkout -b <new-branch-name>
   ```

5. Make Your Changes
   - Modify or add files as needed.

6. Add and Commit Changes
   ```bash
   git add .
   git commit -m "Your commit message"
   ```

7. Push the New Branch to GitHub
   ```bash
   git push origin <new-branch-name>
   ```

8. Create a Pull Request (PR)
   - Go to your GitHub repository, find the new branch, and open a Pull Request (PR) to merge your changes into main.

9. Switch Back to main (When Needed)
   ```bash
   git checkout main
   ```

## Best Practices

- Always pull the latest changes before creating a new branch.
- Use meaningful branch names (e.g., feature-login-page, bugfix-user-auth).
- Regularly push your changes to avoid losing progress.
- Follow code review and merging guidelines.
