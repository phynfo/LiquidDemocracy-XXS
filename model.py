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

class Issued(Relationship):
  label = 'issued'
  created = DateTime(default=current_datetime, nullable=False)

class Votes(Relationship):
  label = 'votes'
  pro = Integer(nullable=False)                  # -1: against , 1: pro , 0 : not voted
  cv = Integer(default=1, nullable=False)        # votecount
  delegated = Integer(default=0, nullable=False) # 0: not delegated , 1: delegated
  created = DateTime(default=current_datetime, nullable=False)

class Proposal(Node):
  element_type = 'proposal'
  title = String(nullable=False)
  body = String(nullable=False)
  ups = Integer()                # Redundant storage of upvotes
  downs = Integer()              # Redundant storage of downvotes
  datetime_created = DateTime(default=current_datetime, nullable=False)
  datetime_modification = DateTime(default=current_datetime)

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
  ups = Integer()                 # Redundant storage of upvotes
  downs = Integer()               # Redundant storage of downvotes
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

# ----------------------------------------------------------------------------
# -- Modeling the 3 basic cases of delegation; they model the users's view.
# -- 1. Delegation of a Person for everything        (DelegationPerson)
# -- 2. Delegation of a Person for a Parlament       (DelegationParlament with Delegation Hyperedge)
# -- 3. Delegation of a Person for a single Proposal (DelegationProposal with Delegation Hyperedge)
#       
#      |------| PersonDelegation  |----------|  DelegationPerson |------|
# 1.    Person ------------------> Delegation ------------------> Person
#      |------|                   |----------|                   |------|
#
#
#      |------| PersonDelegation  |----------|  DelegationPerson |------|
# 2.   |Person|------------------>|Delegation|------------------>|Person|
#      |------|                   |----------|                   |------|
#                                      |
#                                      |    DelegationParlament  |---------|
#                                      |------------------------>|Parlament|
#                                                                |---------|
#
#
#      |------| PersonDelegation  |----------|  DelegationPerson |------|
# 3.   |Person|------------------>|Delegation|------------------>|Person|
#      |------|                   |----------|                   |------|
#                                      |
#                                      |    DelegationProposal   |---------|
#                                      |------------------------>|Proposal |
#                                                                |---------|
# --------------------------
# Each of the 3 Basic Cases is projected to one or more proposal-specific delegation objects DelProp.
#
#      |------| PersonDelegationProp  |----------|  DelegationPropPerson |------|
#      |Person|---------------------->|  DelProp |---------------------->|Person|
#      |------|                       |----------|                       |------|
#                                          |
#                                          |    DelegationPropProposal   |---------|
#                                          |---------------------------->|Proposal |
#                                                                        |---------|
#   

#-- Users View
class Delegation(Node):
  element_type = "delegation"
  time = Integer() # 0: including past; 
                   # 1: excluding past; up from now on.
  datetime_created=DateTime(default=current_datetime, nullable=False)

class PersonDelegation(Relationship):  
  label = "personDelegation"

class DelegationParlament(Relationship):# (Delegation -> Parlament)
  label = "delegationParlament"

class DelegationProposal(Relationship): # (Delegation -> Proposal)
  label = "delegationProposal"

class DelegationPerson(Relationship):   # (Delegation -> Person)
  label = "delegationPerson"

#-- Proposal-Specific

class DelProp(Node): 
  element_type = "delProp"
  datetime_created=DateTime(default=current_datetime, nullable=False)
 
class OlderDel(Relationship):   # (DelProp -> DelProp)
  label = "olderDel"
 
class PersonDelegationProp(Relationship):   # (Person -> DelProp)
  label = "personDelegationProp"

class DelegationPropProposal(Relationship): # (DelProp -> Proposal)
  label = "delegationPropProposal"

class DelegationPropPerson(Relationship):   # (DelProp -> Person)
  label = "delegationPropPerson"


#-------------------------------------------------------------------------------------------------

class Graph(Neo4jGraph):
  def __init__(self, config=None):
    super(Graph, self).__init__(config)

    # --------------- Nodes-Proxies --------------------------------------------------------------
    self.people      = self.build_proxy(Person)
    self.proposals   = self.build_proxy(Proposal)
    self.comments    = self.build_proxy(Comment)
    self.parlaments  = self.build_proxy(Parlament)
    self.instances   = self.build_proxy(Instance) 
    self.delegations = self.build_proxy(Delegation) # Hyperedge: Delegation
                                                    #   needed for delegations relativ to a parlament / proposal
    self.delProp = self.build_proxy(DelProp)        # Hyperedge: Proposal-specific Delegation

    # --------------- Edge-Proxies  --------------------------------------------------------------
    self.issued = self.build_proxy(Issued)                     # Edge: (Person -> Proposal)
    self.votes = self.build_proxy(Votes)                       # Edge: (Person -> Proposal/Comment)
    self.issuesComment = self.build_proxy(IssuesComment)       # Edge: (Person -> Comment)
    self.hasComment = self.build_proxy(HasComment)             # Edge: (Proposal -> Comment)
    self.hasPeople = self.build_proxy(HasPeople)               # Edge: (Instance -> Person)
    self.hasProposal = self.build_proxy(HasProposal)           # Edge: (Instance -> Proposal)
    self.proposalHasParlament = \
                        self.build_proxy(ProposalHasParlament) # Edge: (Proposal -> Parlament)
    self.instanceHasParlament = \
                        self.build_proxy(InstanceHasParlament) # Edge: (Instance -> Parlament)
    #self.delegates = self.build_proxy(Delegates)              
    self.personDelegation = self.build_proxy(PersonDelegation) # Edge: (Person -> Delegation)
                                                               #       (Person -> Person)
    self.delegationParlament = \
                       self.build_proxy(DelegationParlament)   # Edge: (Delegation -> Parlament)
    self.delegationProposal =  \
                       self.build_proxy(DelegationProposal)    # Edge: (Delegation -> Proposal)
    self.delegationPerson = self.build_proxy(DelegationPerson) # Edge: (Delegation -> Person)
    # -------------
    self.personDelegationProp = self.build_proxy(PersonDelegationProp)     # Edge: (Person -> DelProp)
    self.delegationPropProposal = self.build_proxy(DelegationPropProposal) # Edge: (DelProp -> Proposal)
    self.delegationPropPerson = self.build_proxy(DelegationPropPerson)     # Edge: (DelProp -> Person)   
    self.olderDel = self.build_proxy(OlderDel)                             # Edge: (Delprop -> DelProp)


