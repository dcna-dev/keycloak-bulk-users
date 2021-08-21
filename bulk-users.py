#!/usr/bin/env python

import argparse
import logging
import os
import requests

from datetime import date

def get_token(client_id, client_secret, keycloak_base_url, realm):
  data = {"client_id": client_id, "client_secret": client_secret, "grant_type": "client_credentials"}
  headers = { "User-Agent": "Mozilla/5.0 (Keycloak Bulk Users; Linux)" }
  login_url = keycloak_base_url + "/realms/" + realm + "/protocol/openid-connect/token"
  try:
    resp = requests.post(login_url, data=data, headers=headers )
  except requests.exceptions.RequestException as e:
    raise SystemExit(e)  
  if resp.status_code == 200:
    token = resp.json()["access_token"]
    return token
  else:
    logging.error(f"Problem with login {client_id} - Server response: {resp.text}")


def get_user_id(token, username, keycloak_base_url, realm):
  headers = { "User-Agent": "Mozilla/5.0 (Keycloak Bulk Users; Linux)", "Authorization": "Bearer " + token }
  user_url = f"{keycloak_base_url}/admin/realms/{realm}/users"
  params = {"username": username}
  try:
    resp = requests.get(user_url, headers=headers, params=params)
  except requests.exceptions.RequestException as e:
    raise SystemExit(e)
  if resp.status_code == 200 and len(resp.json()) > 0:
    user_id = resp.json()[0]["id"]
    return user_id
  else:
    logging.error(f"Problem in get user_id with username {username} - Server response: {resp.text}")


def get_group_id(token, groupname, keycloak_base_url, realm):
  headers = { "User-Agent": "Mozilla/5.0 (Keycloak Bulk Users; Linux)", "Authorization": "Bearer " + token }
  group_url = f"{keycloak_base_url}/admin/realms/{realm}/groups"
  params = {"search": groupname}
  try:
    resp = requests.get(group_url, headers=headers, params=params)
  except requests.exceptions.RequestException as e:
    raise SystemExit(e)
  if resp.status_code == 200 and len(resp.json()) > 0:
    group_id = resp.json()[0]["id"]
    return group_id
  else:
    logging.error(f"Problem group_id with group name {groupname} - Server response: {resp.text}")
    return "error"


def put_user_in_group(token, user_id, group_id, keycloak_base_url, realm):
  headers = { "User-Agent": "Mozilla/5.0 (Keycloak Bulk Users; Linux)", "Authorization": "Bearer " + token }
  put_user_in_group_url = f"{keycloak_base_url}/admin/realms/{realm}/users/{user_id}/groups/{group_id}"
  try:
    resp = requests.put(put_user_in_group_url, headers=headers)
  except requests.exceptions.RequestException as e:
    raise SystemExit(e)
  if resp.status_code == 204:
    logging.info(f"Success: User {user_id} added to group {group_id}") 
  else:
    logging.error(f"Problem when put user with user_id {user_id} in group_id {group_id} - Server response: {resp.text}")


def init_argparse():
  parser = argparse.ArgumentParser(usage="%(prog)s [OPTIONS]...",
                                  description="Program to add a list of users to a Keycloak group")
  parser.add_argument('-g','--groupname', help='Group name to add users', required=True)
  parser.add_argument('-f','--file', help='File with a list of users one per line', required=True)

  return parser

if __name__ == "__main__":

  parser = init_argparse()
  args = parser.parse_args()

  actual_date = date.today()
  logging.basicConfig(handlers=[logging.FileHandler(f"bulk-users-{actual_date.strftime('%d-%m-%Y')}.log"),
                      logging.StreamHandler()], level=logging.INFO,
                      format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

  client_id = os.environ['KEYCLOAK_CLIENT_ID']
  client_secret = os.environ['KEYCLOAK_CLIENT_SECRET']
  keycloak_base_url = os.environ['KEYCLOAK_BASE_URL']
  realm = os.environ['KEYCLOAK_REALM']

  token = get_token(client_id, client_secret, keycloak_base_url, realm)
  
  group_id = get_group_id(token, args.groupname, keycloak_base_url, realm)
  if group_id == "error":
    logging.error(f"Group name {args.groupname} not found")
    raise SystemExit(1) 

  with open(args.file, 'r') as reader:
    line = reader.readline()
    while line != '':
      username = line.rstrip()
      user_id = get_user_id(token, username , keycloak_base_url, realm)
      put_user_in_group(token, user_id, group_id, keycloak_base_url, realm)
      line = reader.readline()