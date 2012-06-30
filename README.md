# A light implementation of Liquid Democracy. 

It is "light" with respect to:

* **Technology:** 
  It uses "light" technology: 
   - The micro-framework Flask instead of a full-blown framework like Django or Pyramide
   - The REST API of a graph-database instead of a RDBMS
  It uses (at least up to now) little technology 
   - No caching
   - Little security
   - Hardly any javascript
   - ...

* **Software Engineering:** 
   - It uses no fancy abstraction layers
   - It uses no built-in version-management of items. 
   - It uses no "Design Patterns".

* **Requirements:** It implements just the core set of requirements, i.e.
  - **Instances:** An instance comprises a set of proposals and users. -- *just implemented* --
  - **Users:** Basic user-management (login, sign-in, logout)
  - **Proposals:** Add, delete, view Proposals.
  - **Voting:** One Up-Vote/Down-Vote per User per Proposal.
  - **Comments:** Add, delete and vote for discussion-comments of a proposal. 
  - **Rationals:** Add, delete and vote for pro-/con-rationals of a proposal. -- *not implemented yet* --
  - **Parlaments:** Add, delete Parlaments (in which proposals can be raised); Maybe that should be nothing but a mechanism to tag . -- *not implemented yet* --


## Technology:
* It uses a Neo4j-Graphdatabase via bulbs (http://bulbflow.com)
* It uses the Python micro webframework Flask

## Install for running the application on localhost:5000
* Install neo4j and neo4j-server to a path of your choice (say: `/path/to/neo4j`) and start the server via
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

* Install Flask and Bulbs
  ```bash
  $ pip install flask
  $ pip install bulbs
  ```

* clone/copy this git-repo and start the main programm 
  ```bash
  $ python liquidDemocracyLight.py
  ```
  (be sure *not* to use the `/usr/bin/python`-Python but the `.../venv/bin/python`-Python of the local environment. 

* open a webbrowser and call http://localhost:5000






