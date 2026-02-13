# Echo Website

The frontend application for Echo - AI YouTube Video Metadata Generator. Built with Next.js 15, TypeScript, and Tailwind CSS.

## Architecture

- **Framework**: Next.js 15 with App Router and React 19
- **Styling**: Tailwind CSS with @echo/ui component library
- **API Integration**: tRPC client for type-safe API calls
- **State Management**: TanStack Query for server state
- **Authentication**: Supabase Auth integration
- **Animations**: Framer Motion for smooth interactions
- **Typography**: Geist font family

## Getting Started

### Prerequisites

- Bun 1.0+
- Echo core API running on port 8000
- Supabase local instance

### Development

```bash
# From project root
bun dev

# Or run website only
bun dev:web

# The website will be available at http://localhost:3000
```

### Build

```bash
# Build for production
bun run build

# Start production server
bun run start

# Type checking
bun typecheck

# Linting and formatting
bun lint
bun format
```

## Project Structure

```
src/
├── app/                    # Next.js App Router
│   ├── (auth)/            # Authentication routes
│   ├── (dashboard)/       # Dashboard routes
│   ├── api/               # API routes (tRPC adapter)
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/            # React components
│   ├── providers/         # Context providers
│   ├── video-uploader.tsx # Video upload component
│   └── video-results.tsx  # Video results display
├── lib/                   # Utilities and configuration
│   └── trpc.ts           # tRPC client setup
└── utils/                 # Helper functions
```

## Features

### 🎥 Video Upload & Processing
- Drag-and-drop video upload interface
- Real-time upload progress tracking
- File type and size validation
- Integration with Google Cloud Storage

### 🤖 AI-Powered Metadata Generation
- Automatic title generation
- Video transcription
- Chapter detection and timestamps
- Description and tag suggestions

### 📊 Dashboard & Management
- Video library with search and filtering
- Processing job status tracking
- Metadata editing interface
- User analytics and usage stats

### 🔐 Authentication & User Management
- Supabase Auth integration
- Social login (Google OAuth)
- Protected routes and middleware
- User profile management

### 📱 Responsive Design
- Mobile-first design approach
- Optimized for desktop, tablet, and mobile
- Dark/light mode support (planned)
- Accessible UI components

## API Integration

The website communicates with the Echo Core API via tRPC:

```tsx
import { api } from '@/lib/trpc'

function VideoList() {
  const { data: videos, isLoading } = api.video.list.useQuery({
    limit: 10,
    offset: 0
  })

  if (isLoading) return <div>Loading...</div>
  
  return (
    <div>
      {videos?.map(video => (
        <div key={video.id}>{video.title}</div>
      ))}
    </div>
  )
}
```

### Available tRPC Procedures

- **auth**: Authentication operations
- **user**: User profile and preferences
- **video**: Video upload, listing, and metadata management
- **jobs**: Processing job status and management
- **chat**: AI chat functionality
- **analytics**: Usage statistics and insights

## Component Library

The website uses the shared @echo/ui component library:

```tsx
import { Button } from '@echo/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@echo/ui/card'
import { Input } from '@echo/ui/input'
import { Badge } from '@echo/ui/badge'

function VideoCard({ video }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{video.title}</CardTitle>
        <Badge variant={video.status === 'completed' ? 'success' : 'pending'}>
          {video.status}
        </Badge>
      </CardHeader>
      <CardContent>
        <p>{video.description}</p>
        <Button>Edit Metadata</Button>
      </CardContent>
    </Card>
  )
}
```

## Environment Variables

Required environment variables for development:

```bash
# tRPC API endpoint
NEXT_PUBLIC_API_URL=http://localhost:8000

# Supabase configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Optional: Analytics and monitoring
NEXT_PUBLIC_OPENPANEL_CLIENT_ID=your_openpanel_id
```

## Performance Optimizations

### Server Components
- Leverage Next.js server components for initial data fetching
- Reduce client-side JavaScript bundle size
- Improve SEO and initial page load times

### Image Optimization
- Next.js Image component for automatic optimization
- WebP format with fallbacks
- Responsive image sizes

### Code Splitting
- Automatic route-based code splitting
- Dynamic imports for heavy components
- Lazy loading for non-critical features

### Caching Strategy
- tRPC Query caching with React Query
- Static generation for marketing pages
- ISR (Incremental Static Regeneration) for dynamic content

## Deployment

### Vercel (Recommended)

```bash
# Connect to Vercel
vercel

# Set environment variables in Vercel dashboard
# Deploy
vercel --prod
```

### Docker

```bash
# Build Docker image
docker build -t echo-website .

# Run container
docker run -p 3000:3000 echo-website
```

### Self-Hosted

```bash
# Build for production
bun run build

# Start production server
bun run start
```

## Development Guidelines

### Adding New Pages
1. Create route in `src/app/` following App Router conventions
2. Use server components when possible
3. Implement proper loading and error states
4. Add proper meta tags for SEO

### Creating Components
1. Use TypeScript for all components
2. Follow the existing component patterns
3. Import UI components from @echo/ui
4. Include proper accessibility attributes

### API Integration
1. Use tRPC procedures instead of direct fetch calls
2. Implement proper error handling
3. Add loading states with React Query
4. Cache data appropriately

### Styling
1. Use Tailwind CSS classes
2. Follow mobile-first responsive design
3. Use CSS variables for theming
4. Prefer composition over custom CSS

## Testing

```bash
# Run tests (when implemented)
bun test

# E2E testing (planned)
bun test:e2e
```

## Reliability & Security

The Echo website implements comprehensive reliability and security measures:

### 🛡️ Security Features
- **Authentication Protection**: All app functionality secured behind Supabase auth
- **Route Protection**: Middleware-based route protection with automatic redirects
- **Rate Limiting**: Intelligent rate limiting (100/min default, 20/min auth, 200/min API)
- **Security Headers**: XSS protection, clickjacking prevention, content type validation
- **Error Boundaries**: React error boundaries for graceful error handling

### 📊 Monitoring & Health Checks
- **Health Endpoints**: `/api/health`, `/api/ready`, `/api/live` for monitoring
- **API Connectivity**: Automatic backend health verification
- **Supabase Health**: Database connectivity monitoring
- **Memory Monitoring**: Real-time memory usage tracking
- **Build Health**: Environment and deployment validation

### 🎯 Conversion Optimization
- **Pain-Driven Landing Page**: Conversion-focused copy addressing creator pain points
- **Social Proof**: Dynamic user counter and testimonials
- **Urgency Elements**: Scarcity messaging and time-sensitive offers
- **SEO Optimized**: Meta tags, OpenGraph, and Twitter cards for better discoverability
- **Mobile-First Design**: Responsive design optimized for all devices

### 🔒 Route Security
- **Protected Routes**: Dashboard, creator tools, and API endpoints require authentication
- **Public Routes**: Landing page, auth pages, and marketing content remain accessible
- **Smart Redirects**: Maintains user intent after authentication with `redirectedFrom` parameter
- **API Protection**: Unauthorized API calls return proper 401 responses

### ⚡ Performance Features
- **Server Components**: Leverage Next.js server components for faster initial loads
- **Image Optimization**: Automatic WebP conversion and responsive sizing
- **Code Splitting**: Route-based and dynamic imports for smaller bundles
- **tRPC Caching**: Intelligent query caching with React Query
- **Static Generation**: Pre-rendered marketing pages for better performance

See [RELIABILITY.md](../../docs/RELIABILITY.md) for detailed documentation on the platform's reliability features.

## Contributing

See the main [project README](../../README.md#contributing) for contribution guidelines.

## License

This package is part of the Echo project and follows the same license terms.