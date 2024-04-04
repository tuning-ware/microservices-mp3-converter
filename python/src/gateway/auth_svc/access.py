import os, requests

# gateway login function, returns a tuple (token, error)
def login(request):
    # refers to flask request
    auth = request.authorization
    if not auth:
        return None, ("missing credentials", 401)

    basicAuth = (auth.username, auth.password)

    auth_service_address = os.environ.get("AUTH_SVC_ADDRESS")
    if not auth_service_address:
        return None, ("Authentification service address not configured", 500)

    try:
        response = requests.post(f"http://{auth_service_address}/login", auth=basicAuth)
        response.raise_for_status() # raise exception for http errors

    except requests.RequestException as e:
        return None, (f"Error connecting to authentification service: {e}", 500)
        
    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)
