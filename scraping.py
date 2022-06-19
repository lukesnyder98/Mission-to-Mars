# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        # Create a new dictionary to hold a list of dictionaries
        # with the URL string and title of each hemisphere image
        "hemispheres": scrape_hemispheres(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

# Create a function that will scrape the hemisphere data by using code from the Mission_to_Mars_Challenge.py file
# At the end of the function, return the scraped data as a list of dictionaries with the URL string and title of
# each hemisphere image
def scrape_hemispheres(browser):
    hemisphere_image_urls = []

    url = 'https://marshemispheres.com/'
    browser.visit(url)

    for x in range (0,4):
        html = browser.html
        mars_soup = soup(html, 'html.parser')

        hemispheres = {}
        
        hemisphere_elem = mars_soup.find_all('div', class_='item')[x]
        hemisphere_url_rel = hemisphere_elem.find('a').get('href')
        hemisphere_url = f'https://marshemispheres.com/{hemisphere_url_rel}'
        browser.visit(hemisphere_url)
        
        html = browser.html
        img_soup = soup(html, 'html.parser')
        
        img_elem = img_soup.find('ul')
        img_url_rel = img_elem.find('a').get('href')
        hemispheres['img_url']= f'https://marshemispheres.com/{img_url_rel}'
        hemispheres['title']=img_soup.find('h2', class_='title').get_text()
        hemisphere_image_urls.append(hemispheres)
        browser.back()

    return hemisphere_image_urls

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())