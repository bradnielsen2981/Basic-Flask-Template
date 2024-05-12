from geopy.geocoders import Nominatim
import hashlib
import qrcode
from PIL import Image

#helper function to get longitude and latitude
def get_coordinates(address, postcode):
    geolocator = Nominatim(user_agent="app")  # Replace 'my_app' with your app name
    location = geolocator.geocode(f"{address}, {postcode}")
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

#helper function to get address and postcode from longitude and latitude
def get_address(latitude, longitude):
    geolocator = Nominatim(user_agent="app")  # Replace 'my_app' with your app name
    location = geolocator.reverse((latitude, longitude), exactly_one=True)
    if location:
        address = location.address
        postcode = location.raw.get('address', {}).get('postcode', '')
        return address, postcode
    else:
        return None, None
    
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