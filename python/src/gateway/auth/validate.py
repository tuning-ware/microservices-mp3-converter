import os, requests

# validate JWT of client's so they are able to access the endpoints of the gateway
def token(request):
    if not "Authorization" in request.headers:
        return None, ("missing credentials", 401)

    token = request.headers["Authorization"]

    if not token:
        return None, ("missing credentials", 401)

    # create a http post request to the validate endpoint (forward this token to the auth service validate endpoint)
    try:
        response = requests.post(f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate", headers={"Authorization": token},)
        response.raise_for_status()
    except requests.RequestException as e:
        # handle request errors
        return None, (f"Error connecting to authentification service/validate: {e}", 500)

    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)
