import requests

def fetch_currencies_frankfurter():
    """Fetch currencies from Frankfurter API"""
    url = "https://api.frankfurter.dev/v2/rates"
    
    try:
        response = requests.get(
            url,
            params={"base": "USD"},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return True, data
    
    except requests.exceptions.RequestException as e:
        return False, {"error": f"Error fetching currencies: {str(e)}"}