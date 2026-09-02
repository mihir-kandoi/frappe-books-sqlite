# Web frontend

`web/main.ts` starts the Vue application. `web/WebApp.vue` reads the Frappe
boot data and initializes Fyo with the Frappe database adapter.

The startup flow has these steps:

1. Redirect a guest user to the Frappe login page.
2. Connect Fyo to the current Frappe site.
3. Register the shared schemas and models.
4. Show the setup wizard when the company setup is incomplete.
5. Show the Books desk when the company setup is complete.

`initFyo.ts` exports the application Fyo instance.
