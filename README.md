# proFTPd API
##### small rest api written in python to administer proftpd virtual users
---
### Available methods
1. Show service status
`curl -X GET http://127.0.0.1:5000/`
2. List all users
`curl -X GET http://127.0.0.1:5000/users`
3. Show details about a user
`curl -X GET http://127.0.0.1:5000/users/<user_name>`
4. Create new user
`curl -X POST -H "Content-Type: application/json" http://127.0.0.1:5000/users -d '{"action": "create", "username": "<user_name>"}'`
5. Delete user
`curl -X POST -H "Content-Type: application/json" http://127.0.0.1:5000/users -d '{"action": "delete", "username": "<user_name>"}'`
6. Lock user
`curl -X POST -H "Content-Type: application/json" http://127.0.0.1:5000/users -d '{"action": "lock", "username": "<user_name>"}'`
7. Unlock user
`curl -X POST -H "Content-Type: application/json" http://127.0.0.1:5000/users -d '{"action": "unlock", "username": "<user_name>"}'`
8. Show space on disk
`curl -X GET http://127.0.0.1:5000/quota`