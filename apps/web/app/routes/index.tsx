import { createFileRoute } from "@tanstack/react-router"
import React from "react"
import { Layout } from "~/components/layout"
import Hero from "~/components/home/hero"

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
