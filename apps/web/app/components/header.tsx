import { Link } from "@tanstack/react-router"
import { UserMenu } from "./user-menu"
import { useAuthentication } from "~/services/queries"
import { Button } from "./ui/button"

export function Header() {
  const { data: authData } = useAuthentication()

  return (
    <header className="border-b bg-white shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo/Brand */}
          <div className="flex items-center space-x-4">
            <Link
              to="/"
              className="text-xl font-bold text-gray-900 hover:text-gray-700"
            >
              Echo
            </Link>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            <Link
              to="/"
              className="text-gray-600 hover:text-gray-900 transition-colors"
              activeProps={{
                className: "text-blue-600 font-medium",
              }}
            >
              Home
            </Link>
            {authData.isAuthenticated && (
              <Link
                to="/dashboard"
                className="text-gray-600 hover:text-gray-900 transition-colors"
                activeProps={{
                  className: "text-blue-600 font-medium",
                }}
              >
                Dashboard
              </Link>
            )}
          </nav>

          {/* User Menu or Auth Buttons */}
          <div className="flex items-center">
            {authData.isAuthenticated ? (
              <UserMenu />
            ) : (
              <div className="flex items-center space-x-2">
                <Link to="/sign-in">
                  <Button variant="ghost">Sign In</Button>
                </Link>
                <Link to="/signup">
                  <Button>Sign Up</Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
} 