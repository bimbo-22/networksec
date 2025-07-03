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
        
    


