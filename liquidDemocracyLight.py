from flask import Flask, session, render_template, request, redirect, url_for, escape, flash
from model import Person, Proposal, Graph
from bulbs.utils import current_datetime

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

def issuer(propId): 
  ''' Returns the User(s) which issued the Proposal with eid "propId" '''
  return [e.outV() for e in db.proposals.get(propId).inE('issued') ]

@app.route('/')
def show_proposals(): 
  entries = [dict(title=p.title, body=p.body, eid=p.eid, votes=p.votes_up-p.votes_down) for p in db.proposals.get_all()]
  for p in entries: 
    users = issuer(p['eid'])
    p['username'] = users[0].username if users else None
    p['userid'] = users[0].eid if users else None
  return render_template('show_proposals.html', entries=entries)

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

@app.route('/voteup/<int:prop_id>')
def vote_up(prop_id):
  if not session.get('logged_in'):
    abort(401)
  prop = db.proposals.get(prop_id)
  prop.votes_up += 1
  prop.save()
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
