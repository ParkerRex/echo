2.2. Refine Authentication Callback Logic
* Goal: Ensure the OAuth callback page handles all states robustly.
* 2.2.1. Review Callback Logic for isInitialized:
* [x] Open apps/web/src/routes/auth/callback.tsx.
* [x] Confirm: The useEffect hook correctly uses the isInitialized flag from the useAuth() hook to prevent navigation decisions before the Supabase client has had a chance to process the incoming session from the OAuth redirect. The current code if (!isInitialized) { return; } looks correct.
* 2.2.2. Verify Handling of All States:
* [x] Review: In the same useEffect, check the logic for:
* authError is present (should redirect to login with an error toast).
* session is present (should redirect to dashboard with a success toast).
* Neither authError nor session is present after isInitialized is true (should redirect to login with an error toast, indicating a problem with session establishment).
* [x] (Self-check) The current code appears to handle these cases.
* 2.2.3. Test Callback Flow Manually:
* [ ] Action: Perform a Google login.
* [ ] Observe: Ensure you are correctly redirected to the dashboard after the callback.
* [ ] Observe: Check for appropriate toast messages.
* [ ] Test (if possible): Try to navigate to /auth/callback directly in your browser. It should redirect you to /login with an error message because there's no valid OAuth state to process.