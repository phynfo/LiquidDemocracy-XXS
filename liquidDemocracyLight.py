from flask import Flask, session, render_template, request, redirect, url_for, escape, flash, g, abort, jsonify
from model import Graph
from datetime import datetime
from utils import date_diff
from itertools import groupby
import re


# configuration
DATABASE = 'graphdatabase'
DEBUG = True
SECRET_KEY = 'blubber'
USERNAME = 'tobias'
PASSWORD = 'bla'
ADMIN = 'admin'

app = Flask(__name__)
app.config.from_object(__name__)

db = Graph()

@app.template_filter('parlamentTitle')
def parlamentTitle(eid): 
  return db.parlaments.get(eid).title

@app.template_filter('p_cTitle')
def p_cTitle(eid): 
  return db.vertices.get(eid).title


@app.template_filter('utc2str')
def utc2str(utc): 
  return date_diff(datetime.utcfromtimestamp(utc),datetime.today())

@app.template_filter('personUsername')
def personUsername(eid): 
  return db.people.get(eid).username

@app.template_filter('getParlaments')
def getParlaments(eid): 
  v = db.vertices.get(eid)
  if v.element_type == 'instance':
    ps = [p for p in v.outV('instanceHasParlament')]
  elif v.element_type == 'proposal':
    ps = [p for p in v.outV('proposalHasParlament')]
  #insert eid in dicts 
  ds = []
  for p in ps: 
    d = p.data() 
    d['eid'] = p.eid
    ds.append(d)
  return ds

@app.template_filter('getPeople')
def getPeople(eid):
  ''' returns all people of the Instance eid '''
  q =  '''START i=node({i_eid}) 
          MATCH i-[:hasPeople]->p 
          RETURN ID(p), p.username
       '''
  people = db.cypher.table(q,dict(i_eid=eid))[1] # Fetch the people from neo4j ...
  peopleDict = [dict(p_eid = p[0], 
                     username = p[1])
                          for p in people]
  return peopleDict 

@app.template_filter('getProposals')
def getProposals(eid): 
  ''' returns all proposals of the Instance eid'''
  q = '''START i=node({i_eid})
         MATCH i-[:hasProposal]->pr
         RETURN ID(pr), pr.title
      '''
  proposals = db.cypher.table(q,dict(i_eid=eid))[1] # Fetch the propsals from neo4j ...
  proposalDict = [dict(p_eid = p[0],
                       title = p[1])
                          for p in proposals]
  return proposalDict

@app.template_filter('person2proposals')
def person2proposals(p_eid):
  ''' all proposals of a given person p_eid in a given instance g.i_eid in descending 
      order, i.e. props[1] contains the newest proposal, props[-1] contains the oldest proposal.
  '''
  q = '''START p=node({peid}), inst=node({ieid})
         MATCH p-[i:issued]->pr<-[:hasProposal]-inst
         WHERE pr.element_type="proposal"
         RETURN ID(pr), pr.title, pr.datetime_created ORDER BY pr.datetime_created DESC
      '''
  props = db.cypher.table(q,dict(peid=p_eid, ieid=g.i_eid))[1] # Fetch the proposals from neo4j ...
  propsDict = [dict(created = date_diff(datetime.utcfromtimestamp(p[2]), datetime.today()), 
                    title   = p[1], 
                    p_eid   = p[0])
                          for p in props]                      # ... and create a dict-object ...
  return propsDict                                             # ... and return it.

@app.template_filter('person2comments')
def person2comments(p_eid):
  ''' all comments of a given person p_eid in a given instance g.i_eid in descending 
      order, i.e. comments[1] contains the newest comment, comments[-1] contains the oldest comment.
  '''
  q = '''START p=node({peid}), inst=node({ieid})
         MATCH p-[i:issuesComment]->co<-[:hasComment]-pr<-[:hasProposal]-inst
         WHERE co.element_type="comment"
         RETURN ID(co), co.title, co.datetime_created, ID(pr) ORDER BY co.datetime_created DESC
      '''
  comments = db.cypher.table(q,dict(peid=p_eid, ieid=g.i_eid))[1] # Fetch the comments from neo4j ...
  commentsDict = [dict(created = date_diff(datetime.utcfromtimestamp(c[2]), datetime.today()), 
                       title   = c[1], 
                       c_eid   = c[0],
                       p_eid   = c[3])
                          for c in comments]                      # ... and create a dict-object ...
  return commentsDict                                             # ... and return it.
 

@app.template_filter('person2votesProposals')
def person2votesProposals(p_eid):
  ''' all proposals votings of a given person p_eid in a given instance g.i_eid in temporal descending 
      order, i.e. propVotes[0] contains the latest vote, propVotes[-1] contains the oldest vote.
  '''
  q = '''START p=node({peid}), inst=node({ieid})
         MATCH p-[v:votes]->pr<-[:hasProposal]-inst
         WHERE pr.element_type="proposal"
         RETURN v.created, v.pro, pr.title, ID(pr) ORDER BY v.created DESC '''
  propVotes     = db.cypher.table(q,dict(peid=p_eid, ieid=g.i_eid))[1] # Fetch the votes from neo4j ...
  propVotesDict = [dict(created = date_diff(datetime.utcfromtimestamp(p[0]), datetime.today()), 
                        pro     = p[1], 
                        title   = p[2], 
                        p_eid   = p[3]) 
                             for p in propVotes]                       # ... and create a dict-object ...
  return propVotesDict                                                 # ... and return it.


@app.template_filter('person2votesComments')
def person2votesComments(p_eid):
  ''' all comments votings of a given person p_eid in a given instance g.i_eid in temporal descending 
      order, i.e. coVotes[0] contains the latest vote, copVotes[-1] contains the oldest vote.
  '''
  q = '''START p=node({peid}), inst=node({ieid})
         MATCH p-[v:votes]->co<-[:hasComment]-pr<-[:hasProposal]-inst
         WHERE co.element_type="comment"
         RETURN v.created, v.pro, co.title, ID(co), ID(pr) ORDER BY v.created DESC '''
  coVotes     = db.cypher.table(q,dict(peid=p_eid, ieid=g.i_eid))[1] # Fetch the votes from neo4j ...
  coVotesDict = [dict(created = date_diff(datetime.utcfromtimestamp(c[0]), datetime.today()), 
                        pro     = c[1], 
                        title   = c[2], 
                        c_eid   = c[3],
                        p_eid   = c[4])
                             for c in coVotes]                       # ... and create a dict-object ...
  return coVotesDict                                                 # ... and return it.

@app.template_filter('iconize')
def compact(s): 
  ''' return the first few words of the text s in order to produce 
      a short description of an entry's or comment's text '''
  if len(s)<=200:  return s
  s=s[:200]
  s2 = filter(lambda c: c!='\n', s)
  m = re.match(r".*\s", s2) 
  return s2 if not m else s2[:m.end()] + ' ... '

@app.template_filter('iconizePlus')
def verycompact(s): 
  ''' return the first few words of the text s in order to produce 
      a short description of an entry's or comment's text '''
  if len(s)<=200:  return s
  s=s[:50]
  s2 = filter(lambda c: c!='\n', s)
  m = re.match(r".*\s", s2) 
  return s2 if not m else s2[:m.end()] + ' ... '


@app.template_filter('i_eid2title')
def eid2title(i_eid):
  instance = db.instances.get(i_eid)
  return instance.title

@app.url_defaults
def add_i_eid(endpoint, values):
  if 'i_eid' in values or not g.i_eid:
    return
  if app.url_map.is_endpoint_expecting(endpoint, 'i_eid'):
    values['i_eid'] = g.i_eid

@app.url_value_preprocessor
def pull_i_eid(endpoint, values):
  if values: 
    g.i_eid = values.pop('i_eid', None)
  else:
    g.i_eid = None

def data(p): 
   d = p.data()
   d['eid'] = p.eid
   return d

def issuer(eid): 
  ''' Returns the User(s) which issued the Proposal with eid "eId" '''
  if db.vertices.get(eid).element_type=='proposal': 
    return [e.outV() for e in db.vertices.get(eid).inE('issued') ]
  elif db.vertices.get(eid).element_type=='comment':
    return [e.outV() for e in db.vertices.get(eid).inE('issuesComment')]

def countVotes(propId):
  ''' Calculates the votes count '''
  return countVotesUp(propId) - countVotesDown(propId)

def countVotesDown(eid):
  ''' Calculates the votes "down" '''
  v = db.vertices.get(eid)
  return sum([ -1 for voteRel in v.inE('votes') if voteRel.pro==-1])

def countVotesUp(eid):
  ''' Calculates the votes "up" '''
  v = db.vertices.get(eid)
  return sum([1 for voteRel in v.inE('votes') if voteRel.pro==1])

def proposalsByVotes(i_eid):
  ''' Sorts proposals of a specific instance by vote-count '''
  instance = db.instances.get(i_eid)
  proposals = instance.outV('hasProposal')
  return sorted(proposals, key=lambda p:len(list(p.inE('votes'))), reverse=True)

def commentsByVotes(prop_id):
  ''' Sorts proposals by vote-count '''
  comments = db.comments.get(prop_id).outV('hasComment') 
  return sorted(comments, key=lambda c:len(list(c.inE('votesComment'))), reverse=True)

def v2Dict(eid, loggedUserEid=None):
  ''' v = proposal OR comment 
      The resulting dict-Object d collects 
        - the person which issued the proposal/comment, 
        - the vote-counts
        - the creation date ''' 
  v = db.vertices.get(eid)
  d = dict(title = v.title, body=v.body, eid=eid, ups=v.ups, downs=v.downs)
  users = issuer(eid)
  d['username'] = users[0].username if users else None
  d['userid'] = users[0].eid if users else None
  d['voteCountUp'] = countVotesUp(eid)
  d['voteCountDown'] = countVotesDown(eid)
  d['created'] = date_diff(v.datetime_created, datetime.today())
  if loggedUserEid: 
    loggedUser = db.people.get(loggedUserEid)
    votes = [voteEdge for voteEdge in loggedUser.outE('votes') if voteEdge.inV() == v]
    if votes:
      d['upvoted']   = (votes[0].pro == 1)
      d['downvoted'] = (votes[0].pro == -1)
  return d

def i2Dict(i_eid, loggedUserEid=None): 
  ''' i_eid = instance 
      Collects information about an instance: 
        title, body, created, numberUsers, numberVotes, numberProposals, numberComments'''
  instance = db.instances.get(i_eid)
  d = dict(title=instance.title, body=instance.body, eid=i_eid)
  d['created']     = date_diff(instance.datetime_created, datetime.today())
  d['numberUsers'] = len(list(instance.outV('hasPeople')))
  proposals = list(instance.outV('hasProposal'))
  d['numberProposals'] = len(proposals)
  d['numberVotes'] = sum([len(list(p.inE('votes'))) for p in proposals])
  d['numberComments'] = sum([len(list(p.outE('hasComment'))) for p in proposals])
  # Alternatively, the following Cypher-Query could be used: 
  # q = '''START i=node({i_eid}) 
  #   MATCH i-[:hasProposal]->p-[:hasComment]->c
  #   RETURN count(c)'''
  # d['numberComments'] = db.cypher.table(q,dict(i_eid=i_eid))[1][0][0] 
  return d

def person2Dict(person): 
  p = person.data()
  p['eid'] = person.eid
  return p

#-------------------- The view functions ----------------------------------------
#   * Instances
#     - show_instances, add_instance
#   * Proposals 
#     - show_proposal , show_single_proposal, add_proposal, delete_proposal
#   * Comments
#     - add_comment
#   * Votes
#     - vote
#   * People
#     - login, logout, signin, login_instance
#     - show_person, show_people
# -------------------------------------------------------------------------------

@app.route('/')
def show_instances():
  user = db.people.get(session['userId']) if session.get('logged_in') else None
  if user and not session['isAdmin']: 
     instances = [i2Dict(i.eid, user) for i in db.instances.get_all() if user in i.outV('hasPeople')]
  else: 
     instances = [i2Dict(i.eid) for i in db.instances.get_all()]
  return render_template('show_instances.html', instances=instances)

@app.route('/addinstance', methods=['POST'])
def add_instance(): 
  if not (session.get('logged_in') and session['isAdmin']): 
    abort(401)  
  instance = db.instances.create(title=request.form['title'], body=request.form['body'])
  flash('Neue Instanz haette angelegt werden muessen') 
  return redirect(url_for('show_instances'))

@app.route('/<int:i_eid>/proposals')
def show_proposals(): 
  proposals = []
  userEid = db.people.get(session['userId']).eid if session.get('logged_in') else None
  instance = db.instances.get(g.i_eid)
  # i = dict(title=instance.title, eid=g.i_eid)
  for proposal in proposalsByVotes(g.i_eid):
    p = v2Dict(proposal.eid, loggedUserEid=userEid)
    proposals.append(p)
  return render_template('show_proposals.html', entries=proposals)

@app.route('/<int:i_eid>/proposal/<int:prop_id>')
def show_single_proposal(prop_id):
   userEid = db.people.get(session['userId']).eid if session.get('logged_in') else None
   proposal = v2Dict(prop_id, loggedUserEid=userEid)
   comments = []
   for comment in commentsByVotes(prop_id):
     c = v2Dict(comment.eid, loggedUserEid=userEid)
     comments.append(c)
   return render_template('show_single_proposal.html', proposal=proposal, comments=comments)

@app.route('/<int:i_eid>/addproposal',methods=['POST'])
def add_proposal():
  if not session.get('logged_in'):
    abort(401)
  prop = db.proposals.create(title=request.form['title'], body=request.form['body'], ups=0, downs=0)
  if 'parlament' in request.form: 
    p = list(db.parlaments.index.lookup(title=request.form['parlament']))
    if p: 
      db.proposalHasParlament.create(prop,p[0])
  instance = db.instances.get(g.i_eid)
  user = db.people.get(session['userId'])
  db.issued.create(user,prop)           # Edge1: User issues Proposal
  db.hasProposal.create(instance, prop) # Edge2: Proposal belongs to current Instance
  flash('Neuer Eintrag erfolgreich erstellt')
  return redirect(url_for('show_proposals'))

@app.route('/<int:i_eid>/deleteproposal/<int:prop_id>')
def delete_proposal(prop_id):
  if not session.get('logged_in'):
    abort(401)
  proposal = db.proposals.get(prop_id)
  for e in proposal.inE('hasProposal'): 
    db.hasProposal.delete(e.eid) 
  resp = db.proposals.delete(prop_id)
  flash('Eintrag geloescht')
  return redirect(url_for('show_proposals'))

@app.route('/<int:i_eid>/addcomment/<int:prop_id>',methods=['POST'])
def add_comment(prop_id):
  if not session.get('logged_in'):
    abort(401)
  comment = db.comments.create(title=request.form['title'], body=request.form['body']) 
  user = db.people.get(session['userId'])
  db.issuesComment.create(user,comment) 
  db.hasComment.create(db.proposals.get(prop_id), comment)
  flash('Neuer Kommentar erfolgreich erstellt')
  return redirect(url_for('show_single_proposal', prop_id=prop_id))

@app.route('/<int:i_eid>/vote/<int:pro>/<int:eid>')
def vote(pro, eid):
  if pro==0: pro=-1
  if not session.get('logged_in'):
    abort(401)
  loggedUser = db.people.get(session['userId'])
  c_p = db.vertices.get(eid)             # c_p is a comment or a proposal
  voteRels = [rel for rel in loggedUser.outE('votes') if rel.inV() == c_p]
  if voteRels and voteRels[0].pro != 0 and voteRels[0].pro!=pro:  # i.e.: user undoes vote => delete Vote
      if pro==1:  
        c_p.downs-= 1 ; c_p.save() 
      else: 
        c_p.ups-= 1 ; c_p.save() 
      voteRels[0].pro = 0 ; voteRels[0].save()
      # db.votes.delete(voteRels[0].eid) # Alternative: einfach die Kante loeschen.
      flash('Stimme rueckgaengig gemacht')
  elif not voteRels or voteRels[0].pro==0:       # No "votes"-edge exists => create new "votes"-Edge
      if not voteRels: 
        db.votes.create(loggedUser,c_p, pro=pro)
      else: 
        voteRels[0].pro=pro
        voteRels[0].save()
      if pro==1: 
        flash('Erfolgreich dafuer gestimmt') 
        c_p.ups += 1 ; c_p.save() 
      elif pro==-1:   
        flash('Erfolgreich dagegen gestimmt')
        c_p.downs += 1 ; c_p.save() 
  else: # if voteRels and voteRels[0].pro==pro:  , i.e.: Voting up/down a second time is not allowed.
      abort(401)
 
  if c_p.element_type == 'comment':
    proposal = c_p.inV('hasComment').next()
    return redirect(url_for('show_single_proposal', prop_id=proposal.eid))
  return redirect(url_for('show_proposals'))

@app.route('/<int:i_eid>/login',methods=['POST','GET'])
def login_instance(): 
  error = None
  if request.method == 'POST':
    username = request.form['username'] ; password = request.form['password']
    instance = db.instances.get(g.i_eid)
    users = [u for u in db.people.index.lookup(username=username) if u in instance.outV('hasPeople')]
    if users and users[0].password==password: 
      session['logged_in'] = True
      session['userId'] = users[0].eid ; session['username'] = users[0].username 
      session['isAdmin'] = users[0].username==app.config['USERNAME']
      s = "Du hast Dich in Instanz %s eingeloggt" % instance.title
      flash(s) 
      return redirect(url_for('show_proposals'))
    elif not users:
      error = 'Ungueltiger Benutzername'
    else:
      error = 'Ungueltiges Passwort'
  return render_template('login.html', instances=None, error=error)

@app.route('/login', methods=['POST','GET'])
def login(): 
    error = None 
    if request.method == 'POST':
      username = request.form['username'] ; password = request.form['password'] ; instancetitle = request.form['instancetitle']
      instance = db.instances.index.lookup(title=instancetitle).next()
      users = [u for u in db.people.index.lookup(username=username) if u in instance.outV('hasPeople')] 
      if users and users[0].password==password: 
        session['logged_in'] = True
        session['userId'] = users[0].eid ; session['username'] = users[0].username
        session['isAdmin'] = users[0].username==app.config['USERNAME']
        s = "Du hast Dich in Instanz %s eingeloggt" % instancetitle
        flash(s) 
        return redirect(url_for('show_proposals', i_eid=instance.eid))
      elif not users:
        error = 'Ungueltiger Benutzername fuer Instanz %s' % instancetitle
      else:
        error = 'Ungueltiges Passwort'
    return render_template('login.html', i_eid=None, instances = [dict(title=i.title) for i in db.instances.get_all()], error=error)
  
@app.route('/<int:i_eid>/logout')
def logout():
  ''' Deletes the cookies and redirects to show_instances'''
  session.pop('logged_in', None)
  session.pop('userId',None)
  session.pop('username',None)
  session.pop('isAdmin',None)
  flash('Du hast Dich ausgeloggt')
  return redirect(url_for('show_instances'))

@app.route('/<int:i_eid>/signin', methods=['POST', 'GET'])
def signin():  
  ''' There are two cases: 
      1. A new user is created in the current instance
      2. An existing user is associated with the current instance '''
  error = None
  if request.method == 'POST':
    if 'username' in request.form:  
      username = request.form['username'] ; pass1 = request.form['password1'] ; pass2 = request.form['password2']
      email = request.form['email'] ; vorname = request.form['vorname'] ; nachname = request.form['nachname']
      users = [p for p in db.people.index.lookup(username=username)] 
      if users: #Benutzername schon vorhanden?
        error = 'Benutzername existiert schon'
      elif pass1!=pass2: 
        error = 'Passwort nochmals eingeben!'
      elif not (email and vorname and nachname and username): 
        error = 'Eingabedaten unvollstaendig!'
      else: 
        instance = db.instances.get(g.i_eid)
        user = db.people.create(firstname=vorname, secondname=nachname, username=username, password=pass1, email=email)
        db.hasPeople.create(instance, user)
        flash('Benutzer erfolgreich angelegt')
        return redirect(url_for('login_instance'))
    if 'username1' in request.form: 
      username = request.form['username1'] 
      passw = request.form['password']
      # does username alread exist?
      users = list(db.people.index.lookup(username=username))  
      if not users: 
        flash('Der angegebene Benutzername existiert aber noch nicht')
        return redirect(url_for('signin'))
      else: 
        user = users[0]
        if user.password != passw: 
            flash('Password war falsch')
            return redirect(url_for('signin'))
        else: 
            instance = db.instances.get(g.i_eid)
            db.hasPeople.create(instance, user)
            flash('Benutzer erfolgreich zur Instanz hinzugefgt')
            return redirect(url_for('login_instance'))
  return render_template('signin.html', error=error)

@app.route('/<int:i_eid>/logoutLogin/<int:p_eid>')
def logoutLogin(p_eid):
  ''' Wird ein User geklickt, so wird automatisch versucht, den aktuellen Benutzer auszuloggen und 
      mit dem neuen Benutzer einzuloggen '''
  if session.get('logged_in'): 
    flash('Du hast Dich ausgeloggt') 
    session.pop('logged_in', None)
    session.pop('userId',None)
    session.pop('username',None)
    session.pop('isAdmin',None)
  session['userId']=p_eid
  session['username']=db.people.get(p_eid).username
  return redirect(url_for('login_instance'))

@app.route('/<int:i_eid>/person/<int:p_eid>')
def show_person(p_eid):
  if not session.get('logged_in'):
        abort(401)
  person = db.people.get(p_eid)
  return render_template('show_person.html', person=dict(p_eid=p_eid, firstname=person.firstname,\
                                                         secondname=person.secondname,\
                                                         username=person.username, email=person.email))

@app.route('/<int:i_eid>/persons')
def show_people():
  instance = db.instances.get(g.i_eid)
  people = [person2Dict(p) for p in instance.outV('hasPeople')] 
  return render_template('show_people.html', people = people, 
                                             instance = dict(title=instance.title,\
                                                             eid=instance.eid))

@app.route('/<int:i_eid>/parlaments')
def show_parlaments(): 
  q_pa = '''START i=node({i_eid})
            MATCH i-[:instanceHasParlament]->pa
            RETURN pa'''
  pa = db.cypher.query(q_pa, dict(i_eid=g.i_eid))
  parlaments = [data(p) for p in pa]
  q_numProp = '''START pa=node({pa_eid})
                 MATCH pa<-[:proposalHasParlament]-pr
                 RETURN COUNT(pr)'''
  for p in parlaments: 
    erg = db.cypher.table(q_numProp, dict(pa_eid=p['eid']))[1]
    p['numberProposals'] = 0 if not erg else erg[0][0]
  return render_template('show_parlaments.html', parlaments=parlaments)

@app.route('/<int:i_eid>/addparlament', methods=['POST'])
def add_parlament(): 
  if not (session.get('logged_in') and session['isAdmin']): 
    abort(401)
  q = '''START i=node({i_eid}) 
         MATCH i-[:instanceHasParlament]->pa
         WHERE pa.title = {title}
         RETURN pa'''
  pa = list(db.cypher.query(q, dict(i_eid=g.i_eid, title=request.form['title'])))
  if pa: 
    flash('Parlament wurde nicht angelegt! Es existiert schon in dieser Instanz')
  else:  
    instance = db.instances.get(g.i_eid)
    parlament = db.parlaments.create(title=request.form['title'], body=request.form['body'])
    db.instanceHasParlament.create(instance, parlament) 
    flash('Neues Parlament wurde angelegt') 
  return redirect(url_for('show_parlaments'))


## ------------- Delegations ----------------------------------------------------------

@app.route('/<int:i_eid>/delete_delegation/<int:d_eid>')
def delete_delegation(d_eid):
  ''' Deletes delegation-objekct d_eid together with all edges connected with it'''
  query = '''START d=node({d_eid})
             MATCH d-[r]-()
             DELETE d,r 
          '''
  t = db.cypher.execute(query, dict(d_eid=d_eid))
  flash('Delegation '+str(d_eid)+' geloescht.')
  return redirect(url_for('show_delegations', pers_eid=session['userId']))

@app.route('/<int:i_eid>/show_delegations/<int:pers_eid>')
def show_delegations(pers_eid):
  dels = personDelegations(pers_eid)
  # format: dels :: [ (Timestamp, dict{type : eid}) ]  
  return render_template('show_delegations.html', pers_eid=pers_eid, dels=dels)

@app.route('/<int:i_eid>/delegate_parlament/<int:parl_eid>')
def delegateParlament(parl_eid): 
  parlament = db.parlaments.get(parl_eid)
  return render_template('delegate.html', parlament=parl_eid)

@app.route('/<int:i_eid>/delegate_proposal/<int:pr_eid>')
def delegateProposal(pr_eid): 
  return render_template('delegate.html', proposal=pr_eid)

@app.route('/<int:i_eid>/delegate_person/<int:p_eid>')
def delegatePerson(p_eid): 
  return render_template('delegate.html', person=p_eid)

@app.route('/<int:i_eid>/delegate',methods=['POST'])
def delegate(): 
  ''' Create delegation edges and vertices
      There are three cases:
      1. Delegation of a person for all proposals
      2. Delegation of a person for all proposals of a specific parlament
      3. Delegation of a person for a single proposal
  '''
  personWhoDelegatesEid = session['userId']
  personWhoDelegates = db.people.get(session['userId'])
  person = request.form['person'] if 'person' in request.form else None
  proposal = request.form['proposal'] if 'proposal' in request.form else None
  parlament = request.form['parlament'] if 'parlament' in request.form else None
  span = request.form['span'] # span is one of 'parlament' / 'proposal' / 'all'
  time = 0 if request.form['time']=='past' else 1 # time is one of 'past' / 'now'
 
  if not person: 
    flash('Error: You have to specify a person (i.e. the delegate)')
    if parlament and span=='parlament': return render_template('delegate.html', parlament = parlament )
    elif proposal: return render_template('delegate.html', proposal = proposal)
    else: return render_teplate('delegate.html')


  # Create edges: 
  delegation = db.delegations.create(time=time)
  personDelegationEdge = db.personDelegation.create(personWhoDelegates, delegation)
  delegationPersonEdge = db.delegationPerson.create(delegation, db.people.get(person))
  delDict = {}
  if span=='parlament': # create edge from delegation object to parlament
    delegationParlamentEdge = db.delegationParlament.create(delegation, db.parlaments.get(parlament))
    delDict['parlament'] = parlament
  elif span=='proposal': # create edge from delegaton object to proposal
    delegationProposalEdge = db.delegationProposal.create(delegation, db.proposals.get(proposal))
    delDict['proposal'] = proposal
  # else: pass  # here span=='all' should hold: no additonal edges!

  propDels = getPropDelTriples(personWhoDelegatesEid, delegationDict)
  createPropDels(propDels)

  # Create feedback
  personStr = db.people.get(person).username if person else ''
  proposalStr = db.proposals.get(proposal).title if proposal and span=='proposal' else ''
  parlamentStr = db.parlaments.get(parlament).title if parlament and span=='parlament' else ''
  flashstr = 'Delegation erfolgreich erstellt: Delegiere "' + personStr + '" fuer ' + span + ' "' +\
               proposalStr+parlamentStr + '" fuer ' + request.form['time']
  flash(flashstr)
  return redirect(url_for('show_proposals')) 


def getPropDelTriples(pers_eid, delDict): 
  ''' Projects a Delegation-Object (in the form of a dict) to a list of triples of the form
      [(personFrom, personTo, proposal), ...]. Each triple describes one specific proposal-specific
      delegation
  '''
  if 'proposal' in delDict:  
        props = [delDict['proposal']]
  elif 'parlament' in delDict:  # fetch all proposals of parlament
        query = ''' START parl=node({parl_eid})
                    MATCH parl<-[:proposalHasParlament]-prop
                    RETURN COLLECT(ID(prop))'''
        props = db.cypher.table(query, dict(parl_eid=delDict['parlament']))[1][0][0]
  else: # all -- fetch all proposals of current instance
        query = ''' START p=node({pers_eid})
                    MATCH p<-[:hasPeople]-i-[:hasProposal]->prop
                    RETURN COLLECT(ID(prop))  '''
        props = db.cypher.table(query, dict(pers_eid=pers_eid))[1][0][0]
  return [(pers_eid, delDict['person'], pr) for pr in props]


def deletePropDels(propDelTriples): 
  ''' deletes PropDels; there are two cases: 
      1. if the specified delegation is an active delegation, then it's deleted (1.3), all transitively
         affected votes are adapted (1.2) and the next older delegation -- if existing -- is restored 
         (via the 'olderDel'-Edge) (1.1), and all transitively affected votes are adapted (1.4.).
      2. if the specified delegation is not active, then -- not implemented yet -- '''
  for pFrom, pTo, pr in propDelTriples: 
        pFromObj   = db.people.get(pFrom)
        pToObj     = db.people.get(pTo)
        proposal   = db.proposals.get(pr) # the delegated proposal...
        vote       = fetchVoteObject(pFromObj, proposal) # the original vote of the delegater
        vote.delegated = 0 ; vote.save() # set delegated-Flag to False
        
        # get the corresponding delProp and all transitively affected delPops: 
        delProps = transitiveDelProps(pFrom, pr) 

        if delProps and delProps[0][0].eid==pTo: # 1. The specifiied delegation (pFrom delegates pTo for pr) is active.
                delProp = delProps[0][2] 
                if DEBUG: 
                        print "D0: delProp.eid = %d, delProp = %s" % (delProp.eid, str(delProp))
                
                # 1.1. fetch older delProps, if there are any.
                #      ... if there are no older delProps, then olderDelProps == []
                olderDelEdges = list(delProp.outE('olderDel'))
                olderDelProps = list(delProp.outV('olderDel')) 
                if DEBUG: 
                  print "D1: olderDelEdges: %s, olderDelProps: %s" % (str(olderDelEdges), str(olderDelProps))
                if len(olderDelProps)>1: 
                  print "D: ERROR! -- olderDel > 1"
                  return

                # 1.2. transitively adapt all vote.vc-values ...
                for p2Obj, voteT, dp in delProps: 
                        voteT.cv = voteT.cv - vote.cv
                        if DEBUG: 
                                print "D2. delProp = (%d, %d, %d), voteT.cv = voteT.cv - %d" % (p2Obj.eid, voteT.eid, dp.eid , vote.cv)
                                print "    voteT.eid = %d, voteT.cv = %d,  vote.eid = %d" % (voteT.eid, voteT.cv, vote.eid)
                        voteT.save()

                # 1.3. ... and delete the DelProp and all affected edges.
                db.delProp.delete(delProp.eid) 

                if olderDelProps: # 1.4 Restore older delProp-Object
                        olderDelProp = olderDelProps[0] ; olderDelEdge = olderDelEdges[0]
                        if DEBUG: 
                                print "D3: olderDelProp = %s, olderDelPropEdge = %s" % (str(olderDelProp), str(olderDelEdge))
                        pdp = db.personDelegationProp.create(pFromObj, olderDelProp)   # Person -> DelProp
                        dpp = db.delegationPropProposal.create(olderDelProp, proposal) # DelProp -> Proposal
                                                                                       # DelProp -> Person exists...
                        # delete the olderDel-Edge... 
                        # db.olderDel.delete(olderDelEdge.eid) --> has it already been deleted in 3. ?
                        for p2Obj, voteT, delPropObj in transitiveDelProps(pFrom, pr): 
                                voteT.cv = voteT.cv + vote.cv
                                if DEBUG: 
                                        print "D4. delProp = (%d, %d, %d), voteT.cv = voteT.cv + %d" % (p2Obj.eid, voteT.eid, delPropObj.eid , vote.cv)
                                        print "    voteT.eid = %d, voteT.cv = %d,  vote.eid = %d" % (voteT.eid, voteT.cv, vote.eid)
                                voteT.save()
        elif delProps:  # the delegation to be deleted is not active 
                        # -> check, if there is an older delegation with this specification.
                        # If yes, delete the older Delegation
                delProp = delProps[0][2]
                olderDels = transitiveOlderDels(delProp.eid)
                from itertools import dropwhile
                # search for a delegaton to pTo
                olderDelIdx = [i for i in range(len(olderDels)) if olderDels[i][1].eid == pTo]
                # ... if there exists such a delegation: 
                if olderDelIdx: 
                        i = olderDelIdx[0]
                        if DEBUG: print 'olderDel, with idx %d and eid %s' % (i, olderDels[i][0].eid) 
                        dpObj = olderDels[i][0] ; pObj = olderDels[i][1]
                        delPropFrom = olderDels[i-1][0] if i>0 else delProp
                        delPropTo   = olderDels[i+1][0] if i<len(olderDels)-1 else None
                        # loesche delProp
                        db.delProp.delete(olderDels[i][0].eid)
                        # reconnect: 
                        if delPropTo: db.olderDel.create(delPropFrom, delPropTo)
                        #TODO: Better DEBUG-Messeges and better testing-functions!  
                        #      Maybe it already works correctly....
 
def transitiveOlderDels(delProp): 
  ''' yields a (possibly empty) list of older Delegations (i.e. the delegation-stack) in the form of a list of
      tuples [(delPropObj, persObj)] '''
  queryNextDelProp = '''START dp=node({dp})
                        MATCH dp-[:olderDel]->dp2-[:delegationPropPerson]->p2
                        RETURN ID(dp2), ID(p2)'''
  props = db.cypher.table(queryNextDelProp, dict(dp=delProp))[1]
  erg = []
  while props: 
        dp = props[0][0] ; p2 = props[0][1]
        dpObj = db.delProp.get(dp) ; p2Obj = db.people.get(p2)
        erg.append((dpObj, p2Obj))
        props = db.cypher.table(queryNextDelProp, dict(dp=dp))[1]
  return erg
        
  


def createPropDels(propDelTriples):
  '''propDelTriples :: [(personFrom, personTo, proposal)] 
     Every tripel in the propDelTriples-List represents one proposal-specific delegation.
     
     The function creates new propDel-Objects and transitively adapts vote.cv-values; 
     The queryNextDelProp(person, proposal) yields the next DelProp on walk through 
     the transitive delegations. 
  '''
  for pFrom, pTo, pr in propDelTriples: 
        # 17, 7, 20
        pFromObj   = db.people.get(pFrom)
        pToObj     = db.people.get(pTo)
        proposal   = db.proposals.get(pr) # the delegated proposal...
        vote       = fetchVoteObject(pFromObj, proposal) # the original vote of the delegater
        vote.delegated = 1 ; vote.save() # set delegated-Flag to True
        # create new Delegation vertice
        delegation = db.delProp.create()
        if DEBUG: print "created delProp with eid: ", delegation.eid
        
        # is there an older delProp for proposal pr?
        delProps = transitiveDelProps(pFrom, pr) 
        if DEBUG: print "1. delProps = ", delProps
         
        if delProps: # if there is an older delegation on this proposal, then ...
                
                # ... persistently link the new one to the older one...
                olderDelegation = delProps[0][2]
                db.olderDel.create(delegation, olderDelegation) 
                for p2Obj, voteT, delPropObj in delProps: # ... Transitively adapt all votes.vc-values ...
                        voteT.cv = voteT.cv - vote.cv
                        if DEBUG: 
                                print "2. delProp = (%d, %d, %d), voteT.cv = voteT.cv - %d" % (p2Obj.eid, voteT.eid, delPropObj.eid , vote.cv)
                                print "   voteT.eid = %d, voteT.cv = %d,  vote.eid = %d" % (voteT.eid, voteT.cv, vote.eid)
                        voteT.save()
                
                # ... at the end: delete both edges from the olderDelegation...
                edge1 = olderDelegation.outE('delegationPropProposal').next().eid 
                db.delegationPropProposal.delete(edge1)
                if DEBUG: print 'deleted: delegationPropProposal with eid %d' % edge1

        # create new delegation edges  ...
        pdp = db.personDelegationProp.create(pFromObj, delegation)    # Person  -> DelProp
        dpp0 = db.delegationPropProposal.create(delegation, proposal) # DelProp -> Proposal
        dpp1 = db.delegationPropPerson.create(delegation, pToObj)     # DelProp -> Person
        if DEBUG: print 'created "personDelegationProp" with eid %d and "delegationPropProposal" with eid %d and "delegationPropPerson" with eid %d' % (pdp.eid, dpp0.eid, dpp1.eid)

        # ... and adapt all transitively delegated votes
        for p2Obj, voteT, _ in transitiveDelProps(pFrom, pr): 
                voteT.cv = voteT.cv + vote.cv
                if DEBUG: 
                        print "4. delProp = (p2Obj: %d, voteT: %d), voteT.cv = voteT.cv + %d" % (p2Obj.eid, voteT.eid, vote.cv)
                        print "   voteT.eid = %d, voteT.cv = %d,  vote.eid = %d" % (voteT.eid, voteT.cv, vote.eid)
                voteT.save()
  return None

def transitiveDelProps(pers_eid, prop_eid): 
  ''' walks through transitive delegation relationships and returns [(persObj, voteObj, delPropObj)]'''
  queryNextDelProp = '''
           START p = node({pFrom}), prop = node({pr})
           MATCH p-[:personDelegationProp]->d-[:delegationPropProposal]->prop, d-[:delegationPropPerson]->p2
           RETURN id(d), id(p2)'''
  delProp = db.cypher.table(queryNextDelProp, dict(pFrom=pers_eid, pr=prop_eid))[1]
  proposal = db.proposals.get(prop_eid)
  erg = []
  while delProp: 
        p2 = delProp[0][1] ; dp = delProp[0][0] ; p2Obj = db.people.get(p2) 
        dpObj = db.delProp.get(dp)
        voteT = fetchVoteObject(p2Obj, proposal)
        erg.append((p2Obj,voteT, dpObj))
        delProp = db.cypher.table(queryNextDelProp, dict(pFrom=p2, pr=prop_eid))[1]
  return erg



def del2Dict(d_eid): 
  ''' transforms a delegation-node to the dictionary-representation '''
  delegation = db.vertices.get(d_eid)
  d = {}
  parl = [v for v in delegation.outV('delegationParlament')] 
  if parl: d['parlament'] = parl[0].eid
  prop = [v for v in delegation.outV('delegationProposal')] 
  if prop: d['proposal'] = prop[0].eid
  pers =  [v for v in delegation.outV('delegationPerson')] 
  if pers: d['person'] = pers[0].eid
  return d 


def fetchVoteObject(persObj, propObj): 
  ''' Either returns existing vote of persObj for propObj or (if such a vote does not yet exist) 
      creates a new vote-object v with v.pro == 0 '''
  voteSingle = [v for v in persObj.outE('votes') if v.inV() == propObj]
  if voteSingle: return voteSingle[0]
  else: # create a voting v with v.prop = 0
     return db.votes.create(persObj,propObj, pro=0)

## ----------------- Implementaiton of Delegations -------------------------------------------------
#
# 1. Person p1 Creates Delegation-Object d via the web-Interface. 
#
# 2. let d = {'person': p2_eid, 'parlament': parl_eid, 'proposal': prop_eid}
#
# 3. Adapt all vote-Relationsships v from p1 to all props of delegation d, i.e. set v.delegated=1
#    if not Vote-Relationsship exists yet, create a new one with v.delegated=1.
#
# 4. For each proposal p of delegation d: 
#    * Generate a propDel-Object


## ------------------ Generate "Delegation-Triples" ------------------------------------------------
# There are (at least) two possiblities to handle multiple delegations p-->d1, p-->d2, p-->d3, ...  
#                                                              (ordered descending by creation time)
#
# (A) Don't allow the creation of multiple overlapping delegations.
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# ... won't be implemented ...
#
# (B) Implement a delegation-"stack"
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   Basic idea: map a person's delegation to a dict containing all affected proposals
#
#   For a concrete Person p, create a delegation-Dict for all delegations of person p_eid, grouped by proposal:
#     {prop1_eid: [(utc1, p1_eid), ...]), ...}
#     The dict's value-lists are ascendingly sorted by creation time utc1
#
#   * Deleting a delegation results in filtering / deleting these Lists.
#
#   * The following invariant has to hold: 
#       p0-[v0:votes]->pr has an additional "i" in v0.delegates, if there is a Person p with eid p_eid and 
#       d = delegationDicts(p_eid) and pr_eid in d and d[pr_eid][-1] = (time, p0_eid)
#       and there is p-[v1:votes]->pr with v1.delegates==i
#   
#   * When Person p adds a delegation p-->d, the delegationDicts(p_eid) before and after are
#     compared; increment v.delegates for the delta-triples.
#
#   * Same with deletion; the triple-List before and after is compared and the v.delegates in the delta are
#     decremented.

def personDelegations(p_eid): 
  ''' Returns a list of all delegations invoked by person p_eid; the information is returned in the following 
      format: 
           [ (Timestamp, dict{type : eid}) ] '''
  query = ''' START p=node({p_eid})
              MATCH p-[:personDelegation]->d-[r]->x
              RETURN d.datetime_created, ID(d), collect(x.element_type), collect(ID(x)) ORDER BY d.datetime_created DESC''' 
#             RETURN d.datetime_created, collect(type(r)), collect(ID(x)) ''' 
  t = db.cypher.table(query, dict(p_eid=p_eid))[1]
  # returns [TimeStamp, dict{type : eid}]
  return map(lambda x: (x[0],x[1], dict(map(lambda a,b: (a,b), x[2],x[3]))), t) 


def parlamentProposals(p_eid, parl_eid, i_eid): 
  ''' All proposals of parlement parl_eid for which person p_eid voted; all in instance i_eid'''
  query = ''' START p=node({p_eid}), parl=node({parl_eid}), i=node({i_eid})
              MATCH p-[v:votes]->pr-[:proposalHasParlament]->parl
              WHERE (i-[:hasProposal]->pr) and not(v.pro = 0)
              RETURN ID(pr)'''
#              RETURN ID(v), ID(pr)'''
  return db.cypher.table(query,dict(p_eid=p_eid, parl_eid=parl_eid, i_eid=i_eid))[1] # Fetch the proposals

def personProposals(p_eid, i_eid): 
  ''' All proposals for which person p_eid voted; all in instance i_eid '''
  query = ''' START p=node({p_eid}), i=node({i_eid})
              MATCH p-[v:votes]->pr
              WHERE (i-[:hasProposal]->pr) and not(v.pro = 0)
              RETURN ID(pr) '''
#             RETURN ID(v), ID(pr) '''
  return db.cypher.table(query,dict(p_eid=p_eid, i_eid=i_eid))[1] # Fetch the proposals


def singleDelegationTuples(p_eid, d): 
  ''' returns the list of all proposals (tupled with the delegated person) for a specific delegation d.
      d has to be provided as a dict-object: 
      d{u'person': eid, u'proposal': eid, u'parlament': eid} of person p_eid'''
  p = db.people.get(p_eid)
  i_eid = p.inV('hasPeople').next().eid # fetch corresponding instance
  p1 = d['person']
  if 'parlament' in d: 
    return [(p1, p) for pp in parlamentProposals(p1, d['parlament'], i_eid) for p in pp] 
  elif 'proposal' in d: 
    return [(p1,d['proposal'])]
  else: #all!
    return [(p1,p) for pp in personProposals(p1,i_eid) for p in pp]    


# Perhaps, all this should be stored in directly in the graph-db???
#     Pro: ... then, all this hasnt to be calculated all over again.
#     Con: Would insert lots of redundant information in the graph db
def delegationDicts(p_eid): 
  ''' returns a dict which associates each prop_eid to a delegation stack [(time, pers_eid)] (with the
      newstest delegation in the tail, i.e. the dict has the following format: 
        {prop1_eid : [(time1, pers1_eid), ...], prop2_eid: [...]} '''
  triples = sorted([(prop,timestamp,p1)
                   for (timestamp, _, d) in personDelegations(p_eid)  # d -- Info about a single delegation of p_eid
                   for (p1,prop) in singleDelegationTuples(p_eid, d)]) # all proposals affected by d
  groupedTriples = [(k, list(v)) for k,v in groupby(triples, lambda x: x[0])] # grouped by proposal-eid
  d={}  # generate dict 
  for prop,dels in groupedTriples: 
    d[prop]=[]
    for _,time,pers in dels: 
      d[prop].append((time,pers))
  return d
         
## -----------------------------------------------------------------------------------------

@app.route('/_add_numbers')
def add_numbers():
  a = request.args.get('a',0,type=int)
  b = request.args.get('b',0,type=int)
  return jsonify(result=a+b)

def initdb():
  users = [p for p in db.people.index.lookup(username=app.config['USERNAME'])]
  if not users: 
    db.people.create(username=app.config['USERNAME'], \
                     firstname=app.config['USERNAME'], \
                     secondname=app.config['USERNAME'], \
                     password=app.config['PASSWORD'], \
                     email='email')

initdb()
if __name__ == '__main__':
  app.run()
