# musicorg
Organize your spotify album collections


# Running locally
Instructions below show how to run the website locally for development purposes. This guide is geared towards linux but as far
as I'm aware, it should be possible to do everything on Mac or Windows as well.

## Requirements
- python3
- sqlite3 (ex Ubuntu: `apt-get install sqlite3`)

## Setup
- Make a spotify developer app through "https://developer.spotify.com/dashboard"
    - note the client id and client secret for your new app
- Create a python3 virtual environment `python3 -m venv name-of-venv`
- Activate your virtual environment `source path-to-venv/bin/activate`
- Install required packages with `pip install -r requirements.txt`
- Create a flask 'secret key':
    ```python
    import secrets
    print(secrets.token_urlsafe(16))
    ```
- Create a file named *.env* at the root of your repo, and put in the following export commands
  (replacing placeholder values with your own values):
    ```bash
    export SPOTIPY_CLIENT_ID="insert-spotify-client-id-here"
    export SPOTIPY_CLIENT_SECRET="insert-spotify-client-secret-here"
    export FLASK_SECRET_KEY="insert-your-secret-key"
    export FLASK_APP=musicorg
    export FLASK_ENV=development
    ```
    - **note**: The sqlite database will be created at the path you specify upon the first run of the site.

## Run
### syntax and style
- Activate your virtual environment `source path-to-venv/bin/activate`
- Run: `flake8`

### unit tests
- Activate your virtual environment `source path-to-venv/bin/activate`
- Run: `python -m unittest`

### Run website in browser locally
- Setup the spotify redirect uri:
    - Add the following line to your *.env* file: `export SPOTIPY_REDIRECT_URI="http://localhost:5000/sp_auth_complete"`
    - In your spotify developer app (https://developer.spotify.com/dashboard) add this *Redirect URI*: `http://localhost:5000/sp_auth_complete`
- Activate your virtual environment `source path-to-venv/bin/activate`
- From the top level musicorg directory, run: `flask run`
- Open `localhost:5000` in your browser

### Run website in browser on different device on same LAN (ex: to test on mobile)
- Setup the spotify redirect uri:
    - Add the following line to your *.env* file: `export SPOTIPY_REDIRECT_URI="http://<insert-your-host-ip>:5000/sp_auth_complete"`
    - In your spotify developer app (https://developer.spotify.com/dashboard) add this *Redirect URI*: `http://<insert-your-host-ip>:5000/sp_auth_complete`
- Create a rule in your computer's firewall to allow inbound connections to port 5000 (default flask port)
- If running on WSL2, you'll need to expose your WSL2 VM virtual address (find using `ip addr` in your WSL2 terminal) at the flask port with this command in an **elevated** powershell terminal:
```powershell
netsh interface portproxy add v4tov4 listenport=5000 listenaddress=0.0.0.0 connectport=5000 connectaddress=<insert_your_wsl2_ip>
```
- Activate your virtual environment `source path-to-venv/bin/activate`
- From the top level musicorg directory, run: `flask run --host=0.0.0.0`
- Open `<insert-your-host-ip>:5000` in browser of your other device on the same LAN as your host
