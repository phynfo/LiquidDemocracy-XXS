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
  pro = Integer(nullable=False) # 0: against ; 1: pro
  created = DateTime(default=current_datetime, nullable=False)

class Proposal(Node):
  element_type = 'proposal'
  title = String(nullable=False)
  body = String(nullable=False)
  datetime_created = DateTime(default=current_datetime, nullable=False)
  datetime_modification = DateTime()
  votes_up = Integer() #deprecated
  votes_down = Integer() # deprecated

class Instance(Node):
  element_type = 'instance'
  title = String(nullable=False)
  body = String(nullable=False)
  datetime_created = DateTime(default=current_datetime, nullable=False)

class Comment(Node):
  element_type = 'comment'
  title = String(nullable=False)
  body = String(nullable=False)
  datetime_created = DateTime(default=current_datetime, nullable=False)
  datetime_modification = DateTime()

class HasComment(Relationship):
  label = 'hasComment'
  created = DateTime(default=current_datetime, nullable=False)

class IssuesComment(Relationship):
  label = 'issuesComment'
  created = DateTime(default=current_datetime, nullable=False)

class Graph(Neo4jGraph):
  def __init__(self, config=None):
    super(Graph, self).__init__(config)
    self.people = self.build_proxy(Person)
    self.proposals = self.build_proxy(Proposal)
    self.issues = self.build_proxy(Issues)
    self.votes = self.build_proxy(Votes)
    self.comments = self.build_proxy(Comment)
    self.issuesComment = self.build_proxy(IssuesComment)
    self.hasComment = self.build_proxy(HasComment)



