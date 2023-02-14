import time

from selenium import webdriver


def poll_site(url, num_requests, wait_time, chromedriver_path):
    for i in range(num_requests):              
        # spin up the browser, point to a randomly-chosen URL, wait a
        # few seconds, then kill the browser. Wait for next iteration
        driver = webdriver.Chrome(executable_path=chromedriver_path)
        driver.get(url)

        time.sleep(wait_time)
        html = driver.page_source
        driver.quit()
        print(f"> Request {i+1} completed")
        # time.sleep(wait_time)
        return html

def main():
    url = "http://www.bbc.co.uk"
    num_requests = 1
    wait_time = 3
    chromedriver_path = "chromedriver.exe"

    html = poll_site(url=url, num_requests=num_requests, wait_time=wait_time, 
                    chromedriver_path=chromedriver_path)
    print(html)

if __name__ == "__main__":
    main()