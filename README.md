A new extremely light implementation of Liquid Democracy. 

Technology:
==========
* It uses a Neo4j-Graphdatabase via bulbs (http://bulbflow.com)
* It uses the Python micro webframework Flask

Install: 
========
* Install neo4j-server und run the server via
  ```bash
  $ cd /path/to/neo4j
  $ bin/neo4j start
  ```

* create a new local python environment
  ```bash
  $ virtual-env venv
  ```

* activate the environment
  ```bash
  $ source venv/bin/activate
  ```

* Install Flask, Bulbs
  ```bash
  $ pip install flask
  $ pip install bulbs
  ```

* clone the git-repo and start the main programm
  ```bash
  $ python liquidDemocracyLight.py
  ```

* open a webbrowser and call http://localhost:5000






