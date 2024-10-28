import swisseph as swe
import datetime
import requests
from timezonefinder import TimezoneFinder

calendarType = input("Do you follow Amanta or Purnimanta system? (Enter 'amanta' or 'purnimanta'): ").strip().lower()

# Constants for calculations
teluguMonthsPurnimanta = [
    "Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada",
    "Ashwin", "Karthika", "Margashirsha", "Pausha", "Magha", "Phalguna"
]

teluguMonthsAmanta = teluguMonthsPurnimanta[-1:] + teluguMonthsPurnimanta[:-1]  # Offset by one month

# Function to determine the masa based on the sun's position in the zodiac

class MasaPakshaTithiCalculator:

    @staticmethod
    def getSunAndMoonPositions(julianDay):
        # Use Swiss Ephemeris to get the current positions of the sun and moon
        sunPosition = swe.calc_ut(julianDay, swe.SUN)[0]
        moonPosition = swe.calc_ut(julianDay, swe.MOON)[0]

        sunLongitude = sunPosition[0] if isinstance(sunPosition, tuple) else sunPosition
        moonLongitude = moonPosition[0] if isinstance(moonPosition, tuple) else moonPosition

        return {
            "sunLongitude": sunLongitude,
            "moonLongitude": moonLongitude
        }

    @staticmethod
    def getPakshaTithi(sunLongitude, moonLongitude):

        # Calculate the difference between moon and sun positions to determine the tithi. [Each tithi is 12 degrees difference]
        tithi = (moonLongitude - sunLongitude) % 360 / 12 + 1
        tithi = int(tithi) if tithi <= 30 else int(tithi - 30)        

        # Determine paksha based on tithi
        paksha = "Shukla Paksha" if tithi < 15 else "Krishna Paksha"

        return {
            "tithi": tithi,
            "paksha": paksha
        }
    
    @staticmethod
    def getCurrentMasa(calendarType, sunLongitude):
        # Each zodiac sign is 30 degrees
        zodiacPosition = int(sunLongitude / 30)  

        if calendarType == 'amanta':
            return teluguMonthsAmanta[zodiacPosition]
        elif calendarType == 'purnimanta':
            return teluguMonthsPurnimanta[zodiacPosition]
        else:
            raise ValueError("Invalid calendar type. Please enter 'amanta' or 'purnimanta'.")

    @staticmethod
    def getCurrentYoga(sunLongitude, moonLongitude):
        totalLongitude = (sunLongitude + moonLongitude) % 360
        # Each yoga is 13°20', which is equivalent to 13 + 20/60 degrees
        yogaIndex = round(totalLongitude / (13 + 20 / 60)) % 27  # There are 27 yogas

        yogas = [
            "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarman", "Dhriti", "Shula", "Ganda",
            "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
            "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"
        ]

        return yogas[yogaIndex]
    
    @staticmethod
    def getJulianDayAtSunrise(year, month, day, latitude, longitude):
        julian_day = swe.julday(year, month, day)
        sunrise_info = swe.rise_trans(julian_day, swe.SUN, geopos=[longitude, latitude, 0], rsmi=swe.CALC_RISE)[0]

        # Return the Julian day adjusted for the sunrise time
        julian_day_at_sunrise = julian_day + (sunrise_info[0] / 24.0)  # Convert hours to Julian day fraction
        return julian_day_at_sunrise

    @staticmethod
    def getLocationTZ():
        try:
            response = requests.get('https://ipinfo.io/json')
            data = response.json()
            loc = data['loc'].split(',')
            latitude = float(loc[0])
            longitude = float(loc[1])

            # Get timezone
            tzFinder = TimezoneFinder()
            timeZoneStr = tzFinder.timezone_at(lat=latitude, lng=longitude)

            return latitude, longitude, timeZoneStr
        except Exception as e:
            print(f"Error fetching location: {e}")
            return None, None, None
        
# Example usage
current_date = datetime.datetime.now()

latitude, longitude, _ = MasaPakshaTithiCalculator.getLocationTZ()

julian_day = MasaPakshaTithiCalculator.getJulianDayAtSunrise(current_date.year, current_date.month, current_date.day, latitude, longitude)

# Get sun and moon positions
positions = MasaPakshaTithiCalculator.getSunAndMoonPositions(julian_day)
sun_longitude = positions["sunLongitude"]
moon_longitude = positions["moonLongitude"]

# Calculate masa and paksha/tithi using the precomputed sun and moon positions
masa = MasaPakshaTithiCalculator.getCurrentMasa(calendarType, sun_longitude)
paksha_tithi = MasaPakshaTithiCalculator.getPakshaTithi(sun_longitude, moon_longitude)
yoga = MasaPakshaTithiCalculator.getCurrentYoga(sun_longitude, moon_longitude)

print(f"Current Masa: {masa}")
print(f"Current Tithi: {paksha_tithi['tithi']} ({paksha_tithi['paksha']})")
print(f"Current Yoga: {yoga}")