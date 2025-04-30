import { createFileRoute } from '@tanstack/react-router';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Input } from '../components/ui/input';

export const Route = createFileRoute('/')({
    component: Home,
});

function Home() {
    return (
        <div className="container mx-auto p-8">
            <h1 className="text-3xl font-bold mb-6">Component Test Page</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <Card className="p-6">
                    <h2 className="text-xl font-semibold mb-4">Button Component</h2>
                    <div className="flex flex-wrap gap-2">
                        <Button variant="default">Default</Button>
                        <Button variant="destructive">Destructive</Button>
                        <Button variant="outline">Outline</Button>
                        <Button variant="secondary">Secondary</Button>
                        <Button variant="ghost">Ghost</Button>
                        <Button variant="link">Link</Button>
                    </div>
                </Card>

                <Card className="p-6">
                    <h2 className="text-xl font-semibold mb-4">Input Component</h2>
                    <div className="space-y-4">
                        <Input placeholder="Default input" />
                        <Input placeholder="Disabled input" disabled />
                    </div>
                </Card>

                <Card className="p-6">
                    <h2 className="text-xl font-semibold mb-4">Tabs Component</h2>
                    <Tabs defaultValue="account">
                        <TabsList>
                            <TabsTrigger value="account">Account</TabsTrigger>
                            <TabsTrigger value="password">Password</TabsTrigger>
                        </TabsList>
                        <TabsContent value="account" className="p-4">
                            Account settings content
                        </TabsContent>
                        <TabsContent value="password" className="p-4">
                            Password settings content
                        </TabsContent>
                    </Tabs>
                </Card>
            </div>
        </div>
    );
}