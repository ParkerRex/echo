import { createFileRoute } from "@tanstack/react-router";

import { Button } from "~/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Input } from "~/components/ui/input";
import { Label } from "~/components/ui/label";
import { Separator } from "~/components/ui/separator";
import { Switch } from "~/components/ui/switch";
// import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "~/components/ui/select"; // Placeholder for future use

function SettingsComponent() {
  return (
    <div className="container mx-auto py-8 max-w-4xl space-y-8">
      <h1 className="text-3xl font-bold">Settings</h1>

      {/* Profile & Preferences Section */}
      <Card>
        <CardHeader>
          <CardTitle>Profile & Preferences</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="displayName">Display Name</Label>
            <Input
              id="displayName"
              placeholder="Your Name (coming soon)"
              disabled
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="your.email@example.com (coming soon)"
              disabled
            />
          </div>
          <div className="flex items-center justify-between space-x-2 pt-2">
            <Label htmlFor="darkMode" className="flex flex-col space-y-1">
              <span>Dark Mode</span>
              <span className="font-normal leading-snug text-muted-foreground">
                Adjust the appearance to reduce eye strain.
              </span>
            </Label>
            <Switch id="darkMode" disabled />
          </div>
        </CardContent>
      </Card>

      {/* YouTube Integration Section */}
      <Card>
        <CardHeader>
          <CardTitle>YouTube Integration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Connected Account</Label>
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                youtube-channel-name (coming soon)
              </p>
              <Button variant="outline" size="sm" disabled>
                Reconnect
              </Button>
            </div>
          </div>
          <Separator />
          <div className="space-y-2">
            <Label htmlFor="defaultPrivacy">Default Upload Privacy</Label>
            {/* Placeholder for Select component */}
            <Input
              id="defaultPrivacy"
              placeholder="Private (coming soon)"
              disabled
            />
            {/* <Select disabled>
              <SelectTrigger id="defaultPrivacy">
                <SelectValue placeholder="Select default privacy" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="private">Private</SelectItem>
                <SelectItem value="unlisted">Unlisted</SelectItem>
                <SelectItem value="public">Public</SelectItem>
              </SelectContent>
            </Select> */}
          </div>
          <div className="space-y-2">
            <Label htmlFor="defaultCategory">Default Video Category</Label>
            {/* Placeholder for Select component */}
            <Input
              id="defaultCategory"
              placeholder="Science & Technology (coming soon)"
              disabled
            />
          </div>
        </CardContent>
      </Card>

      {/* AI Configuration Section */}
      <Card>
        <CardHeader>
          <CardTitle>AI Configuration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>AI Model</Label>
            <p className="text-sm text-muted-foreground">
              Gemini Pro (Current Model - read-only)
            </p>
          </div>
          <Separator />
          <div className="space-y-2">
            <Label htmlFor="titleSuggestions">
              Number of Title Suggestions
            </Label>
            <Input
              id="titleSuggestions"
              type="number"
              placeholder="3 (coming soon)"
              disabled
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="thumbnailStyles">Thumbnail Generation Style</Label>
            {/* Placeholder for Select component */}
            <Input
              id="thumbnailStyles"
              placeholder="Default (coming soon)"
              disabled
            />
          </div>
        </CardContent>
      </Card>

      {/* Notification Settings Section */}
      <Card>
        <CardHeader>
          <CardTitle>Notifications</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between space-x-2">
            <Label
              htmlFor="emailNotifications"
              className="flex flex-col space-y-1"
            >
              <span>Email Notifications</span>
              <span className="font-normal leading-snug text-muted-foreground">
                Receive email updates for processing events.
              </span>
            </Label>
            <Switch id="emailNotifications" disabled />
          </div>
          <Separator />
          <p className="text-sm font-medium text-muted-foreground">
            Notify me when:
          </p>
          <div className="flex items-center justify-between space-x-2 pl-4">
            <Label htmlFor="notifyUploadComplete">Upload Complete</Label>
            <Switch id="notifyUploadComplete" disabled />
          </div>
          <div className="flex items-center justify-between space-x-2 pl-4">
            <Label htmlFor="notifyProcessingComplete">
              Processing Complete
            </Label>
            <Switch id="notifyProcessingComplete" disabled />
          </div>
          <div className="flex items-center justify-between space-x-2 pl-4">
            <Label htmlFor="notifyProcessingError">Processing Error</Label>
            <Switch id="notifyProcessingError" disabled />
          </div>
        </CardContent>
      </Card>

      {/* Storage & Credentials Section */}
      <Card>
        <CardHeader>
          <CardTitle>Storage & Credentials</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Google Cloud Storage</Label>
            <p className="text-sm text-muted-foreground">
              Input Bucket: `your-input-bucket` (read-only)
            </p>
            <p className="text-sm text-muted-foreground">
              Output Bucket: `your-output-bucket` (read-only)
            </p>
          </div>
          <Separator />
          <div className="space-y-2">
            <Label>Credential Status</Label>
            <p className="text-sm text-muted-foreground">
              Google Cloud: Connected ✅
            </p>
            <p className="text-sm text-muted-foreground">
              YouTube API: Connected ✅
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export const Route = createFileRoute("/settings")({
  component: SettingsComponent,
});
