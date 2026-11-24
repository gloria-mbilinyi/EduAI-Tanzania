import { createContext, useContext, useState, ReactNode } from "react";
import { post, Row } from "../services/api";
const Context = createContext<{
  user: Row | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  update: (u: Row) => void;
}>(null!);
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<Row | null>(() => {
    try {
      return JSON.parse(sessionStorage.getItem("eduai-user") || "null");
    } catch {
      return null;
    }
  });
  const update = (u: Row) => {
    setUser(u);
    sessionStorage.setItem("eduai-user", JSON.stringify(u));
    if (u.language) {
      localStorage.setItem("eduai-language", u.language);
      window.dispatchEvent(new Event("eduai-language"));
    }
  };
  async function login(email: string, password: string) {
    const r = await post("/auth/login", { email, password });
    sessionStorage.setItem("eduai-token", r.access_token);
    update(r.user);
  }
  function logout() {
    sessionStorage.removeItem("eduai-token");
    sessionStorage.removeItem("eduai-user");
    setUser(null);
  }
  return (
    <Context.Provider value={{ user, login, logout, update }}>
      {children}
    </Context.Provider>
  );
}
export const useAuth = () => useContext(Context);
