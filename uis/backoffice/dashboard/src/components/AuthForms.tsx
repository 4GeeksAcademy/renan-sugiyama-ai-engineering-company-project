"use client";

import { useActionState, useEffect } from "react";
import { track } from "@nexova/telemetry";
import { setTelemetryContext } from "@nexova/telemetry/context";
import { login, logout } from "../app/login/actions";

export function LoginForm() {
  const [state, formAction, pending] = useActionState(login, { error: "" });

  useEffect(() => {
    if (state.deniedStatus !== 401) return;
    // No session exists before login; use an anonymous identity and a system session.
    setTelemetryContext({
      userId: "anonymous",
      sessionId: crypto.randomUUID(),
      expiresAt: new Date(Date.now() + 60_000).toISOString(),
      requestId: crypto.randomUUID(),
    });
    track("user_authentication_denied", {
      reason: "unknown_user",
      route: "/login",
      httpStatus: 401,
    });
    setTelemetryContext(null);
  }, [state]);

  return (
    <form action={formAction} className="loginForm">
      <div className="loginField">
        <label htmlFor="username">Username</label>
        <input
          id="username"
          name="username"
          autoComplete="username"
          autoCapitalize="none"
          spellCheck={false}
          maxLength={100}
          required
          aria-describedby={state.error ? "login-error" : undefined}
        />
      </div>
      <div className="loginField">
        <label htmlFor="password">Password</label>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="current-password"
          maxLength={1024}
          required
          aria-describedby={state.error ? "login-error" : undefined}
        />
      </div>
      <p id="login-error" className="authError" role="alert">
        {state.error}
      </p>
      <button className="ctaButton" type="submit" disabled={pending}>
        {pending ? "Signing in..." : "Sign in"}
      </button>
    </form>
  );
}

export function LogoutForm() {
  const [state, formAction, pending] = useActionState(logout, { error: "" });

  return (
    <form action={formAction} className="logoutForm">
      <button className="logoutButton" type="submit" disabled={pending}>
        {pending ? "Signing out..." : "Sign out"}
      </button>
      {state.error && <p role="alert">{state.error}</p>}
    </form>
  );
}
