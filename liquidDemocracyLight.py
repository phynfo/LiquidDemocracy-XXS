from flask import Flask, session, render_template, request, redirect, url_for, escape, flash, g
from model import Person, Proposal, Graph
from bulbs.utils import current_datetime
from datetime import datetime
from utils import date_diff
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

@app.template_filter('iconize')
def compact(s): 
  ''' return the first few words of the text s in order to produce 
      a short description of an entry's or comment's text '''
  if len(s)<=200:  return s
  s=s[:200]
  s2 = filter(lambda c: c!='\n', s)
  m = re.match(r".*\s", s2) 
  return s2 if not m else s2[:m.end()] + ' ... '

@app.template_filter('i_eid2title')
def eid2title(i_eid):
  instance = db.instances.get(i_eid)
  return instance.title

#@app.url_defaults
#def add_i_eid(endpoint, values):
#  if 'i_eid' in values or not g.i_eid:
#    return
#  if app.url_map.is_endpoint_expecting(endpoint, 'i_eid'):
#    values['i_eid'] = g.i_eid

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

def issuer(eid): 
  ''' Returns the User(s) which issued the Proposal with eid "propId" '''
  return [e.outV() for e in db.vertices.get(eid).inE('issued') ]

def countVotes(propId):
  ''' Calculates the votes count '''
  return countVotesUp(propId) - countVotesDown(propId)

def countVotesDown(eid):
  ''' Calculates the votes "down" '''
  v = db.vertices.get(eid)
  return sum([ -1 for voteRel in v.inE('votes') if voteRel.pro==0])

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
  ''' v = proposal OR comment ''' 
  v = db.vertices.get(eid)
  d = dict(title = v.title, body=v.body, eid=eid)
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
      d['downvoted'] = (votes[0].pro == 0)
  return d

def i2Dict(i_eid, loggedUserEid=None): 
  ''' i_eid = instance '''
  instance = db.instances.get(i_eid)
  d = dict(title=instance.title, body=instance.body, eid=i_eid)
  return d

def person2Dict(person): 
  p = person.data()
  p['eid'] = person.eid
  return p

@app.route('/')
def show_instances():
  user = db.people.get(session['userId']) if session.get('logged_in') else None
  if user and user.username == app.config['USERNAME']: 
    isAdmin=True
  else: isAdmin=False
  if user: 
     instances = [i2Dict(i.eid, user) for i in db.instances.get_all() if user in i.outV('hasPeople')]
  else: 
     instances = [i2Dict(i.eid) for i in db.instances.get_all()]
  return render_template('show_instances.html', instances=instances, isAdmin=isAdmin) 


@app.route('/addinstance', methods=['POST'])
def add_instance(): 
  if not (session.get('logged_in') and db.people.get(session['userId']).username == app.config['USERNAME']): 
    abort(401)  
  instance = db.instances.create(title=request.form['title'], body=request.form['body'], datetime_created=current_datetime())
  flash('Neue Instanz haette angelegt werden muessen') 
  return redirect(url_for('show_instances'))

@app.route('/<int:i_eid>/proposals')
def show_proposals(): 
  proposals = []
  userEid = db.people.get(session['userId']).eid if session.get('logged_in') else None
  instance = db.instances.get(g.i_eid)
  i = dict(title=instance.title, eid=g.i_eid)
  for proposal in proposalsByVotes(g.i_eid):
    p = v2Dict(proposal.eid, loggedUserEid=userEid)
    proposals.append(p)
  return render_template('show_proposals.html', instance = i, entries=proposals)

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
  prop = db.proposals.create(title=request.form['title'], body=request.form['body'], datetime_created=current_datetime(), \
                      datetime_modfied=current_datetime(), votes_up=0, votes_down=0)
  instance = db.instances.get(g.i_eid)
  user = db.people.get(session['userId'])
  db.issues.create(user,prop)           # Edge1: User issues Proposal
  db.hasProposal.create(instance, prop) # Edge2: Proposal belongs to current Instance
  flash('Neuer Eintrag erfolgreich erstellt')
  return redirect(url_for('show_proposals'))

@app.route('/<int:i_eid>/addcomment/<int:prop_id>',methods=['POST'])
def add_comment(prop_id):
  if not session.get('logged_in'):
    abort(401)
  comment = db.comments.create(title=request.form['title'], body=request.form['body'], datetime_created=current_datetime(), \
                      datetime_modfied=current_datetime())
  user = db.people.get(session['userId'])
  db.issuesComment.create(user,comment) 
  db.hasComment.create(db.proposals.get(prop_id), comment)
  flash('Neuer Kommentar erfolgreich erstellt')
  return redirect(url_for('show_single_proposal', prop_id=prop_id))

@app.route('/<int:i_eid>/vote/<int:pro>/<int:eid>')
def vote(pro, eid):
  ''' Voting a proposoal or comment with Id eid. Upvote means pro==1, Downvote means pro==0'''
  if not session.get('logged_in'):
    abort(401)
  loggedUser = db.people.get(session['userId'])
  c_p = db.vertices.get(eid) # could be a comment or a proposal
  voteRels = [rel for rel in loggedUser.outE('votes') if rel.inV() == c_p]
  if voteRels and voteRels[0].pro!=pro:
    # User undoes vote => Delete Edge
    db.votes.delete(voteRels[0].eid)
    flash('Stimme rueckgaengig gemacht')
  if voteRels and voteRels[0].pro==pro: 
    # Voting up/down a second time is not allowed.
    abort(401)
  if not voteRels: 
    # No "Votes"-Edge exists => Create new "Votes"-Edge
    db.votes.create(loggedUser,c_p, pro=pro)
    if pro: flash('Erfolgreich dafuer gestimmt') 
    else:   flash('Erfolgreich dagegen gestimmt')
  if c_p.element_type == 'comment':
    proposal = c_p.inV('hasComment').next()
    return redirect(url_for('show_single_proposal', prop_id=proposal.eid))
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
        s = "Du hast Dich in Instanz %s eingeloggt" % instancetitle
        flash(s) 
        return redirect(url_for('show_proposals', i_eid=instance.eid))
      elif not users:
        error = 'Ungueltiger Benutzername fuer Instanz %s' % instancetitle
      else:
        error = 'Ungueltiges Passwort'
    return render_template('login.html', i_eid=None, instances = [dict(title=i.title) for i in db.instances.get_all()], error=error)
  
@app.route('/setinstance/<int:i_eid>')
def set_instance():
  instance = db.instances.get(g.i_eid)
  return redirect(url_for('show_proposals', i_eid=g.i_eid))

@app.route('/<int:i_eid>/logout')
def logout():
  session.pop('logged_in', None)
  session.pop('userId',None)
  session.pop('username',None)
  flash('Du hast Dich ausgeloggt')
  return redirect(url_for('show_instances'))

@app.route('/<int:i_eid>/signin', methods=['POST', 'GET'])
def signin():  
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

@app.route('/<int:i_eid>/person/<int:person_id>')
def show_person(person_id):
  if not session.get('logged_in'):
        abort(401)
  person = db.people.get(person_id)
  return render_template('show_person.html', person=dict(firstname=person.firstname, secondname=person.secondname,\
                         username=person.username, email=person.email))

@app.route('/<int:i_eid>/persons')
def show_people():
  instance = db.instances.get(g.i_eid)
  people = [person2Dict(p) for p in instance.outV('hasPeople')] 
  return render_template('show_people.html', people = people, 
                                             instance = dict(title=instance.title, eid=instance.eid))
  

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
