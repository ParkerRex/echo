import { createFileRoute } from "@tanstack/react-router";

function SettingsComponent() {
  return (
    <div>
      <h1>Settings</h1>
      <p>This is the Settings page route.</p>
    </div>
  );
}

export const Route = createFileRoute("/settings")({
  component: SettingsComponent,
});
