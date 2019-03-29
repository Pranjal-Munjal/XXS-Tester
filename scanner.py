#!/usr/bin/env python

import requests
import re
import urlparse
from BeautifulSoup import BeautifulSoup as BS


class Scanner:
    def __init__(self, url, links_ignore):
        self.session = requests.Session()
        self.target_url = url
        self.target_links = []
        self.links_to_ignore = links_ignore

    def extract_links_form(self, url):
        response = self.session.get(url, verify = False)
        return re.findall('(?:href=")(.*?)"', response.content)

    def crawl(self, url=None,):
        if url == None:
            url = self.target_url
        href_links = self.extract_links_form(url)
        for link in href_links:
            link = urlparse.urljoin(url, link)

            if "#" in link:
                link = link.split("#")[0]

            if self.target_url in link and link not in self.target_links and link not in self.links_to_ignore:
                self.target_links.append(link)
                print(link)
                self.crawl(link)

    def extract_forms(self, url):
        response = self.session.get(url)
        parse_html = BS(response.content)
        return parse_html.findAll("form")

    def submit_form(self, form, value, url):
        actions = form.get("action")
        post_url = urlparse.urljoin(url, actions)
        methods = form.get("method")
        inputs_list = form.findAll("input")
        post_data = {}
        for input in inputs_list:
            input_name = input.get("name")
            input_type = input.get("type")
            input_value = input.get("value")
            if input_type == "text":
                input_value = value
            post_data[input_name] = input_value

            if methods == "post":
                return self.session.post(post_url, data=post_data)

            return requests.get(post_url, params= post_data)

    def run_scanner(self):
        for link in self.target_links:
            forms = self.extract_forms(link)

            for form in forms:
                print("[X] Testing form in " + link)
                is_vuln_xss = self.test_xss_in_form(form, link)
                print("\n\n[XXXX] XSS is discoverd in the following form \n" + link + "\nform is:")
                print(form)


            if "=" in link:
                print("[X[ Testing " + link )
                is_vuln_xss = self.test_xss_in_link(link)
                if is_vuln_xss:
                    print("\n\n[XXXX] XSS is discoverd in the following link \n" + link)


    def test_xss_in_link(self, url):
        xss_test_script = '<sCript>alert("testing")</sCript>'
        url = url.replace("=", "=" + xss_test_script)
        response = self.session.get(url)
        if xss_test_script in response.content:
            return True

    def test_xss_in_form(self, form, url):
        xss_test_script = '<script>alert("test")</script>'
        response = self.submit_form(form, xss_test_script, url)
        if xss_test_script in response.content:
            print(form)
            return True
