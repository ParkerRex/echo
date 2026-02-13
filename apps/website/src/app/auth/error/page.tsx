import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@echo/ui/card'
import { Button } from '@echo/ui/button'
import { AlertCircle, Video } from 'lucide-react'
import Link from 'next/link'

export default function AuthErrorPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1 text-center">
          <div className="flex justify-center mb-4">
            <div className="w-12 h-12 bg-destructive/10 rounded-lg flex items-center justify-center">
              <AlertCircle className="w-6 h-6 text-destructive" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold">Authentication Error</CardTitle>
          <CardDescription>
            There was a problem signing you in
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-center text-sm text-muted-foreground">
            This could be due to an expired link, invalid credentials, or a temporary issue. 
            Please try again or contact support if the problem persists.
          </p>
          
          <div className="flex flex-col space-y-2">
            <Link href="/auth/login">
              <Button className="w-full">Try again</Button>
            </Link>
            <Link href="/">
              <Button variant="outline" className="w-full">Go home</Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}