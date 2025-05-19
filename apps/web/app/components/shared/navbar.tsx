import { cn } from "~/lib/utils";
import { Link } from "@tanstack/react-router";
import { Home, Menu, Search, X } from "lucide-react";
import { useState } from "react";
import { Button } from "../ui/button";
import Container from "./container";

type Props = {};

export default function Navbar({}: Props) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const navItems = [
    {
      label: "Home",
      href: "/",
    },
    {
      label: "Upload",
      href: "/upload",
    },
    {
      label: "Dashboard",
      href: "/dashboard",
    },
    {
      label: "Settings",
      href: "/settings",
    },
  ];

  return (
    <div className="w-full bg-background/90 backdrop-blur-sm border-b border-border/40 sticky top-0 z-50">
      <Container className="flex h-16 items-center justify-between">
        {/* Logo */}
        <div className="flex items-center">
          <Link to="/" className="flex items-center space-x-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary">
              <Home className="h-4 w-4 text-primary-foreground" />
            </div>
            <span className="font-bold text-lg tracking-tight">UrcKe</span>
          </Link>
        </div>

        {/* Desktop navigation */}
        <nav className="hidden md:flex">
          <ul className="flex items-center space-x-8">
            {navItems.map((item) => (
              <li key={item.href}>
                <Link
                  to={item.href}
                  className={
                    "text-sm font-medium transition-colors hover:text-primary"
                  }
                  activeOptions={{ exact: true }}
                  activeProps={{
                    className: "text-primary font-semibold",
                  }}
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        {/* Actions */}
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" className="hidden md:flex">
            <Search className="h-4 w-4" />
            <span className="sr-only">Search</span>
          </Button>
          <Button className="hidden md:flex">Get Started</Button>

          {/* Mobile menu button */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? (
              <X className="h-5 w-5" />
            ) : (
              <Menu className="h-5 w-5" />
            )}
            <span className="sr-only">Toggle menu</span>
          </Button>
        </div>
      </Container>

      {/* Mobile navigation */}
      <div
        className={cn(
          "md:hidden border-t border-border/40",
          isMenuOpen ? "block" : "hidden",
        )}
      >
        <Container className="py-4 px-6 space-y-4">
          <nav>
            <ul className="space-y-4">
              {navItems.map((item) => (
                <li key={item.href}>
                  <Link
                    to={item.href}
                    className="block text-sm font-medium transition-colors hover:text-primary"
                    activeOptions={{ exact: true }}
                    activeProps={{
                      className: "text-primary font-semibold",
                    }}
                    onClick={() => setIsMenuOpen(false)}
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
          <div className="flex flex-col space-y-3 pt-3 border-t border-border/40">
            <Button
              variant="outline"
              className="w-full justify-start"
              size="sm"
            >
              <Search className="mr-2 h-4 w-4" />
              Search
            </Button>
            <Button className="w-full" size="sm">
              Get Started
            </Button>
          </div>
        </Container>
      </div>
    </div>
  );
}
