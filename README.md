# keycloak-bulk-users
Python program to manipulate Keycloak users in a bulk way

## How to use

First, create a Client in Keycloak Realm and configure in the follow way:
* Change Access Type to confidencial (Settings tab)
* Turn on Service Accounts Enabled (Settings tab)
* In Service Accounts tab, go to Client Roles and choose realm-management and add realm-admin role (I will test with less permissions)
* Get the Client ID from Settings tab and Secret ID from Credentials tab

```
$ git clone https://github.com/dcna-dev/keycloak-bulk-users && cd keycloak-bulk-users
$ python3 -m venv .venv
$ . .venv/bin/activat
$ pip install -r requirements.txt
$ export KEYCLOAK_CLIENT_ID=xxxxxxxx
$ export KEYCLOAK_CLIENT_SECRET=xxxxxxxx
$ export KEYCLOAK_BASE_URL=https://keycloak.local/login
$ export KEYCLOAK_REALM=MyRealm
$ ./bulk-users.py -g group-name -f file-with-usernames-one-per-line.txt
```
