"""
Supabase Authentication Module
Provides email/password and Google OAuth authentication
"""

import streamlit as st
from supabase import create_client, Client
import os
from typing import Optional, Dict, Any
import time

class SupabaseAuth:
    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize Supabase client for authentication."""
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.client = create_client(supabase_url, supabase_key)
    
    def sign_up_with_email(self, email: str, password: str) -> Dict[str, Any]:
        """Register a new user with email and password."""
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if response.user:
                st.success("✅ Account created successfully! Please check your email for verification.")
                return {
                    "success": True,
                    "user": response.user,
                    "message": "Account created successfully!"
                }
            else:
                st.error("❌ Failed to create account")
                return {
                    "success": False,
                    "error": "Failed to create account"
                }
                
        except Exception as e:
            error_msg = str(e)
            if "already registered" in error_msg.lower():
                st.error("❌ Email already registered. Please try logging in instead.")
            elif "password" in error_msg.lower():
                st.error("❌ Password must be at least 6 characters long.")
            else:
                st.error(f"❌ Registration failed: {error_msg}")
            
            return {
                "success": False,
                "error": error_msg
            }
    
    def sign_in_with_email(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in user with email and password."""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                st.success("✅ Login successful!")
                return {
                    "success": True,
                    "user": response.user,
                    "message": "Login successful!"
                }
            else:
                st.error("❌ Login failed")
                return {
                    "success": False,
                    "error": "Login failed"
                }
                
        except Exception as e:
            error_msg = str(e)
            if "invalid" in error_msg.lower():
                st.error("❌ Invalid email or password. Please try again.")
            elif "not confirmed" in error_msg.lower():
                st.error("❌ Please check your email and confirm your account first.")
            else:
                st.error(f"❌ Login failed: {error_msg}")
            
            return {
                "success": False,
                "error": error_msg
            }
    
    def sign_in_with_google(self) -> str:
        """Generate Google OAuth URL for sign in."""
        try:
            # Get the OAuth URL for Google
            response = self.client.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {
                    "redirect_to": f"{self.supabase_url}/auth/v1/callback"
                }
            })
            
            return response.url
            
        except Exception as e:
            st.error(f"❌ Google OAuth setup failed: {str(e)}")
            return None
    
    def sign_out(self) -> bool:
        """Sign out the current user."""
        try:
            self.client.auth.sign_out()
            st.success("✅ Logged out successfully!")
            return True
        except Exception as e:
            st.error(f"❌ Logout failed: {str(e)}")
            return False
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get the currently authenticated user."""
        try:
            user = self.client.auth.get_user()
            return user.user if user.user else None
        except Exception:
            return None
    
    def reset_password(self, email: str) -> Dict[str, Any]:
        """Send password reset email."""
        try:
            self.client.auth.reset_password_email(email)
            st.success("✅ Password reset email sent! Check your inbox.")
            return {
                "success": True,
                "message": "Password reset email sent!"
            }
        except Exception as e:
            st.error(f"❌ Failed to send reset email: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_password(self, password: str) -> Dict[str, Any]:
        """Update user password."""
        try:
            response = self.client.auth.update_user({
                "password": password
            })
            
            if response.user:
                st.success("✅ Password updated successfully!")
                return {
                    "success": True,
                    "message": "Password updated successfully!"
                }
            else:
                st.error("❌ Failed to update password")
                return {
                    "success": False,
                    "error": "Failed to update password"
                }
                
        except Exception as e:
            st.error(f"❌ Password update failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

def show_auth_ui():
    """Show the authentication UI with email/password and Google options."""
    
    # Initialize Supabase Auth
    supabase_url = "https://lrowromhpwebukywmtem.supabase.co"
    supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxyb3dyb21ocHdlYnVreXdtdGVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI5NzE5ODUsImV4cCI6MjA2ODU0Nzk4NX0.Pd74n0CbooCvF1AHFtRGpzCuzQJ7TjydZPzna16fp0I"
    
    auth = SupabaseAuth(supabase_url, supabase_key)
    
    # Check if user is already authenticated
    current_user = auth.get_current_user()
    
    if current_user:
        # User is already logged in
        st.success(f"✅ Welcome back, {current_user.email}!")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"**Email:** {current_user.email}")
            st.info(f"**User ID:** {current_user.id}")
            st.info(f"**Last Sign In:** {current_user.last_sign_in_at}")
        
        with col2:
            if st.button("🚪 Logout", type="secondary"):
                if auth.sign_out():
                    st.session_state['user_id'] = None
                    st.session_state['is_authenticated'] = False
                    st.rerun()
        
        # Set user ID for data isolation
        st.session_state['user_id'] = current_user.id
        st.session_state['is_authenticated'] = True
        st.session_state['user_email'] = current_user.email
        
        return True
    
    # User is not authenticated - show login/register options
    st.markdown("## 🔐 User Authentication")
    
    # Authentication tabs
    tab1, tab2, tab3 = st.tabs(["📧 Email/Password", "🔍 Google Login", "🆔 Quick Login"])
    
    with tab1:
        st.markdown("### 📧 Email/Password Authentication")
        
        # Choose between login and register
        auth_mode = st.radio(
            "Choose action:",
            ["Login", "Register", "Reset Password"],
            horizontal=True
        )
        
        if auth_mode == "Login":
            st.markdown("#### 🔑 Login to Your Account")
            
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="your.email@example.com")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                col1, col2 = st.columns(2)
                with col1:
                    login_submit = st.form_submit_button("🔑 Login", type="primary")
                with col2:
                    if st.form_submit_button("🔄 Demo Login"):
                        # Demo login for testing
                        st.session_state['user_id'] = f"demo_user_{int(time.time())}"
                        st.session_state['is_authenticated'] = True
                        st.session_state['user_email'] = "demo@example.com"
                        st.success("✅ Demo login successful!")
                        st.rerun()
                
                if login_submit and email and password:
                    result = auth.sign_in_with_email(email, password)
                    if result['success']:
                        st.session_state['user_id'] = result['user'].id
                        st.session_state['is_authenticated'] = True
                        st.session_state['user_email'] = result['user'].email
                        st.rerun()
        
        elif auth_mode == "Register":
            st.markdown("#### 📝 Create New Account")
            
            with st.form("register_form"):
                email = st.text_input("Email", placeholder="your.email@example.com")
                password = st.text_input("Password", type="password", placeholder="Create a password (min 6 characters)")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                
                if st.form_submit_button("📝 Register", type="primary"):
                    if not email or not password:
                        st.error("❌ Please fill in all fields")
                    elif password != confirm_password:
                        st.error("❌ Passwords do not match")
                    elif len(password) < 6:
                        st.error("❌ Password must be at least 6 characters long")
                    else:
                        result = auth.sign_up_with_email(email, password)
                        if result['success']:
                            st.info("📧 Please check your email to verify your account before logging in.")
        
        elif auth_mode == "Reset Password":
            st.markdown("#### 🔄 Reset Your Password")
            
            with st.form("reset_form"):
                email = st.text_input("Email", placeholder="your.email@example.com")
                
                if st.form_submit_button("📧 Send Reset Email", type="primary"):
                    if email:
                        auth.reset_password(email)
                    else:
                        st.error("❌ Please enter your email address")
    
    with tab2:
        st.markdown("### 🔍 Google OAuth Login")
        
        st.info("🔧 Google OAuth requires additional setup in Supabase dashboard.")
        st.markdown("""
        **To enable Google login:**
        
        1. Go to your Supabase Dashboard
        2. Navigate to Authentication → Providers
        3. Enable Google provider
        4. Add your Google OAuth credentials
        5. Configure redirect URLs
        
        **For now, use Email/Password or Quick Login options.**
        """)
        
        # Placeholder for Google OAuth
        if st.button("🔍 Login with Google (Coming Soon)", disabled=True):
            st.info("Google OAuth will be available after setup in Supabase dashboard.")
    
    with tab3:
        st.markdown("### 🆔 Quick Login (Session-Based)")
        
        st.info("💡 Quick login creates a temporary session for immediate use.")
        
        # Simple username-based login
        username = st.text_input("Enter a username:", placeholder="e.g., john_doe")
        
        if st.button("🚀 Quick Login", type="primary"):
            if username and len(username) > 2:
                st.session_state['user_id'] = f"user_{username}_{int(time.time())}"
                st.session_state['is_authenticated'] = True
                st.session_state['user_email'] = f"{username}@quicklogin.local"
                st.success(f"✅ Quick login successful as {username}!")
                st.rerun()
            else:
                st.error("❌ Please enter a valid username (at least 3 characters)")
    
    return False

# Global auth instance
auth_instance = None

def get_auth_instance():
    """Get or create global auth instance."""
    global auth_instance
    if auth_instance is None:
        supabase_url = "https://lrowromhpwebukywmtem.supabase.co"
        supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxyb3dyb21ocHdlYnVreXdtdGVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI5NzE5ODUsImV4cCI6MjA2ODU0Nzk4NX0.Pd74n0CbooCvF1AHFtRGpzCuzQJ7TjydZPzna16fp0I"
        auth_instance = SupabaseAuth(supabase_url, supabase_key)
    return auth_instance 