import { createFileRoute } from "@tanstack/react-router";

function DashboardComponent() {
    return (
        <div>
            <h1>Dashboard</h1>
            <p>This is the Dashboard page route.</p>
        </div>
    );
}

export const Route = createFileRoute("/dashboard")({
    component: DashboardComponent,
});
