# 🧪 OAuth Flow Testing Guide

**Incident ID**: INC-2025-001  
**Testing Phase**: Manual OAuth Flow Validation  
**Date**: 2025-01-27  

## 🎯 **Testing Objective**

Verify that the OAuth flow state validation failure has been resolved and that Google OAuth authentication works end-to-end.

## ✅ **Pre-Testing Checklist**

- [x] Supabase services running on http://127.0.0.1:54321
- [x] Frontend development server running on http://localhost:3000
- [x] All VITE_ environment variables configured
- [x] `skip_nonce_check = true` enabled in Supabase config
- [x] Google OAuth client credentials configured

## 🔬 **Test Scenarios**

### **Test 1: OAuth Initiation**
**Objective**: Verify Google OAuth flow can be initiated successfully

**Steps**:
1. Open http://localhost:3000/login in browser
2. Click "Sign in with Google" button
3. Verify redirect to Google OAuth consent screen

**Expected Result**: 
- ✅ Redirect to Google OAuth happens without errors
- ✅ Google consent screen displays correctly
- ✅ No JavaScript errors in browser console

**Actual Result**: _[To be filled during testing]_

---

### **Test 2: OAuth Callback Processing**
**Objective**: Verify the callback processing works without flow state errors

**Steps**:
1. Complete Google OAuth consent (grant permissions)
2. Verify redirect to http://localhost:3000/auth/callback
3. Monitor browser console for errors
4. Check for successful session creation

**Expected Result**:
- ✅ Redirect to /auth/callback occurs
- ✅ No "invalid flow state" errors
- ✅ `exchangeCodeForSession(code)` succeeds
- ✅ User session is created successfully

**Actual Result**: _[To be filled during testing]_

---

### **Test 3: Session Persistence**
**Objective**: Verify authenticated session persists correctly

**Steps**:
1. After successful OAuth, verify redirect to dashboard
2. Refresh the page
3. Navigate to protected routes
4. Check session persistence

**Expected Result**:
- ✅ Redirect to /dashboard after authentication
- ✅ Session persists after page refresh
- ✅ Protected routes accessible
- ✅ User information displayed correctly

**Actual Result**: _[To be filled during testing]_

---

### **Test 4: Error Resolution Verification**
**Objective**: Confirm the original error is completely resolved

**Steps**:
1. Complete full OAuth flow multiple times
2. Test with different Google accounts
3. Verify no occurrence of original error message

**Expected Result**:
- ✅ No "invalid flow state, no valid flow state found" errors
- ✅ Consistent successful authentication
- ✅ No PKCE flow validation failures

**Actual Result**: _[To be filled during testing]_

## 🐛 **Debugging Information**

### **Browser Console Monitoring**
Monitor for these specific messages:
- ✅ "Found OAuth code, exchanging for session..."
- ❌ "AuthApiError: invalid flow state, no valid flow state found"
- ✅ "Welcome, [username]!"

### **Network Tab Monitoring**
Check these API calls:
- `POST /auth/v1/token` (OAuth token exchange)
- `GET /auth/v1/user` (User session verification)

### **Supabase Logs**
Monitor Supabase logs for:
- OAuth flow initiation
- PKCE challenge/response validation
- Session creation events

## 📊 **Test Results Summary**

| Test Scenario | Status | Notes |
|---------------|--------|-------|
| OAuth Initiation | ⏳ Pending | |
| Callback Processing | ⏳ Pending | |
| Session Persistence | ⏳ Pending | |
| Error Resolution | ⏳ Pending | |

## 🚨 **If Tests Fail**

### **Common Issues & Solutions**

1. **Environment Variables Not Loaded**
   - Restart development server
   - Verify .env file is in correct location

2. **Supabase Configuration Not Applied**
   - Run `supabase stop && supabase start`
   - Verify config.toml changes

3. **Google OAuth Client Issues**
   - Check Google Cloud Console OAuth settings
   - Verify redirect URIs match exactly

## ✅ **Success Criteria**

All tests must pass with:
- ✅ No "invalid flow state" errors
- ✅ Successful OAuth flow completion
- ✅ Proper session creation and persistence
- ✅ Access to protected routes

---

**Testing Status**: Ready for Manual Testing  
**Next Step**: Execute test scenarios and document results
