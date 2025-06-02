# Web Crawler and PageRank Generator

## Overview

This project implements a web crawler that:

- Starts from one or more given web pages (seeds)

- Stays within a specified domain

- Crawls only HTML pages

- Builds a directed graph where:

    -  Nodes = web pages

    - Edges = hyperlinks between pages

- Applies the PageRank algorithm on the graph.

- Generates a log-log plot showing degree distribution._

The crawler uses Scrapy, NetworkX, and Matplotlib.

## How to Run

``` python page_rank.py [OPTIONS] ```

Options:

- ``` --crawler crawler.txt``` : Crawl web pages listed in ```crawler.txt``` and build a graph.

- ```--input graph.gml``` : Load an existing .gml graph file instead of crawling.

- ```--crawler_graph out_graph.gml``` : Save the crawled graph to a .gml file.

- ```--pagerank_values node_rank.txt``` : Save PageRank scores to a .txt file.

- ```--loglogplot``` : Plot the log-log degree distribution of the graph.

### Examples:

Crawl from seed pages:

```python page_rank.py --crawler crawler.txt --crawler_graph out_graph.gml --pagerank_values node_rank.txt --loglogplot```

Run PageRank on an existing graph:

```python page_rank.py --input graph.gml --pagerank_values node_rank.txt --loglogplot```

## crawler.txt Format
```
    100
    https://dblp.org
    https://dblp.org/pid/e/PErdos.html
    https://dblp.org/pid/s/PaulGSpirakis.html
```

- First line: Max number of nodes to crawl (e.g., 100)

- Second line: Domain to stay inside (e.g., dblp.org)

- Remaining lines: Starting URLs

## Notes on Crawler Behavior

Q: Why don't all starting URLs crawl equally?

- Scrapy launches requests for all starting URLs.

- However, whichever seed expands faster (finds more links) will dominate the crawl.

- If the max node limit is reached while one seed is expanding, other seeds are stopped.

- This is normal because crawling is asynchronous and event-driven.

Q: Why do links found by the starting URLs also get crawled?

- This is the broad crawl behavior (not linear).

- Starting from a seed URL:

    - We extract all internal links.

    - Visit those links.

    - Then extract links from those pages.

- This "wave-like" spread continues until reaching the maximum number of nodes.

In short:

    ``` Seeds start crawling in parallel, but exploration grows outward (BFS style) until the node cap. ```

# Important Libraries Used

- Scrapy: Web crawling and HTML extraction.

- NetworkX: Graph creation and PageRank computation.

- Matplotlib: Graph plotting and log-log plot visualization.

- BeautifulSoup (optional): Used by reinforce_edges() to fix broken edges (disabled by default).

