import React, { useEffect, useState } from "react";
import { useNavigate } from "@tanstack/react-router";

type ProtectedLayoutProps = {
  children: React.ReactNode;
};

export function ProtectedLayout({ children }: ProtectedLayoutProps) {
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    async function checkAuth() {
      try {
        const res = await fetch("/auth/me", {
          credentials: "include",
        });
        if (res.ok) {
          setAuthenticated(true);
        } else {
          setAuthenticated(false);
          navigate({ to: "/login" });
        }
      } catch (err) {
        setAuthenticated(false);
        navigate({ to: "/login" });
      } finally {
        setLoading(false);
      }
    }
    checkAuth();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!authenticated) {
    return null;
  }

  return <>{children}</>;
}

export default ProtectedLayout;
