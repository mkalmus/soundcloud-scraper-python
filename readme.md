# Soundcloud Scraper (v1)

# READ THIS: Instructions for Running

## Running App with Current Data in the Github Repo (you're not caching or scraping the data yourself)
1. Ensure library dependencies are installed: `plotly` and `pandas` by typing `pip install plotly` and `pip install pandas` if you have pip. Otherwise, please read documentation for package installation.
3. Open terminal and Google Chrome and navigate to the `main-app-files` directory
4. Run the sc-scraper.py file by typing `python3 sc-scraper.py` into your terminal
5. Follow the prompts that appear in your terminal and hover over graphs in your browser to interact with them

## Fetching New Data, Updating Database and Running App 
## WARNING: Running this can take over 30 minutes (optimization in to-do) and creates new files


1. Install a Chromedriver (https://chromedriver.chromium.org/downloads, https://chromedriver.storage.googleapis.com/index.html?path=90.0.4430.24/) then change lines 64 and 184 of `final-project-scraping-dbstoring.py` to the path of  your chromedriver
1. Install libraries listed in step 1 above (`plotly` and `pandas`)
2. Ensure library dependencies are installed: `selenium`, `beautifulsoup4`, `numpy`. You can use pip to install as outlined above.
3. Delete `sc_cache.json` and `soundcloud_data.db` if they exist. 
4. Run the final-project-scraping-dbstoring.py file by typing `python3 final-project-scraping-dbstoring.py` into your terminal (NOTE: This can take 30+ and creates a new `.db` file and a large `.json` file) 
5. Run the sc-scraper.py file by typing `python3 sc-scraper.py` into your terminal
6. Follow the prompts that appear in your terminal and hover over graphs in your browser to interact with them

# To-do:

<ul>
    <li> [ ] Cache less HTML data (no styling or scripts) </li>
    <li>
         [ ] Optimize Selenium scraping process flow 
        <ul>
            <li> [ ] Use headless webdriver </li>
            <li> [ ] Find better sleep time </li>
            <li> [ ] Incorporate waiting for elements </li>
        </ul>
    </li>
</ul>
