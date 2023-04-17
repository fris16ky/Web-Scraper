from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup

#This personal project is my first attempt at Web Scraping
#The idea is to parse through my profile on a site called MyAnimeList (https://myanimelist.net/animelist/Fris16ky)
#My favorite show of all time is One Piece, and it's pretty long too, so I want to see how long I've spent watching it!
#Everytime I watch a new episode/movie, I can add it to MyAnimeList, and this code will keep up and tell me the statistics (shows watched + duration)

#We're using Selenium since it'll open it's own Google Chrome tab instead of taking the HTML code from when the site is loaded normally
#The tags I need (for show names, durations, etc.) are added dynamically, so they're not on the base HTML
from selenium import webdriver
from selenium.webdriver.common.by import By

#Arrays for the show names, duration (in hours and minutes), and the hyperlinks to each show's page
movie_names = []
movie_durations = []
movie_links = []

#Starting the Web Scrape process

#Create a new instance of the Chrome driver
driver = webdriver.Chrome()
#Navigate to my MyAnimeList page
driver.get("https://myanimelist.net/animelist/Fris16ky")

#Wait 10 seconds for the page to load
driver.implicitly_wait(10)
#Get the page source/all of it's code
html = driver.page_source

#Code to get the episode count of the One Piece main show
soup = BeautifulSoup(html, "html.parser")
#Find the tag that contains the progress/episodes watched (anything that contains the words "One Piece")
findProgress = soup.find("a", string=lambda text: "One Piece" in str(text))

if findProgress is not None:
    #As long as we found a One Piece show, extract the episode count from the next sibling tag
    episode_count = findProgress.find_next(class_="progress-21").text.strip()
    #We only want the number (i.e. 939) from the Episode Progress; get rid of spaces and other characters
    episode_count = "".join(c for c in episode_count if c.isalnum())
else:
    print("Could not find One Piece in the list.")

#Code to get the href and names for each One Piece show (including the main show)
#Find all the anchor tags containing "One Piece"
elements = driver.find_elements(By.XPATH, '//a[contains(text(), "One Piece")]')
for element in elements:
    #Adding the links to the movie_links array; adding the string names to the movie_names array
    movie_links.append(element.get_attribute("href"))
    movie_names.append(element.text)

#print(movie_links)
#for logging purposes ^

#Replacing the name for Movie 07, which took the Japanese name instead of its English one
movie_names = list(map(lambda x: x.replace('One Piece Movie 07: Karakuri-jou no Mecha Kyohei', 'One Piece Movie 07: The Giant Mechanical Soldier of Kakuri Castle'), movie_names))
#Adding a period to the last movie for sanity's sake
movie_names[-1] = movie_names[-1] + "."
#Removing the "One Piece" element. We already talk about how many episodes I've watched, so no need to include this twice
movie_names.remove("One Piece")

#print(movie_names)
#Also for logging

#Close the browser
driver.quit()

#Parsing through each movie link to get its duration
for link in movie_links: 
    url = link
    response = requests.get(url)
    html_content = response.content
    soup = BeautifulSoup(html_content, "html.parser")
    #Find the tag that contains the duration; the span before the duration has a text of "Duration:"
    duration_tag = soup.find("span", string="Duration:")
    #Extract the duration (in hours/minutes) from the next sibling tag
    duration = duration_tag.next_sibling.strip()
    #Add the duration to the movie_durations array
    movie_durations.append(duration)

#Printing the show/movie names
print() #Extra line before to separate from coding glob
print("You have watched", episode_count, "episodes of One Piece! You have also watched the following films: ")
#Special code to print the elements of the array (movie names) all in one line
for i in range (len(movie_names)): 
    if i == len(movie_names) - 1: 
        #If we're at the last element, we don't need a comma
        print("and", movie_names[i])
    else: 
        #Put a comma in between each movie/film
        print(movie_names[i], end=", ")

#Converting the movie durations array into the totalled minutes
def convert_time(array): 
    #Given an array of strings in the format: xx min. or xx hr. xx min.
    total_minutes = 0
    for time in array: 
        #Splitting the elements up by spaces
        parts = time.split(' ')
        movie_minutes = 0 #number of minutes for each movie
        for i, part in enumerate(parts): 
            if part.isdigit(): 
                if i < len(parts) - 1 and parts[i+1] == 'min.': 
                    #If we're not at the end and we're looking at minutes, add them to the current movie_minutes
                    movie_minutes += int(part)
                elif i < len(parts) - 1 and parts[i+1] == 'hr.': 
                    #If we're not at the end and we're looking at the hours, multiply by 60 then add to the current movie_minutes
                    movie_minutes += int(part) * 60
                else: 
                    movie_minutes += int(part)
        total_minutes += movie_minutes
    #For the One Piece main series (non-movie), we need to multiply it's general duration by how many episodes I've watched
    #Including intro and outro, the average/general duration is 24 minutes per episode
    total_minutes += (int(episode_count) - 1) * 24
    total_hours = total_minutes / 60

    print() #For a new line
    print("You have spent", '{:,.0f}'.format(total_minutes), "minutes watching One Piece, which is also equal to", round(total_hours, 3), "hours, or", round(total_hours/24, 3), "days!")
    #Special formatting to make 10000 go to 10,000, and rounding for clean numbers
convert_time(movie_durations)
print() #Line after for a cleaner viewing and reading
#Currently (8 Movies, 939 Episodes) this will print 23,178 minutes or 386.3 Hours or 16.096 Days
