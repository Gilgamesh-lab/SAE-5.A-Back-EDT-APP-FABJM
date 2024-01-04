#!/usr/bin/env python
# coding: utf-8

# In[8]:


from conftest import client, login
import pytest
import json

headers = {'Content-Type': 'application/json'} # Indispensable pour les requêtes envoyant du Json dans le body
admin_login_data = {'Username': 'johndoe', 'Password': 'password123'}
user_eleve_data =   { "role": "eleve", 
            "users": [ 
                { "FirstName": "Elève1", 
                "LastName": "lastName",
                "Username": "pytest",
                "Password": "sqlite3",
                    "info": { "idSalle": "", 
                    "isManager": "" , 'idgroupe' : 1} } ] }

def test_index(client):
    response = client.get('/index')
    assert response.status_code == 200

    data = response.data.decode() 
    assert data == 'Hello, World!'

def test_jwt(client):
    response = client.get('/utilisateurs/getAll')
    assert response.status_code == 401 # == Unauthorized

def test_getAll_utilisateur(client):
    login(client,admin_login_data['Username'], admin_login_data['Password'])
    response = client.get('/utilisateurs/getAll')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert 'John' == data[0]['FirstName']

def test_add_utilisateur(client):
    login(client,admin_login_data['Username'], admin_login_data['Password'])
    response = client.post('/utilisateurs/add', data = json.dumps(user_eleve_data), headers = headers)
    assert response.status_code == 200

    cursor = client.application.config['DATABASE'].cursor()
    cursor.execute("SELECT * FROM Utilisateur WHERE FirstName = ? AND LastName = ? AND Username = ? AND Password = ?",
                   (user_eleve_data["users"][0]["FirstName"], user_eleve_data["users"][0]["LastName"], user_eleve_data["users"][0]["Username"], user_eleve_data["users"][0]["Password"]))
    result = cursor.fetchone()
    assert result is not None







