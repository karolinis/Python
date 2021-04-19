from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import networkx as nx


#function that with given url will collect hashtags and return a 2 dimentional list with
#the hashtags and their links
def hasher(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path='../premarket/chromedriver.exe', options=chrome_options)
    driver.get(url)

    #tries to go into the hashtag, if there are no hashtags or they are unretrievable, it will run the function again
    try:
        #wait max 20 seconds for all hashtags to appear
        tweets = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//span[@class='r-18u37iz']/a")
            ))
    except:
        hasher(url)

    #find all hashtags and user links
    bs = BeautifulSoup(driver.page_source, 'html.parser')
    divs = bs.find_all('span', {'class': 'r-18u37iz'})

    #2 dimensional array for url endings and hashtag names
    queue = []
    for div in divs:
        #put both to lower to not get same hashtag in upper and lower letters
        #picking up hashtag text and href of it
        hashtag = div.get_text().lower()
        #if there's no href in span, pass, because it's not a hashtag
        try:
            hashtag_link = div.a['href'].lower()
        except:
            hashtag_link = ''
            pass

        #check if hashtag, duplication
        if '/hashtag' in hashtag_link and [hashtag_link,hashtag] not in queue:
            queue.append([hashtag_link,hashtag])

    return queue

#will be used as a link maker
main_url = 'https://twitter.com'
#used to not visit a same website twice
visited = []
#main urls to start with
urls = [['https://twitter.com/search?q=%23newyork','#newyork'],['https://twitter.com/search?q=%23dog','#dog']]


G = nx.Graph()
#manually adding the start nodes
G.add_node('#newyork')
G.add_node('#dog')
#will crawl the 2 main hashtags
for url, main_tag in urls:
    #making a variable of the function return
    queue = hasher(url)
    #keeping visited updated, to not visit it twice
    visited.append(url)
    #loop through the list of hashtags that will be crawled
    for link, tag in queue:
        page = main_url+link
        if page not in visited and len(visited) <= 20:
            #add node for all 20 hashtags found in newyork
            G.add_node(tag)
            #add edge from all found hashtags to newyork
            G.add_edge(main_tag,tag)
            visited.append(page)
            #will go into the already found hashtags to find their own hashtags
            new_queue = hasher(page)
            #adding nodes from a list of hashtags
            G.add_nodes_from([tag for link, tag in  new_queue])
            #same with edges
            for link, taggy in new_queue:
                G.add_edge(tag, taggy)
        else:
            pass

nx.write_graphml(G, "newyorkdog.graphml")