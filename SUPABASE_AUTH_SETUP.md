# 🔐 Supabase Auth Setup Guide

## 🎯 **What You'll Get:**
- ✅ **Email/Password Registration & Login**
- ✅ **Google OAuth Login**
- ✅ **Password Reset Functionality**
- ✅ **Email Verification**
- ✅ **Professional User Management**

## 🛠️ **Setup Steps:**

### **Step 1: Enable Supabase Auth**

1. **Go to Supabase Dashboard**
   - Visit: https://supabase.com/dashboard
   - Select your project: `lrowromhpwebukywmtem`

2. **Navigate to Authentication**
   - Click on "Authentication" in the left sidebar
   - Click on "Settings"

3. **Configure Site URL**
   - Set **Site URL** to: `https://your-app-name.streamlit.app`
   - For local development: `http://localhost:8501`
   - Add both URLs to **Redirect URLs**

### **Step 2: Enable Email/Password Auth**

1. **Go to Authentication → Providers**
2. **Enable Email Provider**
   - Toggle "Enable email confirmations" (recommended)
   - Set **Confirm email template** (optional)
   - Save changes

### **Step 3: Enable Google OAuth (Optional)**

1. **Get Google OAuth Credentials**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Google+ API
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
   - Set **Authorized redirect URIs** to:
     ```
     https://lrowromhpwebukywmtem.supabase.co/auth/v1/callback
     ```

2. **Configure in Supabase**
   - Go to Supabase → Authentication → Providers
   - Enable **Google** provider
   - Enter your **Client ID** and **Client Secret**
   - Save changes

### **Step 4: Update Database Policies**

Run this SQL in your Supabase SQL Editor:

```sql
-- Enable RLS on tables
ALTER TABLE content_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE token_usage ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated users
CREATE POLICY "Users can view own files" ON content_files
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can insert own files" ON content_files
    FOR INSERT WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can update own files" ON content_files
    FOR UPDATE USING (auth.uid()::text = user_id);

CREATE POLICY "Users can delete own files" ON content_files
    FOR DELETE USING (auth.uid()::text = user_id);

-- Token usage policies
CREATE POLICY "Users can view own token usage" ON token_usage
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can insert own token usage" ON token_usage
    FOR INSERT WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can update own token usage" ON token_usage
    FOR UPDATE USING (auth.uid()::text = user_id);

CREATE POLICY "Users can delete own token usage" ON token_usage
    FOR DELETE USING (auth.uid()::text = user_id);
```

### **Step 5: Test Authentication**

1. **Run your app:**
   ```bash
   streamlit run app.py
   ```

2. **Test Registration:**
   - Click "Register" tab
   - Enter email and password
   - Check email for verification

3. **Test Login:**
   - Click "Login" tab
   - Enter credentials
   - Should see user info

## 🔧 **Configuration Options:**

### **Email Templates (Optional)**
1. Go to Authentication → Email Templates
2. Customize:
   - **Confirm signup**
   - **Reset password**
   - **Change email address**

### **Password Policy**
1. Go to Authentication → Settings
2. Configure:
   - **Minimum password length** (default: 6)
   - **Password strength requirements**

### **Session Management**
1. Go to Authentication → Settings
2. Set:
   - **JWT expiry** (default: 3600 seconds)
   - **Refresh token expiry** (default: 60 days)

## 🚀 **Deployment Setup:**

### **For Streamlit Cloud:**

1. **Add secrets to Streamlit Cloud:**
   ```toml
   # .streamlit/secrets.toml
   SUPABASE_URL = "https://lrowromhpwebukywmtem.supabase.co"
   SUPABASE_KEY = "your-anon-key"
   ```

2. **Update Site URL in Supabase:**
   - Go to Authentication → Settings
   - Set Site URL to your Streamlit app URL
   - Add to Redirect URLs

### **For Local Development:**

1. **Set environment variables:**
   ```bash
   export SUPABASE_URL="https://lrowromhpwebukywmtem.supabase.co"
   export SUPABASE_KEY="your-anon-key"
   ```

2. **Update Site URL:**
   - Set to `http://localhost:8501`

## 🎯 **User Experience:**

### **Registration Flow:**
1. User clicks "Register"
2. Enters email and password
3. Receives verification email
4. Clicks verification link
5. Can now login

### **Login Flow:**
1. User clicks "Login"
2. Enters email and password
3. Gets authenticated
4. Sees personalized dashboard

### **Google OAuth Flow:**
1. User clicks "Login with Google"
2. Redirected to Google
3. Authorizes the app
4. Redirected back and logged in

### **Password Reset Flow:**
1. User clicks "Reset Password"
2. Enters email address
3. Receives reset email
4. Sets new password

## 🔒 **Security Features:**

### **Built-in Security:**
- ✅ **Email verification** required
- ✅ **Password hashing** (bcrypt)
- ✅ **JWT tokens** for sessions
- ✅ **CSRF protection**
- ✅ **Rate limiting**

### **Database Security:**
- ✅ **Row Level Security (RLS)**
- ✅ **User-specific data access**
- ✅ **Automatic user ID injection**

## 💰 **Cost Considerations:**

### **Free Tier Limits:**
- **Users**: Unlimited
- **Email**: 50,000 emails/month
- **OAuth**: Unlimited
- **Perfect for capstone projects**

### **Paid Plans:**
- **Pro**: $25/month for 100,000 users
- **Team**: $599/month for enterprise features

## 🐛 **Troubleshooting:**

### **Common Issues:**

1. **"Invalid redirect URL"**
   - Check Site URL in Supabase settings
   - Ensure redirect URLs include your app URL

2. **"Email not verified"**
   - Check spam folder
   - Resend verification email
   - Disable email confirmation for testing

3. **"Google OAuth not working"**
   - Verify Client ID and Secret
   - Check redirect URIs in Google Console
   - Ensure Google+ API is enabled

4. **"Database policies not working"**
   - Verify RLS is enabled
   - Check policy syntax
   - Test with authenticated user

### **Testing Commands:**
```bash
# Test Supabase connection
python test_supabase.py

# Test authentication
python -c "from supabase_auth import SupabaseAuth; print('Auth module loaded')"
```

## 🎉 **Benefits:**

### **For Your Capstone:**
- ✅ **Professional authentication** system
- ✅ **Real user accounts** with email/password
- ✅ **Google OAuth** integration
- ✅ **Production-ready** security
- ✅ **Scalable** user management

### **For Users:**
- ✅ **Easy registration** and login
- ✅ **Password reset** functionality
- ✅ **Google login** option
- ✅ **Secure** data access
- ✅ **Professional** experience

---

## 🚀 **Ready to Deploy!**

Your app now has **professional authentication** with:
- Email/password registration and login
- Google OAuth (after setup)
- Password reset functionality
- Email verification
- Secure user data isolation

**Perfect for a production-ready capstone project! 🎉** 