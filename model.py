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
  created = DateTime(default=current_datetime, nullable=False)

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

class Instance(Node):
  element_type = 'instance'
  title = String(nullable=False)
  body = String(nullable=False)
  datetime_created = DateTime(default=current_datetime, nullable=False)

class HasPeople(Relationship):
  label = 'hasPeople'
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

class HasProposal(Relationship):
  label = 'hasProposal'

class IssuesComment(Relationship):
  label = 'issuesComment'
  created = DateTime(default=current_datetime, nullable=False)

class Parlament(Node): 
  element_type = 'parlament'
  title = String(nullable=False)
  body = String(nullable=False)
  datetime_created=DateTime(default=current_datetime, nullable=False)

class ProposalHasParlament(Relationship):
  label = 'proposalHasParlament'

class InstanceHasParlament(Relationship):
  label = 'instanceHasParlament'

class Graph(Neo4jGraph):
  def __init__(self, config=None):
    super(Graph, self).__init__(config)
    # --------------- Nodes-Proxies
    self.people = self.build_proxy(Person)
    self.proposals = self.build_proxy(Proposal)
    self.comments = self.build_proxy(Comment)
    self.parlaments = self.build_proxy(Parlament)
    self.instances = self.build_proxy(Instance) 
    # --------------- Edge-Proxies
    self.issues = self.build_proxy(Issues)               # Edge: (Person -> Proposal)
    self.votes = self.build_proxy(Votes)                 # Edge: (Person -> Proposal)
    self.issuesComment = self.build_proxy(IssuesComment) # Edge: (Person -> Comment)
    self.hasComment = self.build_proxy(HasComment)       # Edge: (Proposal -> Comment)
    self.hasPeople = self.build_proxy(HasPeople)         # Edge: (Instance -> Person)
    self.hasProposal = self.build_proxy(HasProposal)     # Edge: (Instance -> Proposal)
    self.proposalHasParlament = self.build_proxy(ProposalHasParlament) # Edge: (Proposal -> Parlament)
    self.instanceHasParlament = self.build_proxy(InstanceHasParlament) # Edge: (Instance -> Parlament)



