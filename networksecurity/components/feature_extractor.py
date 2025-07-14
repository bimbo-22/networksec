from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import FeatureExtractorConfig

from urllib.parse import urlparse
import re
import requests
import pandas as pd
import whois 
import dns.resolver
import dns.rdatatype
import dns.exception
from datetime import date
from serpapi import GoogleSearch
import sys
import os
import ssl 
import BeautifulSoup
from bs4 import BeautifulSoup

class FeatureExtractor:
    def __init__ (self, feature_extractor_config:
        FeatureExtractorConfig):
        try:
            self.feature_extractor_config = feature_extractor_config
            self.serpapi_key = self.feature_extractor_config.serpapi_key
            if not self.serpapi_key:
                raise ValueError("SERPAPI key is not set in the environment variables.")
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def extract_having_ip_address(url):
        pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        return 1 if re.search(pattern, url) else 0
    
    def extract_url_length(self,url):
        if len(url) > self.feature_extractor_config.url_length_threshold:
            return 1
        return 0
    
    def extract_shortening_service(self, url):
        shortening_services = [
            "bit.ly", "goo.gl", "tinyurl.com", "is.gd", "t.co",
            "ow.ly", "buff.ly", "adf.ly", "shorte.st", "rebrandly.com"
        ]
        parsed_url = urlparse(url)
        return 1 if parsed_url.netloc in shortening_services else 0
    
    def extract_having_at_symbol(self, url):
        return 1 if "@" in url else 0
    
    def extract_double_slash_redirecting(self, url):
        parsed_url = urlparse(url)
        return 1 if parsed_url.count("//") > 1 else 0
    
    def extract_prefix_suffix(self, url):
        domain = urlparse(url).netloc
        return 1 if '-' in domain or domain.startswith('www.') or domain.endswith('.com') else 0
    
    def extract_subdomain_count(self, url):
        domain_parts = urlparse(url).netloc
        subdomains = domain_parts.split('.')
        if len(subdomains) > self.feature_extractor_config.max_subdomains:
            return 1
        return 0
    
    def extract_SSLfinalstate(self, url):
        try:
            response = requests.get(url, timeout=self.feature_extractor_config.requests_timeout)
            return 1 if response.url.startswith('https://') and not response.history else 0
        except (requests.RequestException, ssl.SSLError):
            return 0
        
    def extract_domain_registration_length(self, url):
        try:
            w = whois.whois(urlparse(url).netloc)
            creation_date = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
            if creation_date:
                age_days = (date.today() - creation_date).days
                return 1 if age_days >= self.feature_extractor_config.min_domain_age_days else 0
        except Exception as e:
            logging.error(f"Error extracting domain registration length: {e}")
            return 0
        
    def extract_favicon(self, url):
        try: 
            response = requests.get(url, timeout=self.feature_extractor_config.requests_timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            favicon = soup.find("link", rel="icon") or soup.find("link", rel="shortcut icon")
            if favicon and "href" in favicon.attrs:
                favicon_url = urlparse(favicon['href']).netloc
                return 1 if favicon_url and favicon_url != urlparse(url).netloc else 0
            return 0
        except requests.RequestException as e:
            raise NetworkSecurityException(f"Error fetching favicon: {e}", sys)
        
    def extract_port(self, url):
        parsed_url = urlparse(url)
        port = parsed_url.port if parsed_url.port else (443 if parsed_url.scheme == 'https' else 80)
        return 1 if port not in [80, 443] else 0
    
    def extract_https_token(self, url):
        parsed_url = urlparse(url)
        if parsed_url.scheme == 'https':
            return 1
        return 0
    
    def extract_request_url(self, url):
        try:
            response = requests.get(url, timeout=self.feature_extractor_config.requests_timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all(["a", "img", "script", "link"], href=True)
            external_count = sum(1 for link in links if urlparse(link.get('src', link.get('href'))).netloc != urlparse(url).netloc)
            return 1 if external_count / len(links) > 0.5 else 0
        except requests.RequestException as e:
            raise NetworkSecurityException(f"Error extracting request URL: {e}", sys)
        
    def extract_url_of_anchor(self,url):
        try:
            response = requests.get(url, timeout=self.feature_extractor_config.requests_timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            anchors = soup.find_all('a', href=True)
            external_count = sum(1 for anchor in anchors if urlparse(anchor['href']).netloc != urlparse(url).netloc)
            return 1 if external_count / len(anchors) > 0.3 else 0
        except requests.RequestException as e:
            raise NetworkSecurityException(f"Error extracting URL of anchor: {e}", sys)
        
    def extract_links_in_tags(self, url):
        try: 
            response = requests.get(url, timeout=self.feature_extractor_config.requests_timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            tags = soup.find_all(['a', 'link', 'script'])
            return 1 if len(tags) > self.feature_extractor_config.max_links_in_tags else 0
        except requests.RequestException as e:
            raise NetworkSecurityException(f"Error extracting links in tags: {e}", sys)
        
    def extract_sfh(self, url):
        try:
            response = requests.get(url, timeout=self.feature_extractor_config.requests_timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            form = soup.find('form')
            if form in form.attrs:
                action = form.get('action', '').lower()
                if not action or "about:blank" in action or urlparse(action).netloc != urlparse(url).netloc:
                    return 1
            return 0
        except requests.RequestException as e:
            raise NetworkSecurityException(f"Error extracting SFH: {e}", sys)
        
    def extract_submitting_to_email(self, url):
        try:
            response = requests.get(url, timeout=self.feature_extractor_config.requests_timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            forms = soup.find_all('form')
            for form in forms:
                action = form.get('action', '').lower()
                if "@" in action:
                    return 1
            return 0
        except requests.RequestException as e:
            raise NetworkSecurityException(f"Error extracting submitting to email: {e}", sys)
        
    def extract_abnormal_url(self,url):
        special_chars = r'[@_!#$%^&*()<>?/\|}{~:,.]'
        count = len(re.findall(special_chars, url))
        return 1 if count > 5 else 0
    
    def extract_redirect(self, url):
        try:
            response = requests.get(url, timeout=self.feature_extractor_config.requests_timeout, allow_redirects=True)
            return 1 if len(response.history) > 0 else 0
        except requests.RequestException as e:
            raise NetworkSecurityException(f"Error extracting redirect: {e}", sys)
    
    def extract_on_mouseover(self, url ):
        try: 
            response = requests.get(url, timeout=self.feature_extractor_config.requests_timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            elements = soup.find_all(lambda tag: tag.get('onmouseover') or tag.get('onmouseout'))
            return 1 if elements else 0
        except requests.RequestException as e:
            raise NetworkSecurityException(f"Error extracting on mouseover: {e}", sys)
        
    def extract_rightclick(self, url):
        try:
            response = requests.get(url, timeout=self.feature_extractor_config.requests_timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            body = soup.find('body')
            if body and 'oncontextmenu' in str(body).lower() and 'return false' in str(body).lower():
                return 1
            return 0
        except requests.RequestException as e:
            raise NetworkSecurityException(f"Error extracting right click: {e}", sys)
        
    def extract_popupwindow(self, url):
        try:
            response = requests.get(url, timeout=self.feature_extractor_config.requests_timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            scripts = soup.find_all('script')
            for script in scripts:
                if 'window.open' in str(script).lower():
                    return 1
        except requests.RequestException as e:
            raise NetworkSecurityException(f"Error extracting popup window: {e}", sys)
        
    def extract_iframe(self, url):
        try:
            response = requests.get(url, timeout =  self.feature_extractor_config.requests_timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            iframes = soup.find_all('iframe')
            return 1 if len(iframes) > self.feature_extractor_config.max_iframes else 0
        except requests.RequestException as e:
            raise NetworkSecurityException(f"Error extracting iframe: {e}", sys)
        
    def extract_age_of_domain(self, url):
        try:
             w = whois.whois(urlparse(url).netloc)
             creation_date = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
             if creation_date:
                 age_days = (date.today() - creation_date).days
                 return 1 if age_days >= self.feature_extractor_config.min_domain_age_days else 0
        except Exception as e:
            raise NetworkSecurityException(f"Error extracting age of domain: {e}", sys)
        
    def extract_dns_record(self, url):
        try:
            domain = urlparse(url).netloc
            dns.resolver.default_resolver(domain,  'A')
            return 1 
        except (dns.exception.DNSException, Exception) as e:
            logging.error(f"DNS record extraction failed: {e}")
            return 0
        
    def extract_web_traffic(self, url):
        try:
            params = {
                "q": url,
                "api_key": self.serpapi_key,
                "engine": "google",
                "hl": "en",
                "gl": "us"
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            organic_results = results.get('organic_results', [])
            return 1 if len(organic_results) > 0 else 0 # a simple check
        except Exception as e:
            raise NetworkSecurityException(f"Error extracting web traffic: {e}", sys)
        
    def extract_page_rank(self, url):
        try:
            params = {
                "q": url,
                "api_key": self.serpapi_key,
                "engine": "google",
                "hl": "en",
                "gl": "us"
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            organic_results = results.get('organic_results', [])
            return 1 if organic_results and organic_results[0].get('position')  <= 10 else 0
        except Exception as e:
            raise NetworkSecurityException(f"Error extracting page rank: {e}", sys)
        
    def extract_google_index(self, url):
        try:
            params = {
                "q": url,
                "api_key": self.serpapi_key,
                "engine": "google",
                "hl": "en",
                "gl": "us"
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            return 1 if results.get('search_information', {}).get('total_results', 0) > 0 else 0
        except Exception as e:
            raise NetworkSecurityException(f"Error extracting Google index: {e}", sys)
        
    def extract_links_pointing_to_page(self, url):
        try:
            params = {
                "q": url,
                "api_key": self.serpapi_key,
                "engine": "google",
                "hl": "en",
                "gl": "us"
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            return 1 if results.get('search_information', {}).get('total_results', 0) > 10 else 0
        except Exception as e:
            raise NetworkSecurityException(f"Error extracting links pointing to page: {e}", sys)
        
    def extract_statisical_report(self, url):
        # i need to implement the pretrained model here to extract the statistical report
        # -- skipping for now
        pass
    
    def extract_features(self, url: str) -> pd.DataFrame:
        try:
            features = {
                "ip_address": self.extract_having_ip_address(url),
                "url_length": self.extract_url_length(url),
                "shortening_service": self.extract_shortening_service(url),
                "having_at_symbol": self.extract_having_at_symbol(url),
                "double_slash_redirecting": self.extract_double_slash_redirecting(url),
                "prefix_suffix": self.extract_prefix_suffix(url),
                "subdomain_count": self.extract_subdomain_count(url),
                "SSL_final_state": self.extract_SSLfinalstate(url),
                "domain_registration_length": self.extract_domain_registration_length(url),
                "favicon": self.extract_favicon(url),
                "port": self.extract_port(url),
                "https_token": self.extract_https_token(url),
                "request_url": self.extract_request_url(url),
                "url_of_anchor": self.extract_url_of_anchor(url),
                "links_in_tags": self.extract_links_in_tags(url),
                "sfh": self.extract_sfh(url),
                "submitting_to_email": self.extract_submitting_to_email(url),
                "abnormal_url": self.extract_abnormal_url(url),
                "redirect": self.extract_redirect(url),
                "on_mouseover": self.extract_on_mouseover(url),
                "right_click": self.extract_rightclick(url),
                "popup_window": self.extract_popupwindow(url),
                "iframe": self.extract_iframe(url),
                "age_of_domain": self.extract_age_of_domain(url),
                "dns_record": self.extract_dns_record(url),
                "web_traffic": self.extract_web_traffic(url),
                "page_rank": self.extract_page_rank(url),
                "google_index": self.extract_google_index(url),
                "links_pointing_to_page": self.extract_links_pointing_to_page(url)
            }
            return pd.DataFrame([features])
        except Exception as e:
            raise NetworkSecurityException(f"Error extracting features: {e}", sys)
        
        
    


