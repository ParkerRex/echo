import { createFileRoute } from "@tanstack/react-router"
import React from "react"
import { Layout } from "src/components/layout"
import Hero from "src/components/home/hero"

export const Route = createFileRoute("/")({
  component: Home,
})

function Home() {
  return (
    <Layout>
      <Hero />
    </Layout>
  )
}
