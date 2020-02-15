from amadeus import Client


def get_client():
    CLIENT_API_KEY = "bCDPijBMX0J26qjRbjoM20PfX37PZGye"
    CLIENT_API_SECRET = "m519izNzO29PGEbl"
    amadeus_client = Client(
        client_id=CLIENT_API_KEY,
        client_secret=CLIENT_API_SECRET)
    return amadeus_client
