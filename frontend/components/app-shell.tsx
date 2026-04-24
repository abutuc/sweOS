"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { AuthContextProvider } from "@/components/auth-context";
import { AuthPanel } from "@/components/auth-panel";
import { api, ApiError, type AuthUser } from "@/lib/api";
import { clearStoredToken, getStoredToken, getStoredUser } from "@/lib/session";

type AppShellProps = {
  children: React.ReactNode;
};

const NAV_ITEMS = [
  { href: "/", label: "Dashboard" },
  { href: "/practice", label: "Practice" },
  { href: "/profile", label: "Profile" },
  { href: "/settings", label: "Settings" },
];

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isBootstrapping, setIsBootstrapping] = useState(true);

  useEffect(() => {
    const token = getStoredToken();

    if (!token) {
      setIsBootstrapping(false);
      return;
    }

    const cachedUser = getStoredUser();
    if (cachedUser) {
      setUser(cachedUser);
      setIsBootstrapping(false);
    }

    void api
      .getMe()
      .then((response) => {
        setUser(response.data);
      })
      .catch((error) => {
        if (error instanceof ApiError && error.status === 401) {
          clearStoredToken();
        }
      })
      .finally(() => {
        if (!cachedUser) {
          setIsBootstrapping(false);
        }
      });
  }, []);

  const handleAuthenticated = (nextUser: AuthUser) => {
    setUser(nextUser);
    router.replace("/onboarding");
  };

  const handleLogout = () => {
    clearStoredToken();
    setUser(null);
    router.replace("/");
  };

  if (isBootstrapping) {
    return (
      <main className="page-shell">
        <section className="loading-panel">
          <p className="eyebrow">Booting</p>
          <h1>Restoring your engineering workspace.</h1>
        </section>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="page-shell">
        <AuthPanel onAuthenticated={handleAuthenticated} />
      </main>
    );
  }

  return (
    <AuthContextProvider value={{ user, setUser }}>
      <main className="page-shell page-shell-app">
        <header className="app-shell-header">
          <Link className="app-shell-brand" href="/">
            <span className="app-shell-brand-mark">sweOS</span>
            <div>
              <strong>Companion</strong>
              <p>Engineering operating system</p>
            </div>
          </Link>

          <nav className="app-shell-nav" aria-label="Primary">
            {NAV_ITEMS.map((item) => (
              <Link
                className={`app-shell-nav-item ${pathname === item.href ? "app-shell-nav-item-active" : ""}`}
                href={item.href}
                key={item.href}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="app-shell-identity">
            <div className="identity-chip">
              <span className="identity-chip-label">Active identity</span>
              <strong>{user.fullName ?? user.email}</strong>
            </div>
            <button className="ghost-button" type="button" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </header>

        {children}
      </main>
    </AuthContextProvider>
  );
}
