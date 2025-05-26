import {
  ErrorComponent,
  createFileRoute,
  useNavigate,
} from "@tanstack/react-router"
import React from "react"
import { ErrorBoundary } from "react-error-boundary"
import { Layout } from "~/components/layout"

export const Route = createFileRoute("/")({
  component: Home,
})

const skeletons = Array.from({ length: 2 })

function Home() {
  const filters = Route.useSearch()
  const navigate = useNavigate()

  return (
    <Layout>
      <div className="mb-9 text-center">
        <h1 className="text-4xl font-bold tracking-tight mb-3">
          Tech Events & Conferences
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Discover the best tech conferences, meetups, and workshops happening
          around the world.
        </p>
      </div>
      <div className="flex flex-col gap-4 w-full">
        <ErrorBoundary
          fallbackRender={(props) => <ErrorComponent error={props.error} />}
        >
        </ErrorBoundary>
        <div className="flex flex-col gap-4">
          <ErrorBoundary
            fallbackRender={(props) => <ErrorComponent error={props.error} />}
          >
 
          </ErrorBoundary>
        </div>
      </div>
    </Layout>
  )
}
