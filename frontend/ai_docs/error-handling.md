# Error Handling Standards

This document outlines the standardized error handling patterns to be implemented across the frontend application. It defines error types, user-facing feedback mechanisms, and recovery strategies.

## Error Types

The application defines several error types to categorize different failure scenarios:

```typescript
// api.ts or errors.ts
export class AppError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AppError';
  }
}

export class AuthenticationError extends AppError {
  constructor(message = 'Authentication failed. Please log in again.') {
    super(message);
    this.name = 'AuthenticationError';
  }
}

export class NetworkError extends AppError {
  constructor(message = 'Network connection issue. Please check your internet connection.') {
    super(message);
    this.name = 'NetworkError';
  }
}

export class ValidationError extends AppError {
  constructor(message = 'Invalid input data. Please check your entries.') {
    super(message);
    this.name = 'ValidationError';
  }
}

export class ServerError extends AppError {
  constructor(message = 'Server error. Our team has been notified.') {
    super(message);
    this.name = 'ServerError';
  }
}

export class WebSocketError extends AppError {
  constructor(message = 'Real-time connection error. Updates may be delayed.') {
    super(message);
    this.name = 'WebSocketError';
  }
}
```

## API Error Handling

All API requests should use a standardized error handling approach:

```typescript
// Example API client function with error handling
async function fetchVideos() {
  try {
    const response = await fetch('/api/videos', {
      headers: {
        'Authorization': `Bearer ${getSupabaseToken()}`
      }
    });
    
    if (!response.ok) {
      // Handle different HTTP status codes
      if (response.status === 401 || response.status === 403) {
        throw new AuthenticationError();
      } else if (response.status === 400) {
        throw new ValidationError();
      } else if (response.status >= 500) {
        throw new ServerError();
      } else {
        throw new AppError(`Request failed with status: ${response.status}`);
      }
    }
    
    return await response.json();
  } catch (error) {
    // Categorize uncaught errors
    if (error instanceof AppError) {
      // Rethrow our custom errors
      throw error;
    } else if (error instanceof TypeError && error.message.includes('fetch')) {
      // Network errors
      throw new NetworkError();
    } else {
      // Unknown errors
      console.error('Unexpected error:', error);
      throw new AppError('An unexpected error occurred');
    }
  }
}
```

## User Feedback Mechanisms

### Toast Notifications

Use toast notifications for transient errors:

```typescript
// Example usage with shadcn/ui toast
import { useToast } from '@/components/ui/use-toast';

function ExampleComponent() {
  const { toast } = useToast();
  
  const handleAction = async () => {
    try {
      await someApiCall();
    } catch (error) {
      toast({
        variant: error instanceof ValidationError ? 'warning' : 'destructive',
        title: error.name,
        description: error.message,
        action: error instanceof NetworkError ? (
          <ToastAction altText="Retry" onClick={handleAction}>Retry</ToastAction>
        ) : undefined
      });
    }
  };
}
```

### Form Validation Errors

Display form validation errors inline:

```tsx
function FormExample() {
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  const handleSubmit = async (data) => {
    try {
      setErrors({});
      await submitForm(data);
    } catch (error) {
      if (error instanceof ValidationError && error.fieldErrors) {
        setErrors(error.fieldErrors);
      } else {
        // Handle other errors with toast
      }
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <div>
        <Label htmlFor="title">Title</Label>
        <Input id="title" />
        {errors.title && (
          <p className="text-sm text-red-500">{errors.title}</p>
        )}
      </div>
      {/* Other form fields */}
    </form>
  );
}
```

### Error States

Implement error states for failed data loading:

```tsx
function DataComponent() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['data'],
    queryFn: fetchData
  });
  
  if (isLoading) {
    return <LoadingSpinner />;
  }
  
  if (error) {
    return (
      <div className="error-container">
        <p>Failed to load data: {error.message}</p>
        <Button onClick={() => refetch()}>Retry</Button>
      </div>
    );
  }
  
  return <DataDisplay data={data} />;
}
```

## Retry Strategies

### Automatic Retries

Implement automatic retries for network errors:

```typescript
// Example retry logic for API calls
async function fetchWithRetry(url, options, maxRetries = 3) {
  let retries = 0;
  
  while (retries < maxRetries) {
    try {
      const response = await fetch(url, options);
      if (response.ok) return response.json();
      
      // Don't retry for client errors (except 429 too many requests)
      if (response.status >= 400 && response.status < 500 && response.status !== 429) {
        handleErrorByStatus(response);
      }
      
      // For 5xx and 429 errors, retry
      throw new NetworkError(`Request failed with status: ${response.status}`);
    } catch (error) {
      retries += 1;
      
      if (retries >= maxRetries) {
        throw error;
      }
      
      // Exponential backoff
      const delay = Math.min(1000 * (2 ** retries) + Math.random() * 1000, 10000);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
}
```

### TanStack Query Configuration

Configure TanStack Query for automatic retries:

```typescript
// Configure in QueryClient setup
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error) => {
        // Don't retry for authentication or validation errors
        if (error instanceof AuthenticationError || error instanceof ValidationError) {
          return false;
        }
        // Retry network errors up to 3 times
        if (error instanceof NetworkError) {
          return failureCount < 3;
        }
        // Default retry logic
        return failureCount < 2;
      },
      retryDelay: attemptIndex => Math.min(1000 * (2 ** attemptIndex), 30000),
    },
  },
});
```

## Error Handling for WebSockets

The WebSocket hook should include specific error handling:

```typescript
function useAppWebSocket() {
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [error, setError] = useState<Error | null>(null);
  
  // Connection logic with error handling
  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectAttempts = 0;
    let reconnectTimeout: NodeJS.Timeout | null = null;
    
    const connect = () => {
      try {
        ws = new WebSocket(`${WEBSOCKET_URL}?token=${getSupabaseToken()}`);
        
        ws.onopen = () => {
          setConnectionStatus('connected');
          setError(null);
          reconnectAttempts = 0;
        };
        
        ws.onclose = (event) => {
          setConnectionStatus('disconnected');
          
          // Don't reconnect if closed cleanly (code 1000)
          if (event.code !== 1000) {
            reconnect();
          }
        };
        
        ws.onerror = (event) => {
          setError(new WebSocketError('Connection error occurred'));
          ws?.close();
        };
        
        // Message handling logic
      } catch (err) {
        setError(new WebSocketError('Failed to establish connection'));
        reconnect();
      }
    };
    
    const reconnect = () => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      
      reconnectAttempts += 1;
      setConnectionStatus('reconnecting');
      
      // Exponential backoff with max delay
      const delay = Math.min(1000 * (2 ** reconnectAttempts), 30000);
      
      reconnectTimeout = setTimeout(() => {
        connect();
      }, delay);
    };
    
    connect();
    
    return () => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      if (ws) {
        ws.close(1000, 'Component unmounting');
      }
    };
  }, []);
  
  // Rest of the hook implementation
}
```

## Authentication Error Handling

For authentication errors, implement automatic redirection to login:

```typescript
// Global error handler for authentication errors
function AuthErrorHandler({ children }) {
  const navigate = useNavigate();
  
  // Set up a global error boundary or listener
  useEffect(() => {
    const handleUnauthorized = (error) => {
      if (error instanceof AuthenticationError) {
        // Clear local auth state
        // Redirect to login
        navigate('/login', { 
          state: { 
            from: window.location.pathname,
            reason: 'session_expired' 
          } 
        });
      }
    };
    
    // Listen to custom error events
    window.addEventListener('app:error', (e) => handleUnauthorized(e.detail));
    
    return () => {
      window.removeEventListener('app:error', (e) => handleUnauthorized(e.detail));
    };
  }, [navigate]);
  
  return children;
}
```

## Error Logging

Implement consistent error logging:

```typescript
// Error logger utility
export function logError(error: Error, context?: Record<string, any>) {
  console.error('Application error:', {
    name: error.name,
    message: error.message,
    stack: error.stack,
    context,
    timestamp: new Date().toISOString(),
  });
  
  // In production, could send to error monitoring service
  if (import.meta.env.PROD) {
    // Send to monitoring service
  }
}
``` 