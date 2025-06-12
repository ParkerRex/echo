# @echo/ui

A comprehensive UI component library built with React, TypeScript, and Tailwind CSS. Based on shadcn/ui with additional custom components for the Echo application.

## Overview

This package provides a complete set of reusable UI components built on top of:

- **Radix UI**: Unstyled, accessible components
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icons
- **class-variance-authority**: Type-safe variant management
- **TipTap**: Rich text editor components

## Installation

The UI package is used internally within the Echo monorepo. To use components in your app:

```tsx
import { Button } from '@echo/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@echo/ui/card'
import { Input } from '@echo/ui/input'
```

## Component Categories

### Layout & Structure
- **Card**: Content containers with header, body, and footer sections
- **Separator**: Visual dividers for content sections
- **Sheet**: Slide-out panels and drawers
- **Drawer**: Mobile-optimized slide-up panels

### Navigation
- **Navigation Menu**: Horizontal navigation with dropdowns
- **Tabs**: Tabbed content organization
- **Breadcrumbs**: Hierarchical navigation trails

### Form Components
- **Input**: Text input fields with various types
- **Textarea**: Multi-line text input
- **Button**: Primary, secondary, and variant buttons
- **Checkbox**: Checkboxes with indeterminate state
- **Radio Group**: Radio button groups
- **Select**: Dropdown select menus
- **Combobox**: Searchable select with autocomplete
- **Switch**: Toggle switches
- **Slider**: Range input sliders
- **Input OTP**: One-time password input fields
- **Form**: Form field wrappers with validation
- **Submit Button**: Form submission buttons with loading states

### Data Display
- **Table**: Data tables with sorting and pagination
- **Avatar**: User avatars with fallbacks
- **Badge**: Status indicators and tags
- **Progress**: Progress bars and indicators
- **Chart**: Data visualization components (via Recharts)
- **Skeleton**: Loading placeholders

### Feedback
- **Alert**: Success, error, warning, and info messages
- **Toast**: Temporary notification messages
- **Spinner**: Loading indicators
- **Tooltip**: Contextual information overlays

### Overlays
- **Dialog**: Modal dialogs and confirmations
- **Alert Dialog**: Confirmation dialogs
- **Popover**: Floating content containers
- **Hover Card**: Hover-triggered content previews
- **Context Menu**: Right-click context menus
- **Dropdown Menu**: Dropdown action menus

### Specialized Components
- **Editor**: Rich text editor with TipTap
- **Calendar**: Date picker calendar
- **Date Range Picker**: Date range selection
- **Time Range Input**: Time range selection
- **Currency Input**: Formatted currency input
- **Quantity Input**: Numeric quantity selectors
- **Multiple Selector**: Multi-select with tags
- **Animated Size Container**: Smooth height transitions

### Utilities
- **Icons**: Lucide React icon components
- **Hooks**: Custom React hooks for common patterns
- **cn**: Tailwind class name utility
- **truncate**: Text truncation utilities

## Usage Examples

### Basic Components

```tsx
import { Button } from '@echo/ui/button'
import { Input } from '@echo/ui/input'
import { Card, CardContent } from '@echo/ui/card'

function LoginForm() {
  return (
    <Card className="w-96">
      <CardContent className="space-y-4">
        <Input type="email" placeholder="Email" />
        <Input type="password" placeholder="Password" />
        <Button className="w-full">Sign In</Button>
      </CardContent>
    </Card>
  )
}
```

### Form with Validation

```tsx
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from '@echo/ui/form'
import { Input } from '@echo/ui/input'
import { Button } from '@echo/ui/button'

function ContactForm() {
  return (
    <Form>
      <FormField name="email">
        <FormItem>
          <FormLabel>Email</FormLabel>
          <FormControl>
            <Input type="email" />
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>
      <Button type="submit">Submit</Button>
    </Form>
  )
}
```

### Data Table

```tsx
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@echo/ui/table'

function VideoTable({ videos }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Title</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Created</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {videos.map((video) => (
          <TableRow key={video.id}>
            <TableCell>{video.title}</TableCell>
            <TableCell>{video.status}</TableCell>
            <TableCell>{video.created_at}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
```

## Theming

Components use CSS variables for theming. Override the default theme by customizing the CSS variables in your application:

```css
:root {
  --primary: 210 40% 98%;
  --primary-foreground: 222.2 84% 4.9%;
  --secondary: 210 40% 96%;
  --secondary-foreground: 222.2 84% 4.9%;
  /* ... other theme variables */
}
```

## Accessibility

All components are built with accessibility in mind:

- Proper ARIA attributes
- Keyboard navigation support
- Screen reader compatibility
- Focus management
- Color contrast compliance

## Development

```bash
# Type checking
bun typecheck

# Linting
bun lint

# Formatting
bun format
```

## Contributing

When adding new components:

1. Follow the existing patterns and conventions
2. Use Radix UI primitives when possible
3. Include proper TypeScript types
4. Add accessibility features
5. Document component APIs and usage examples
6. Test with keyboard navigation and screen readers

## License

This package is part of the Echo project and follows the same license terms.