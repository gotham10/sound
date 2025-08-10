from flask import Flask, jsonify
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

@app.route('/asset-id/<int:asset_id>', methods=['GET'])
def get_asset_name(asset_id):
    url = f"https://create.roblox.com/store/asset/{asset_id}"
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        
        WebDriverWait(driver, 15).until(
            EC.title_contains("- Creator Store")
        )
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        title_text = soup.title.string
        
        if ' - Creator Store' in title_text:
            name_part = title_text.split(' - Creator Store')[0].strip()
            if '/' in name_part:
                asset_name = name_part.split('/')[-1]
                return jsonify({'name': asset_name})
            else:
                return jsonify({'name': name_part})

        return jsonify({'error': 'Asset name could not be determined from the page format.'}), 404

    except Exception as e:
        return jsonify({'error': 'An internal server error occurred.', 'details': str(e)}), 500
    finally:
        if driver:
            driver.quit()

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=8080)
