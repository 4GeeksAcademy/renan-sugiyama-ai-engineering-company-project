"use client";

import { useActionState } from "react";
import { login, logout } from "../app/login/actions";

export function LoginForm() {
  const [state, formAction, pending] = useActionState(login, { error: "" });

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
