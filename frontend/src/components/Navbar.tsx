import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { authAPI } from '@/lib/api';
import Cookies from 'js-cookie';

export default function Navbar() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const userId = Cookies.get('user_id');
    const user = Cookies.get('username');
    setIsAuthenticated(!!userId);
    setUsername(user || null);
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
          {mounted && isAuthenticated ? (
            <>
              <Link href="/dashboard" className="navbar-link">
                Dashboard
              </Link>
              {username && <span className="navbar-user">Welcome, {username}</span>}
              <button onClick={handleLogout} className="navbar-link btn-link">
                Logout
              </button>
            </>
          ) : mounted ? (
            <>
              <Link href="/login" className="navbar-link">
                Login
              </Link>
              <Link href="/register" className="navbar-link">
                Register
              </Link>
            </>
          ) : (
            <>
              <Link href="/login" className="navbar-link">
                Login
              </Link>
              <Link href="/register" className="navbar-link">
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

