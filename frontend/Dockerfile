# frontend/Dockerfile
FROM node:20-alpine 
# Using a specific Node.js version and alpine for smaller size

WORKDIR /app # Changed from /workspace to /app for consistency

# Copy package.json and package-lock.json to install dependencies
COPY package.json ./
COPY package-lock.json ./

# Install frontend dependencies
RUN npm install

# Expose the port React dev server runs on
EXPOSE 3000

# The CMD will be overridden by the docker-compose command.
# This runs the development server with hot-reloading.
CMD ["npm", "start"]