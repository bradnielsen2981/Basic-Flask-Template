import hashlib
import qrcode
from PIL import Image
import requests


#helper function to get longitude and latitude
def get_coordinates(address, postcode):
    address = address + " " + postcode
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
        "addressdetails": 1
    }
    longitude = 0; latitude = 0
    response = requests.get(base_url, params=params)
    data = response.json()
    if data:
        location = data[0]
        latitude = float(location["lat"])
        longitude = float(location["lon"])

    print(longitude, latitude)
    return longitude, latitude
    

#helper function to get address and postcode from longitude and latitude
def get_address(latitude, longitude):
    base_url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": latitude,
        "lon": longitude,
        "format": "json",
        "addressdetails": 1
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if data:
        address = data.get("display_name", "Address not found")
        return address
    else:
        return "Address not found or invalid"

    
#helper function to create a qrcode for the event using the eventvenue and eventdatetime
def create_qrcode(eventid):
    data = "karaoke " + str(eventid)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("qrcodes/"+str(data)+".png")
    return

#helper function to get the eventvenue and eventdatetime from the qrcode
def read_qrcode(image):
    data = qrcode.image_to_string(image)
    karaoke, eventid = data.split(" ")
    return eventid