- Always use bun instead of npm or pnpm
- Always write tests using bun
- **Avoid using any. heres how to use our types:**
  - **Use Supabase Types When:**
    - Working directly with Supabase client  
    - Handling authentication flows  
    - Implementing real-time features  
    - Performing file storage operations  

  - **Use Drizzle Types When:**
    - Writing backend database queries  
    - Creating or modifying database schema  
    - Implementing complex business logic  
    - Optimizing database performance  

  - **Use tRPC Types When:**
    - Building dashboard UI components  
    - Making API calls from frontend  
    - Implementing form submissions  
    - Fetching data for React components  

  - **Use Zod Schemas When:**
    - Validating user input  
    - Documenting REST APIs  
    - Creating OpenAPI specifications  
    - Transforming data between layers  