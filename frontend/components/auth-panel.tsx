"use client";

import { useState } from "react";

import { api, ApiError, type AuthUser } from "@/lib/api";

type AuthPanelProps = {
  onAuthenticated: (user: AuthUser, mode: "login" | "register") => void;
};

export function AuthPanel({ onAuthenticated }: AuthPanelProps) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isRegister = mode === "register";

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      const response = isRegister
        ? await api.register({
            email: email.trim(),
            password,
            fullName: fullName.trim() || undefined,
          })
        : await api.login({ email: email.trim(), password });

      onAuthenticated(response.data.user, mode);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Authentication failed.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="auth-panel">
      <div className="auth-panel-copy">
        <p className="brand">sweOS COMPANION</p>
        <h1>
          Engineer your next role with a system that remembers where you are
          headed.
        </h1>
        <p>
          Profile direction, calibrated skills, and goal momentum in one
          operating surface built for modern software engineers.
        </p>
      </div>

      <div className="auth-card">
        <div className="auth-card-header">
          <div>
            <p className="section-kicker">Identity</p>
            <h2>
              {isRegister ? "Create your workspace" : "Enter your workspace"}
            </h2>
          </div>
          <div
            className="mode-toggle"
            role="tablist"
            aria-label="Authentication mode"
          >
            <button
              className={mode === "login" ? "mode-toggle-active" : ""}
              type="button"
              onClick={() => setMode("login")}
            >
              Login
            </button>
            <button
              className={mode === "register" ? "mode-toggle-active" : ""}
              type="button"
              onClick={() => setMode("register")}
            >
              Register
            </button>
          </div>
        </div>

        <div className="field-grid auth-grid">
          {isRegister ? (
            <label className="field field-wide">
              <span>Full name</span>
              <input
                value={fullName}
                onChange={(event) => setFullName(event.target.value)}
                placeholder="John Doe"
              />
            </label>
          ) : null}
          <label className="field field-wide">
            <span>Email</span>
            <input
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="john.doe@mail.com"
              type="email"
            />
          </label>
          <label className="field field-wide">
            <span>Password</span>
            <input
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Minimum 8 characters"
              type="password"
            />
          </label>
        </div>

        <p
          className={`inline-feedback ${error ? "inline-feedback-error" : ""}`}
        >
          {error ??
            (isRegister
              ? "Create an identity to start shaping your engineer profile."
              : "Use your account to unlock your profile, skills, and goals.")}
        </p>

        <div className="section-actions section-actions-left">
          <button
            className="primary-button"
            type="button"
            onClick={handleSubmit}
            disabled={
              isSubmitting ||
              email.trim().length === 0 ||
              password.trim().length < 8
            }
          >
            {isSubmitting
              ? "Working..."
              : isRegister
                ? "Create account"
                : "Login"}
          </button>
        </div>
      </div>
    </section>
  );
}
