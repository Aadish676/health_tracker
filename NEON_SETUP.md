# Neon database setup

The app uses SQLite locally when `DATABASE_URL` is not set. For the deployed
Render service, use a Neon PostgreSQL database so information is retained for
every user account.

1. Create a project at [Neon](https://console.neon.tech/).
2. Copy the connection string from the project's **Connect** panel. Keep the
   `?sslmode=require` ending.
3. In Render, open the **health-tracker** web service, then go to
   **Environment**.
4. Add an environment variable named `DATABASE_URL` and paste the Neon
   connection string as its value.
5. Save the change and manually redeploy the service once. The application
   creates its tables on startup.

Never commit the connection string or add it to the frontend's Vercel
environment variables.
