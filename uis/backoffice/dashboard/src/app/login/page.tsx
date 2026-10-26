import { redirect } from "next/navigation";
import { LoginForm } from "../../components/AuthForms";
import { getSession } from "../../lib/auth";

export const metadata = { title: "Sign in | Nexova Backoffice" };

export default async function LoginPage() {
  if (await getSession()) redirect("/");

  return (
    <main className="loginPage">
      <div className="loginContent">
        <div className="loginBrand">Nexova</div>
        <p className="eyebrow">Operations backoffice</p>
        <h1>Sign in</h1>
        <LoginForm />
      </div>
    </main>
  );
}
