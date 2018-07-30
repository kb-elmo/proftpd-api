# proftpd-api
small rest api written in python to administer proftpd virtual users via ftpasswd

### Available methods
URL | Function
------------ | -------------
/ | Get the ProFTPd service status
/users | show all users
/users/<user_name> | details about a specific user
/users/create/<user_name> | create new user
/users/delete/<user_name> | delete user
/users/lock/<user_name> | lock a user account
/users/unlock/<user_name> | unlock user account
/quota | show free space of ftpdata dir
