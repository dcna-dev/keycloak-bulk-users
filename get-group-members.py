#!/usr/bin/env python

import argparse
import csv
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


def get_group_members(token, group_id, keycloak_base_url, realm):
  headers = { "User-Agent": "Mozilla/5.0 (Keycloak Bulk Users; Linux)", "Authorization": "Bearer " + token }
  group_url = f"{keycloak_base_url}/admin/realms/{realm}/groups/{group_id}/members"
  first = 0
  max = 100
  group_members = []
  next = True

  while next:
    try:
      params = {"first": first, "max": max}
      resp = requests.get(group_url, headers=headers, params=params)
    except requests.exceptions.RequestException as e:
      raise SystemExit(e)
    if len(resp.json()) > 0:
      group_members += resp.json()
      first += max
    else:
      next = False

  return group_members


def init_argparse():
  parser = argparse.ArgumentParser(usage="%(prog)s [OPTIONS]...",
                                  description="Program to get a list of members from Keycloak group")
  parser.add_argument('-g','--groupname', help='Group name to add users', required=True)

  return parser

if __name__ == "__main__":

  parser = init_argparse()
  args = parser.parse_args()

  actual_date = date.today()
  logging.basicConfig(handlers=[logging.FileHandler(f"get-users-{actual_date.strftime('%d-%m-%Y')}.log"),
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

  group_members = get_group_members(token, group_id, keycloak_base_url, realm)
  with open(f"{args.groupname}.csv", 'w') as file:
    csv_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['username', 'firstName'])
    for user in group_members:
      csv_writer.writerow([user['username'], user['firstName']])