import { Link, Outlet, createFileRoute, ErrorComponentProps } from '@tanstack/react-router'
import { DEPLOY_URL } from '../utils/users'
import type { User } from '../utils/users'

function UsersListSkeleton() {
  return (
    <div className="p-2 flex gap-2">
      <ul className="list-disc pl-4 animate-pulse">
        {[...Array(3)].map((_, i) => (
          <li key={i} className="whitespace-nowrap py-1">
            <div className="h-5 bg-gray-300 rounded w-32 my-1"></div>
          </li>
        ))}
      </ul>
      <hr />
      {/* Outlet might show its own skeleton or nothing */}
    </div>
  )
}

function UsersErrorComponent({ error }: ErrorComponentProps) {
  // Log the error for debugging (optional)
  // console.error("Error in UsersRoute:", error);
  return (
    <div className="p-4 text-red-600 bg-red-50 border border-red-200 rounded-md">
      <h4 className="font-semibold mb-2">Error Loading Users</h4>
      <p>{error instanceof Error ? error.message : 'An unexpected error occurred.'}</p>
      <p className="mt-2 text-sm">Please try again later.</p>
    </div>
  )
}

export const Route = createFileRoute('/users')({
  loader: async () => {
    try {
      const res = await fetch(DEPLOY_URL + '/api/users')
      if (!res.ok) {
        throw new Error('Unexpected status code')
      }

      const data = (await res.json()) as Array<User>

      return data
    } catch {
      throw new Error('Failed to fetch users')
    }
  },
  pendingComponent: UsersListSkeleton,
  errorComponent: UsersErrorComponent,
  component: UsersLayoutComponent,
})

function UsersLayoutComponent() {
  const users = Route.useLoaderData()

  if (users.length === 0) {
    return (
      <div className="p-2 flex gap-2">
        <div>
          <p className="text-muted-foreground">No users found.</p>
          {/* Still render Outlet in case it has independent content or a default view */}
        </div>
        <hr />
        <Outlet />
      </div>
    )
  }

  return (
    <div className="p-2 flex gap-2">
      <ul className="list-disc pl-4">
        {[
          ...users,
          { id: 'i-do-not-exist', name: 'Non-existent User', email: '' },
        ].map((user) => {
          return (
            <li key={user.id} className="whitespace-nowrap">
              <Link
                to="/users/$userId"
                params={{
                  userId: String(user.id),
                }}
                className="block py-1 text-blue-800 hover:text-blue-600"
                activeProps={{ className: 'text-black font-bold' }}
              >
                <div>{user.name}</div>
              </Link>
            </li>
          )
        })}
      </ul>
      <hr />
      <Outlet />
    </div>
  )
}