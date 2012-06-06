from bulbs.model import Node, Relationship
from bulbs.property import String, DateTime, Integer
from bulbs.neo4jserver import Graph as Neo4jGraph
from bulbs.utils import current_datetime

class Person(Node):
  element_type = 'person'
  firstname = String(nullable=False)
  secondname = String(nullable=False)
  username = String(nullable=False)
  password = String(nullable=False)
  email = String(nullable=False)

class Issues(Relationship):
  label = 'issued'
  created = DateTime(default=current_datetime, nullable=False)

class Votes(Relationship):
  label = 'votes'
  created = DateTime(default=current_datetime, nullable=False)

class Proposal(Node):
  element_type = 'proposal'
  title = String(nullable=False)
  body = String(nullable=False)
  datetime_created = DateTime(default=current_datetime, nullable=False)
  datetime_modification = DateTime()
  votes_up = Integer()
  votes_down = Integer()

class Graph(Neo4jGraph):
  def __init__(self, config=None):
    super(Graph, self).__init__(config)
    self.people = self.build_proxy(Person)
    self.proposals = self.build_proxy(Proposal)
    self.issues = self.build_proxy(Issues)
    self.votes = self.build_proxy(Votes)


