"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { authRequest, SESSION_COOKIE, type AuthSession } from "../../lib/auth";

export type AuthFormState = { error: string; deniedStatus?: 401 };

export async function login(
  _previousState: AuthFormState,
  formData: FormData,
): Promise<AuthFormState> {
  const username = formData.get("username");
  const password = formData.get("password");
  if (
    typeof username !== "string" ||
    !username.trim() ||
    username.trim().length > 100 ||
    typeof password !== "string" ||
    !password ||
    password.length > 1024
  ) {
    return { error: "Enter a valid username and password." };
  }

  let session: AuthSession & { token: string };
  try {
    const response = await authRequest("/login", {
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: username.trim(), password }),
    });
    if (response.status === 401) {
      return { error: "Invalid username or password.", deniedStatus: 401 };
    }
    if (!response.ok) {
      return { error: "Sign-in is unavailable. Please try again later." };
    }
    session = await response.json();
  } catch {
    return { error: "Sign-in is unavailable. Please try again later." };
  }

  (await cookies()).set(SESSION_COOKIE, session.token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    expires: new Date(session.expiresAt),
  });
  redirect("/");
}

export async function logout(
  _previousState: AuthFormState,
  _formData: FormData,
): Promise<AuthFormState> {
  const cookieStore = await cookies();
  const token = cookieStore.get(SESSION_COOKIE)?.value;
  if (token) {
    try {
      const response = await authRequest("/logout", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) {
        return { error: "Could not sign out. Please try again." };
      }
    } catch {
      return { error: "Could not sign out. Please try again." };
    }
  }
  cookieStore.delete(SESSION_COOKIE);
  redirect("/login");
}
