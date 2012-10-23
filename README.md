# A light implementation of Liquid Democracy. 

It is "light" with respect to:

* **Technology:** 
   - It uses a Neo4j-Graphdatabase via bulbs (http://bulbflow.com), i.e. a REST-interface 
     (instead of a RDBMS)
   - It uses the Python micro webframework Flask
     (instead of a full-blown framework like Django or Pyramide)
   - No caching
   - Little security
   - Hardly any javascript
   - ...

* **Software Engineering:** 
   - It uses no fancy abstraction layers
   - It uses no built-in version-management of items. 
   - It uses no "Design Patterns".

* **Requirements:** It implements just the core set of requirements, i.e.
  - **Instances:** An instance comprises a set of proposals and users.
  - **Users:** Basic user-management (login, sign-in, logout)
  - **Proposals:** Add, delete, view Proposals.
  - **Voting:** One Up-Vote/Down-Vote per User per Proposal / Comment.
  - **Comments:** Add, delete and vote for discussion-comments of a proposal. 
  - **Rationals:** Add, delete and vote for pro-/con-rationals of a proposal. -- *not implemented yet* --
  - **Delegations:** Delegate own vote to other user(s) relative to parlament, proposal or whole instance. 
    -- *right in the process of being implemented* -- 
    (I dont yet know: Should the delegation also be projected to past actions?) 
  - **Parlaments:** Add, delete Parlaments (in which proposals can be raised); Maybe that should be nothing but a mechanism to tag
    -- *just implemented* --


## Install on a Linux-System 

* Install neo4j and neo4j-server to a path of your choice (say: `/path/to/neo4j`) and start the server via
  ```bash
  $ cd /path/to/neo4j
  $ bin/neo4j start
  ```

* create a new local python environment
  ```bash
  $ virtualenv venv
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

## Use the Test Data

* You are free to use my test data, which can be found in the `data`-folder of this repository. 

* It contains proposals (written in german), Users (which all use the password `bla`), Comments (written in german), Parlaments,
  Votings, two Instances. 

* Install the test data by copying the `data`-Folder to `/path/to/neo4j`
  (hopfully just copying will work, I am not fully sure about it). 

* The admin is `tobias` (username) and `bla` as password.


## Install on Windows 

I find it much easier to set up the development environment on Linux. Perhaps you want to install Linux e.g. on 
VirutalBox inside Windows and go on with the above instructions? If not, try to do the following:

### Install python, setuptools and pip

* install setuptools from http://pypi.python.org/pypi/setuptools
* Add C.\\Python2x\ and C:\\Python2x\scripts to the windows path variable
* Open a new DOS shell and run 
  ```
  > easy_install pip
  ```

* activate the environment
  ```
  > \path\to\env\Scripts\activate
  ```

* install flask, bulbs and dateutil
  ```
  > pip install flask
  > pip install bulbs
  > pip install python-dateutil
  ```
  Note: To get it all working, you must have a compiler installed (Visual Studio 2008 or mingw)

* Download the latest **stable** release of the neo4j--Graphdatabase (http://neo4j.org)
* Start the neo4j-Graphdatabase-Server (you need a Java Runtime Environment for that): 
  ```
  > bin\Neo4j.bat
  ```
  (you access the REST-API via a browser opening http:\\localhost:7474)






