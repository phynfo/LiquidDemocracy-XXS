# A light implementation of Liquid Democracy. 

It is "light" with respect to:

* **Technology:** 
   - It uses a Neo4j-Graphdatabase via bulbs (http://bulbflow.com), i.e. a REST-interface 
     (instead of a RDBMS)
   - It uses the Python micro webframework Flask
     (instead of a full-blown framework like Django or Pyramide)
   - No caching
   - No i18n
   - Little security
   - Hardly any javascript

* **Software Engineering:** 
   - No fancy abstraction layers
   - No built-in version-management of items. 
   - No "Design Patterns".

* **Requirements:** It implements just the core set of requirements, i.e.
  - **Instances:** An instance comprises a set of proposals and users. -- *implemented* --
  - **Users:** Basic user-management (login, sign-in, logout) -- *implemented* --
  - **Proposals:** Add, delete, view Proposals. -- *implemented* --
  - **Voting:** One Up-Vote/Down-Vote per User per Proposal / Comment. -- *implemented* --
  - **Comments:** Add, delete and vote for discussion-comments of a proposal. -- *implemented* --
  - **Rationals:** Add, delete and vote for pro-/con-rationals of a proposal. -- *not yet implemented* --
  - **Delegations:** Delegate own vote to other user(s) relative to parlament, proposal or whole instance. 
    -- *right in the process of being implemented* -- 
    (I dont yet know: Should the delegation also be projected to past actions?) 
  - **Parlaments:** Add, delete Parlaments (in which proposals can be raised); actually, that's nothing but a
    mechanism to tag proposals. 
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
  (venv)$ pip install flask
  (venv)$ pip install bulbs
  ```

* clone/copy this git-repo and start the main programm 
  ```bash
  (venv)$ git clone https://github.com/phynfo/LiquidDemocracy-XXS.git liquidDemocracyXXS
  (venv)$ cd LiquidDemocracy-XXS
  (venv)$ python liquidDemocracyLight.py
  ```
  Be sure *not* to use the global  `/usr/bin/python`-Python but the local `.../venv/bin/python`-Python of the local environment. 

* open a webbrowser and call http://localhost:5000

## Use the Test Data

* You are free to use the Neo4j-test data, provided in the `data`-folder of this repository. 

* It contains proposals (written in german), Users (which all use the password `bla`; the admin-user is
* `tobias`), Comments (written in german), Parlaments, Votings, two Instances.  

* Install the test data by copying the `data`-Folder to `/path/to/neo4j`
  (probably just copying will work, however I am not fully sure about it). 


## Install on Windows 

I found it much easier to set up the development environment on a Linux-System. Perhaps you want to install Linux 
e.g. on VirutalBox inside Windows and go on with the above instructions? If not, try to do the following:

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
  Note: To get it all working, you must have a compiler installed (e.g. Visual Studio 2008 or mingw)

* Download the latest **stable** release of the Neo4j-Graphdatabase (http://neo4j.org)
* Start the Neo4j-Server (you need a Java Runtime Environment for that): 
  ```
  > bin\Neo4j.bat
  ```
* Run the script liquidDemocracy.py with python; a Test-Webserver is included.





