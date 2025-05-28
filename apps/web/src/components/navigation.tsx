import React from "react";
import { Link } from "@tanstack/react-router";
import { cn } from "src/lib/utils";
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  navigationMenuTriggerStyle,
} from "./ui/navigation-menu";

export const Navigation = () => {
  return (
    <NavigationMenu>
      <NavigationMenuList>
        <NavigationMenuItem>
          <Link
            to="/dashboard"
            className={navigationMenuTriggerStyle()}
          >
            Dashboard
          </Link>
        </NavigationMenuItem>
        <NavigationMenuItem>
          <NavigationMenuTrigger>Account</NavigationMenuTrigger>
          <NavigationMenuContent>
            <ul className="flex flex-col gap-2 p-4 w-[350px]">
              <Link to="/settings">
                <ListItem title="Settings">Manage your account settings.</ListItem>
              </Link>
              <Link to="/dashboard">
                <ListItem title="Videos">
                  Access your video content.
                </ListItem>
              </Link>
              <Link to="/logout">
                <ListItem title="Logout">Sign out of your account.</ListItem>
              </Link>
            </ul>
          </NavigationMenuContent>
        </NavigationMenuItem>
        <NavigationMenuItem>
          <Link
            to="/login"
            className={navigationMenuTriggerStyle()}
          >
            Login
          </Link>
        </NavigationMenuItem>
      </NavigationMenuList>
    </NavigationMenu>
  );
};

const ListItem = React.forwardRef<
  React.ElementRef<"li">,
  React.ComponentPropsWithoutRef<"li">
>(({ className, title, children, ...props }, ref) => {
  return (
    <li
      className={cn(
        "block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground",
        className,
      )}
      {...props}
    >
      <div className="text-sm font-medium leading-none">{title}</div>
      <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
        {children}
      </p>
    </li>
  );
});
ListItem.displayName = "ListItem";
