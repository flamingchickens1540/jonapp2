# JonApp API Documentation

All endpoints except for `/login` must be authenticated by supplying the `Authorization: Basic <TOKEN>` header which can be obtained through a POST to `/login`

| Endpoint                     | Method | Arguments             | Usage              |
| ---------------------------- | :------: | --------------------- | ------------------ |
| `/login`                   | POST  | `email`, `password` | Get token for user |
| `/signup` | POST | `email`, `name`, `password`, `type` | Sign a user up |
| `/projects` | GET | None | Get a user's projects |
| `/project/create` | POST | `name`, `description`, `image` | Create a project |
| `/project?id=<id>` | GET, POST, DELETE | `id` supplied as a URL parameter | Get, edit, or delete a project |
| `/task/create` | POST | `name`, `description`, `image`, `project-id` | Create a project |
