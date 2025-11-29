import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { authAPI } from '@/lib/api';
import { useTheme } from '@/context/ThemeContext';

export default function Navbar() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);
  const { theme, toggleTheme } = useTheme();

  useEffect(() => {
    setMounted(true);

    // Ask backend who the current user is; rely on session cookie there,
    // but keep the UI decision based only on this flag.
    const checkAuth = async () => {
      try {
        const me = await authAPI.getCurrentUser();
        setIsAuthenticated(true);
        setUsername(me.username);
      } catch {
        setIsAuthenticated(false);
        setUsername(null);
      } finally {
        setAuthChecked(true);
      }
    };

    checkAuth();
  }, []);

  const handleLogout = () => {
    authAPI.logout();
    setIsAuthenticated(false);
    setUsername(null);
    router.push('/');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link href="/" className="navbar-brand">
          TrueTrace AI
        </Link>
        
        <div className="navbar-links">
          <button
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label="Toggle theme"
          >
            {theme === 'light' ? 'Dark Mode' : 'Light Mode'}
          </button>

          {mounted && authChecked ? (
            isAuthenticated ? (
              <>
                <Link href="/dashboard" className="navbar-link">
                  Dashboard
                </Link>
                <Link href="/multimodal-check" className="navbar-link">
                  Multimodal Checker
                </Link>
                {username && <span className="navbar-user">Welcome, {username}</span>}
                <button onClick={handleLogout} className="navbar-link btn-link">
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link href="/login" className="navbar-link">
                  Login
                </Link>
                <Link href="/register" className="navbar-link">
                  Register
                </Link>
                <Link href="/multimodal-check" className="navbar-link">
                  Multimodal Checker
                </Link>
              </>
            )
          ) : (
            // Before we know auth state, avoid flashing Login/Register
            <>
              <Link href="/multimodal-check" className="navbar-link">
                Multimodal Checker
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

