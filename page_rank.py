import sys
import networkx as nx
import os
import numpy as np
import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlparse, urljoin
from scrapy.linkextractors import LinkExtractor
import matplotlib.pyplot as plt

import requests
from bs4 import BeautifulSoup

def reinforce_edges(graph):
    print("\nReinforcing internal edges using BeautifulSoup...")

    # List of all nodes (URLs) already in the graph
    all_nodes = list(graph.nodes())

    for source in all_nodes:
        try:
            response = requests.get(source, timeout=5)
            if "text/html" not in response.headers.get("Content-Type", ""):
                continue  # Only parse HTML pages

            soup = BeautifulSoup(response.text, "html.parser")
            links = [urljoin(source, a.get('href')) for a in soup.find_all('a', href=True)]

            for target in links:
                if target in graph:
                    # If target node exists in graph, add edge
                    if source != target:
                        graph.add_edge(source, target)


        except Exception as e:
            print(f"Failed to fetch {source}: {e}")

    print("Reinforcement complete.\n")



import random

class SimpleCrawler(scrapy.Spider):
    name = 'simple_crawler'

    def __init__(self, start_urls, domain, graph, max_nodes, *args, **kwargs):
        super(SimpleCrawler, self).__init__(*args, **kwargs)
        random.shuffle(start_urls)  # shuffle for fairness
        self.start_urls = [url.strip() for url in start_urls]
        self.allowed_domain = domain
        self.graph = graph
        self.max_nodes = max_nodes
        self.visited = set()

    def start_requests(self):
        """Ensure we crawl from each seed page once."""
        for url in self.start_urls:
            self.graph.add_node(url)
            self.visited.add(url)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        current_url = response.url

        # ensure it's an HTML page
        content_type = response.headers.get('Content-Type', b'').decode()
        if 'html' not in content_type:
            return

        if current_url not in self.graph:
            self.graph.add_node(current_url)

        # if max nodes reached, stop crawling
        if len(self.graph) >= self.max_nodes:
            return

        # extract links from page
        extractor = LinkExtractor()
        links = extractor.extract_links(response)

        for link in links:
            target_url = link.url

            # skip if wrong domain
            if self.allowed_domain not in target_url:
                continue

            # skip if already visited
            if target_url in self.visited:
                continue

            # stop if we've hit max nodes
            if len(self.graph) >= self.max_nodes:
                break

            # add new node and edge
            self.graph.add_node(target_url)
            self.graph.add_edge(current_url, target_url)
            self.visited.add(target_url)

            # crawl next (this is what enables depth!)
            yield scrapy.Request(url=target_url, callback=self.parse)



'''
def page_rank(g, k, file):
    n = len(g) 
    # assign all nodes the same initial page rank, set to be 1/n
    rank = 1/n
    nx.set_node_attributes(g, rank, 'currentRank')
    nx.set_node_attributes(g, 0, 'upcomingRank')
    for _ in range(k):  # k iterations
        # set upcomingRank to 0 for all nodes
        for node in g.nodes():
            g.nodes[node]['upcomingRank'] = 0.0
        #  distribute ranks
        for node in g.nodes():
            current_rank = g.nodes[node]['currentRank']
            neighbors = list(g.neighbors(node))
            if neighbors:
                share = current_rank / len(neighbors)
                for neighbor in neighbors:
                    g.nodes[neighbor]['upcomingRank'] += share
            else:
                # no outgoing links = keep its rank
                g.nodes[node]['upcomingRank'] += current_rank

        # after distribution, update currentRank
        for node in g.nodes():
            g.nodes[node]['currentRank'] = g.nodes[node]['upcomingRank']
    
    # write the page rank of all the nodes in node_rank.txt
    ranks = nx.get_node_attributes(g, 'currentRank')
    with open(file, "w") as f:
        for r in ranks:
            f.writelines(f"{r}, {ranks[r]}\n")
'''
def page_rank(graph, output_file):
    pr = nx.pagerank(graph)
    with open(output_file, 'w') as f:
        for node, rank in sorted(pr.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{node} {rank}\n")

def plot_graph(g):
    plt.figure(figsize=(12, 8))

    pos = nx.spring_layout(g, seed=42)  # Layout positions for nodes

    # Draw nodes
    nx.draw_networkx_nodes(g, pos, node_size=50, node_color='skyblue')

    # Draw directed edges with arrows
    nx.draw_networkx_edges(g, pos, edge_color='gray', arrows=True, arrowsize=10, width=1)

    # Optional: Draw labels (can be cluttered for big graphs)
    nx.draw_networkx_labels(g, pos, font_size=6)

    plt.title("Directed Web Graph", fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.show()

def plot_loglog(G):
    degree_order = sorted([d for n, d in G.degree()], reverse=True)
    degree_num = np.bincount(degree_order)
    plt.loglog(range(len(degree_num)), degree_num, marker='o')
    plt.title("LogLog PLot")
    plt.xlabel("degree (log)")
    plt.ylabel("number of nodes (log)")
    plt.grid(True)
    plt.show()


def main():
    # python ./page_rank.py --crawler crawler.txt --input graph.gml --loglogplot --crawler_graph out_graph.gml  --pagerank_values node_rank.txt
    args = sys.argv

    # safety checks
    # the program accepts optional parameters: '--input'
    if '--input' in args: # check if command is to read gml file
        try: # check if file name proceeds '--input'
            file = args[args.index('--input') + 1] # find index of '--input' and increment by 1 to get file name
            if not os.path.exists(file): # check if file provided is located in the current directory 
                print(f"Error: {file} does not exist in current directory.")
                return
            else: # passed safety checks, create graph
                graph = nx.read_gml(file)
        except ValueError:
            print(f"Error: No file was provided.")
            return 
    
    elif '--crawler' in args: # check if command is to create a graph, given txt file
        try: # check if file name proceeds '--crawler'
            txtfile = args[args.index('--crawler') + 1] 
            if not os.path.exists(txtfile): # check if file provided is located in the current directory 
                print(f"Error: {txtfile} does not exist in current directory.")
                return
            else: # create a directed graph using scrapy and only visiting Html pages
                print("Starting crawl ... ")
                # open and read txt file
                with open(txtfile, 'r') as file:
                    content = file.readlines()
                
                max_nodes = int(content[0].strip())
                full_domain_url = content[1].strip()
                parsed_domain = urlparse(full_domain_url).netloc
                domain = parsed_domain

                web_pages = content[2:] # web pages to start crawling

                # Create the graph first
                graph = nx.DiGraph()

                process = CrawlerProcess(settings={
                    'USER_AGENT': 'Mozilla/5.0',  # Prevent simple block
                    'LOG_ENABLED': False,         # Disable scrapy logs to avoid clutter
                })

                # Launch the crawler
                process.crawl(SimpleCrawler, start_urls=[url.strip() for url in web_pages], domain=domain, graph=graph, max_nodes=max_nodes)
                process.start()
                #reinforce_edges(graph) for plot

               
                if '--crawler_graph' in args:
                    try:
                        out_file = args[args.index('--crawler_graph') + 1]
                        nx.write_gml(graph, out_file)
                        print(f"Graph saved to {out_file}")
                    except IndexError:
                        print("Error: No output file provided after '--crawler_graph'")
                        return
                    #plot_graph(graph)
                else:
                    print("Error: '--crawler_graph' option is missing.")
                    return
                
        except ValueError:
            print(f"Error: No file was provided.")
            return

        # now we have graph -> perform page rank algorithm
        if '--pagerank_values' in args:
            try:
                rank_file = args[args.index('--pagerank_values') + 1]
                #k=3
                page_rank(graph, rank_file)
            except ValueError:
                print(f"Error: No value was provided.")
                return
        
        if '--loglogplot' in args:
            plot_loglog(graph)
        
        
if __name__ == "__main__":
    main()