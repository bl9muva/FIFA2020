

from bs4 import BeautifulSoup
import requests
import pandas as pd
import pycountry
import pycountry_convert

# Main Function
def connection():
    # Empty Dataframe for storing scrapped data
   playersData = pd.DataFrame()
   
   # For loop for the number of webpages to iterate through 
   for page in range(1,560):
       
       # Url address for Gold, Silver, and Bronze players
       if page < 71:
           url = 'https://www.futbin.com/20/players?page='+str(page)+'&sort=Player_Rating&order=desc&version=gold'
       elif page >= 71 and page < 352:
           url = 'https://www.futbin.com/20/players?page='+str(page-70)+'&sort=Player_Rating&order=desc&version=silver'
       else:
            url = 'https://www.futbin.com/20/players?page='+str(page-351)+'&sort=Player_Rating&order=desc&version=bronze'
       
       response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})

       # BeautifulSoup parser
       soup = BeautifulSoup(response.text, 'html.parser')
       rows = soup.find_all('tr')
        
       playersInfo = []
       # For loop for retrieving information such as name, club, country, and skill ratings
       for row in range(len(rows)):
           
           if row not in range (0, 2):
               cols = rows[row].find_all('td')
               playerInfo = []
               
               # Add each data point to a playerinfo list
               for col in range(0,len(cols)):
                   if col == 0:
                       playersName = cols[col].text.strip()
                       playerInfo.append(playersName)
                       playerClubCountryLeague = cols[col].find('span', {'class' : 'players_club_nation'})
                       NoneTypeCheck(playerClubCountryLeague, playerInfo, 'a', 0, 'data-original-title')
                       NoneTypeCheck(playerClubCountryLeague, playerInfo, 'a', 1, 'data-original-title')
                       NoneTypeCheck(playerClubCountryLeague, playerInfo, 'a', 2, 'data-original-title')
                   elif col == 7:
                       playerInfo.append(cols[col].text.replace('\\', '/'))
                   elif col == 14:
                       # Formatting for players height
                       playerInfo.append(cols[col].text.strip().split('cm')[0])
                   elif col not in range(3,5) and col != 15:
                       playerInfo.append(cols[col].text.strip())
               playersInfo.append(playerInfo)
    
       # Add player info to dataframe
       playersData = playersData.append(playersInfo, ignore_index = True)
   
    # Column names  
   playersData.columns =  ['Name', 'Club', 'Country', 'League', 'Overall Rating', 'Position',
                           'Skill' , 'Weak Foot', 'Work Rate', 'Pace', 'Shooting', 'Passing',
                           'Dribbling' , 'Defending', 'Physicality', 'Height', 'Base Stats',
                           'In Game Stats']
   
   # Convert country to continent
   playersData.insert(3, "Continent", playersData['Country'].apply(continent) , True)
   # Convert each position to position group
   playersData.insert(7, "Position Group", playersData['Position'].apply(position), True)
   
   # Remove duplicate players and keep the last instance
   playersData.drop_duplicates(subset = ['Name', 'Overall Rating', 'Position'], keep = 'last', inplace = True)

   # Write dataframe to csv file
   playersData.to_csv('FIFA Player Info.csv')
   return(pd.read_csv('FIFA Player Info.csv'))
       
# This support function checks if a data item is not a nonetype
def NoneTypeCheck(data, listname, item = None, iterator = None, get = None):
    if data is not None and get is not None:
        data = data.findAll(item)[iterator]
        data = data.get(get)
        listname.append(data)
    elif data is not None:
        listname.append(data.text)

# This support function converts postions into their corresponding position groups 
def position(DFColumn):
    # Four position groups
    positions = {
            'Attacker' : ['CF', 'ST', 'RW', 'RF', 'LW', 'LF'], 
            'Midfielder' : ['RM', 'LM', 'CAM', 'CM', 'CDM'],
            'Defender' : ['LB', 'LWB', 'RB', 'RWB', 'CB'],
            'Goal Keeper' : ['GK']}
    for position in positions.keys():
        if DFColumn in positions.get(position):
            return(position)

# Converts country to continent        
def continent(DFColumn):
  countries = {}
  
  # Using pycountry package retrieve the country alpha 2 code
  for country in pycountry.countries:
    countries[country.name] = country.alpha_2
    
  # Convert country alpha 2 to continent code 
  if countries.get(DFColumn) is not None:
      return(pycountry_convert.country_alpha2_to_continent_code(countries.get(DFColumn)))
  # Some countries could not be matched so we hard coded the alpha value
  elif DFColumn == 'Korea Republic':
      return(pycountry_convert.country_alpha2_to_continent_code('KR'))
  elif DFColumn == 'Korea DPR':
      return(pycountry_convert.country_alpha2_to_continent_code('KP'))
  elif DFColumn == 'Congo DR':
      return(pycountry_convert.country_alpha2_to_continent_code('CD'))
  elif DFColumn == 'Cape Verde Islands':
      return(pycountry_convert.country_alpha2_to_continent_code('CV'))
  elif DFColumn == 'China PR':
      return(pycountry_convert.country_alpha2_to_continent_code('CN'))
  elif DFColumn == 'Republic of Ireland':
      return(pycountry_convert.country_alpha2_to_continent_code('IE'))
  elif DFColumn == 'FYR Macedonia':
      return(pycountry_convert.country_alpha2_to_continent_code('MK'))
  elif DFColumn == 'St. Kitts and Nevis':
      return(pycountry_convert.country_alpha2_to_continent_code('KN'))
  elif DFColumn == 'São Tomé e Príncipe':
      return(pycountry_convert.country_alpha2_to_continent_code('ST'))
  elif DFColumn == 'Chinese Taipei':
      return(pycountry_convert.country_alpha2_to_continent_code('TW'))
  elif DFColumn == 'St. Lucia':
      return(pycountry_convert.country_alpha2_to_continent_code('LC'))
  else:
  # Used search fuzzy to search for country string in pycountry package
      return(pycountry_convert.country_alpha2_to_continent_code(pycountry.countries.search_fuzzy(DFColumn)[0].alpha_2))
                   
if __name__ == '__main__':
    DF = connection()
