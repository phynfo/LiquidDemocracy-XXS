from flask import Flask, session, render_template, request, redirect, url_for, escape, flash
from model import Person, Proposal, Graph
from bulbs.utils import current_datetime
from datetime import datetime
from utils import date_diff

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

def proposalsByVotes():
  ''' Sorts proposals by vote-count '''
  return sorted(db.proposals.get_all(), key=lambda p:len(list(p.inE('votes'))), reverse=True)

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

@app.route('/')
def show_proposals(): 
  entries = []
  userEid = db.people.get(session['userId']).eid if session.get('logged_in') else None
  for proposal in proposalsByVotes():
    p = v2Dict(proposal.eid, loggedUserEid=userEid)
    entries.append(p)
  return render_template('show_proposals.html', entries=entries)

@app.route('/proposal/<int:prop_id>')
def show_single_proposal(prop_id):
   userEid = db.people.get(session['userId']).eid if session.get('logged_in') else None
   proposal = v2Dict(prop_id, loggedUserEid=userEid)
   comments = []
   for comment in commentsByVotes(prop_id):
     c = v2Dict(comment.eid, loggedUserEid=userEid)
     comments.append(c)
   return render_template('show_single_proposal.html', proposal=proposal, comments=comments)

@app.route('/add',methods=['POST'])
def add_proposal():
  if not session.get('logged_in'):
    abort(401)
  prop = db.proposals.create(title=request.form['title'], body=request.form['body'], datetime_created=current_datetime(), \
                      datetime_modfied=current_datetime(), votes_up=0, votes_down=0)
  user = db.people.get(session['userId'])
  db.issues.create(user,prop) 
  flash('Neuer Eintrag erfolgreich erstellt')
  return redirect(url_for('show_proposals'))

@app.route('/addcomment/<int:prop_id>',methods=['POST'])
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


@app.route('/voteup/<int:prop_id>')
def vote_up(prop_id):
  if not session.get('logged_in'):
    abort(401)
  loggedUser = db.people.get(session['userId'])
  proposal = db.proposals.get(prop_id)
  voteRels = [rel for rel in loggedUser.outE('votes') if rel.inV() == proposal]
  if voteRels and voteRels[0].pro==0: 
    # Kante loeschen!
    db.votes.delete(voteRels[0].eid)
  if voteRels and voteRels[0].pro==1:
    abort(401)
  if not voteRels:
    db.votes.create(loggedUser,proposal,pro=1)
  return redirect(url_for('show_proposals'))

@app.route('/votedown/<int:prop_id>')
def vote_down(prop_id):
  if not session.get('logged_in'):
    abort(401)
  loggedUser = db.people.get(session['userId'])
  proposal = db.proposals.get(prop_id)
  voteRels = [rel for rel in loggedUser.outE('votes') if rel.inV() == proposal]
  if voteRels and voteRels[0].pro==1:
    #Kante loeschen
    db.votes.delete(voteRels[0].eid)
  if voteRels and voteRels[0].pro==0:
    abort(401)
  if not voteRels:
    db.votes.create(loggedUser,proposal, pro=0)
  return redirect(url_for('show_proposals'))

@app.route('/delete/<int:prop_id>')
def delete_proposal(prop_id):
  if not session.get('logged_in'):
    abort(401)
  title = db.proposals.get(prop_id)
  resp = db.proposals.delete(prop_id)
  flash('Eintrag geloescht')
  return redirect(url_for('show_proposals'))

@app.route('/login',methods=['POST','GET'])
def login(): 
  error = None
  if request.method == 'POST':
    username = request.form['username'] ; password = request.form['password']
    users = [p for p in db.people.index.lookup(username=username)]
    if users and users[0].password==password: 
      session['logged_in'] = True
      session['userId'] = users[0].eid ; session['username'] = users[0].username
      flash('Du hast Dich eingeloggt') 
      return redirect(url_for('show_proposals'))
    elif not users:
      error = 'Ungueltiger Benutzername'
    else:
      error = 'Ungueltiges Passwort'
  return render_template('login.html', error=error)

@app.route('/logout')
def logout():
  session.pop('logged_in', None)
  session.pop('userId',None)
  session.pop('username',None)
  flash('Du hast Dich ausgeloggt')
  return redirect(url_for('show_proposals'))

@app.route('/signin', methods=['POST', 'GET'])
def signin():  
  error = None
  if request.method == 'POST':
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
      db.people.create(firstname=vorname, secondname=nachname, username=username, password=pass1, email=email)
      flash('Benutzer erfolgreich angelegt')
      return redirect(url_for('show_proposals'))
  return render_template('signin.html', error=error)

@app.route('/person/<int:person_id>')
def show_person(person_id):
  if not session.get('logged_in'):
    abort(401)
  person = db.people.get(person_id)
  return render_template('personendaten.html', person=dict(firstname=person.firstname, secondname=person.secondname,\
                         username=person.username, email=person.email))

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
