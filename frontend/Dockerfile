# Use Node.js as the base image
FROM node:20-slim

# Install pnpm
RUN npm install -g pnpm

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install

# Copy the rest of the application
COPY . .

# Expose the default Vite port
EXPOSE 3000

# Command to run the development server
CMD ["pnpm", "dev", "--host", "0.0.0.0"]