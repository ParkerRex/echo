import { createFileRoute } from "@tanstack/react-router";

import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/card";

function SettingsComponent() {
  return (
    <div className="max-w-2xl mx-auto py-8">
      <Card>
        <CardHeader>
          <CardTitle>Settings</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-gray-700">
              This is the Settings page. Future configuration options will appear here.
            </p>
            <ul className="list-disc pl-6 text-gray-600">
              <li>Profile and preferences (coming soon)</li>
              <li>Notification settings (coming soon)</li>
              <li>Project configuration (coming soon)</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export const Route = createFileRoute("/settings")({
  component: SettingsComponent,
});
