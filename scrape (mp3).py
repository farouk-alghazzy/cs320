from collections import deque
import os
import pandas as pd
from io import StringIO
import requests
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager



import time
import requests
from selenium.webdriver.common.by import By

import time
import requests
from selenium.webdriver.common.by import By

class GraphSearcher:
    def __init__(self):
        self.visited = set()
        self.order = []

    def visit_and_get_children(self, node):
        """ 
        Leave this method as is! It will be over-written in the child classes.
        Each child class should perform the following:
            - Record the node value in self.order
            - Return its children
            parameter: node
            return: children of the given node
        """
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        self.visited.clear()
        self.order = []
        self.dfs_visit(node)

    def dfs_visit(self, node):
        if node in self.visited:
            return

        self.visited.add(node)
        children = self.visit_and_get_children(node)
        for child in children:
            self.dfs_visit(child)

    def bfs_search(self, node):
        self.visited.clear()
        self.order = []
        queue = deque([node])

        while queue:
            current_node = queue.popleft()
            if current_node not in self.visited:
                self.visited.add(current_node)
                children = self.visit_and_get_children(current_node)
                queue.extend(children)
class MatrixSearcher(GraphSearcher):
    def __init__(self, df):
        super().__init__()
        self.df = df

    def visit_and_get_children(self, node):
        self.order.append(node)
        children = [child_node for child_node, has_edge in self.df.loc[node].items() if has_edge == 1]
        return children
    
class FileSearcher(GraphSearcher):
    def __init__(self):
        super().__init__()

    def visit_and_get_children(self, node):
        filepath = os.path.join('file_nodes', node)
        with open(filepath, 'r') as file:
            lines = file.readlines()
            value = lines[0].strip()
            self.order.append(value)
            children = lines[1].strip().split(',') if len(lines) > 1 else []
        return children

    def concat_order(self):
        return ''.join(self.order)

    

class WebSearcher(GraphSearcher):
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.table_fragments = []

    def visit_and_get_children(self, node):
        self.driver.get(node)
        self.order.append(node)
        
        children = [link.get_attribute('href') for link in self.driver.find_elements(By.TAG_NAME, 'a') if link.get_attribute('href')]
        
        html_content = self.driver.page_source
        tables = pd.read_html(StringIO(html_content))
        self.table_fragments.extend(tables)
        
        return children

    def table(self):
        return pd.concat(self.table_fragments, ignore_index=True)
        
def reveal_secrets(driver, url, travellog):
    driver.get(url)
    pswd = ""

    for i, data in travellog.iterrows():
        clue = data["clue"]
        pswd += str(clue)
    pwd_input = driver.find_element(By.ID, "password-textbox")
    pwd_input.send_keys(pswd)

    go_btn = driver.find_element(By.ID, "submit-button")
    go_btn.click()
    time.sleep(10)
    location_btn = driver.find_element(By.ID, "location-button")
    location_btn.click()
    time.sleep(10)
    
    location_img = driver.find_element(By.ID, "image")
    img_url = location_img.get_attribute("src")
    img_response = requests.get(img_url)
    with open("Current_Location.jpg", "wb") as file:
        file.write(img_response.content)
        
    current_place = driver.find_element(By.ID, "location").text
    return current_place
