# A light implementation of Liquid Democracy. 

It is "light" with respect to:

* **Technology:** It uses as light technology (the micro-framework Flask instead of a full-blown framework like Django or
  Pyramide, the REST API of a graph-database instead of a RDBMS) and little technology (up to now no caching, little security, etc).

* **Software Engineering:** No fancy abstraction layers. No built-in version-management. Just as simple as ever possible.

* **Requirements:** It implements just the core set of requirements, i.e.
  - **Users:** Basic user-management (login, sign-in, logout)
  - **Proposals:** Add, delete, view Proposals.
  - **Voting:** One Up-Vote/Down-Vote per User.
  - **Comments:** Add, delete and vote for discussion-comments of a proposal. -- *not implemented yet* --
  - **Rationals:** Add, delete and vote for pro-/con-rationals of a proposal. -- *not implemented yet* --
  - **Parlaments:** Add, delete Parlaments (in which proposals can be raised. -- *not implemented yet* --


## Technology:
* It uses a Neo4j-Graphdatabase via bulbs (http://bulbflow.com)
* It uses the Python micro webframework Flask

## Install: 
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






