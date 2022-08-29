# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
import chromedriver_autoinstaller
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': chromedriver_autoinstaller.install()}
    browser = Browser('chrome', **executable_path, headless=False)

    news_title, news_paragraph = mars_news(browser)

    hemisphere_image_urls = scrape_challenge(browser)

    # Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "hemispheres": hemisphere_image_urls,
      "last_modified": dt.datetime.now()

    }



    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:

        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p



def featured_image(browser):

    # Visit URL
    url = 'https://spaceimages-mars.com/'
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


    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url


def mars_facts():
    try:
       # use 'read_html" to scrape the facts table into a dataframe
       df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
       return None


    # Assign columns and set index of dataframe
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)


    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()

def scrape_challenge(browser):

    url = 'https://marshemispheres.com/'
    browser.visit(url)

    hemisphere_holding_list = []

    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:

        img_url_list = []
        images = img_soup.find_all('img', {'class': 'thumb'})
        for img in images:
            if img.has_attr('src'):
                print(img['src'])
                img_url_list.append(img['src'])

    
        for item in img_url_list:
            hemisphere_holding_list.append(f'https://marshemispheres.com/{item}')

        html = browser.html
        news_soup = soup(html, 'html.parser')
        news = news_soup.find_all('div', attrs={'class':'description'})

        titles = []
        for result in news:
            title = result.find('a', class_='itemLink product-item').get_text()
            titles.append(title)

        titles = [title.replace('\n', '') for title in titles]

        full_list = [item for sublist in zip(hemisphere_holding_list, titles) for item in sublist]

        key_list = ["img_url","title"]
        length = len(full_list)
        new_list = []
        for item in range (0, length, 2):
            new_list.append({key_list[0]: full_list[item], key_list[1] : full_list[item + 1]})

        hemisphere_image_urls = new_list

    except AttributeError:
        return None

    return hemisphere_image_urls

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())