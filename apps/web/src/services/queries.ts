import {
    type UseSuspenseQueryResult,
    queryOptions,
    useMutation,
    useQueryClient,
    useSuspenseQuery,
  } from "@tanstack/react-query"
  import { getUser } from "./auth.api"
  
  // TODO: Implement event queries when backend is ready
// export const eventQueries = {
//   all: ["events"],
//   list: (filters: EventFilters) =>
//     queryOptions({
//       queryKey: [...eventQueries.all, "list", filters],
//       queryFn: () => getEvents({ data: filters }),
//     }),
//   detail: (eventId: number) =>
//     queryOptions({
//       queryKey: [...eventQueries.all, "detail", eventId],
//       queryFn: () => getEvent({ data: { id: eventId } }),
//       enabled: !Number.isNaN(eventId) && !!eventId,
//     }),
// }

// export const useUpsertEventMutation = () => {
//   const queryClient = useQueryClient()
//   return useMutation({
//     mutationFn: (data: Parameters<typeof upsertEvent>[0]) => upsertEvent(data),
//     onSuccess: () => {
//       queryClient.invalidateQueries({ queryKey: eventQueries.all })
//     },
//   })
// }
  

  
  export const authQueries = {
    all: ["auth"],
    user: () =>
      queryOptions({
        queryKey: [...authQueries.all, "user"],
        queryFn: () => getUser(),
      }),
  }
  
  export const useAuthentication = () => {
    return useSuspenseQuery(authQueries.user())
  }
  
  export const useAuthenticatedUser = () => {
    const authQuery = useAuthentication()
  
    if (authQuery.data.isAuthenticated === false) {
      throw new Error("User is not authenticated!")
    }
  
    return authQuery as UseSuspenseQueryResult<typeof authQuery.data>
  }
  