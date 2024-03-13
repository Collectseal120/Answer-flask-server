# app.py

from flask import Flask, request, render_template, send_from_directory, redirect, url_for, session, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
import pyrebase
import ast
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import pytz
from werkzeug.utils import secure_filename
import os
from email.message import EmailMessage
import ssl
import smtplib
import secrets
import string

config = {
  #firebase credentials
  #poistin varmuuden vuoksi
}

config_storage= {
  #firebase storage credentials
  #poistin varmuuden vuoksi
}

firebase = pyrebase.initialize_app(config)
database = firebase.database()

storage = firebase.storage()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key' #postin varmuuden vuoksi
app.permanent_session_lifetime = timedelta(seconds=3600)

# Sample list
box_data = [
    ["/editor", "https://tse4.mm.bing.net/th?id=OIP.MxnpMS1A5JPp75Aw44lbtQHaH3&pid=Api&P=0&h=180", "Text Editor"],
    ["/library/Yhteiskuntaoppi", "https://tse3.mm.bing.net/th?id=OIP.VZPNQbhMpMGbvSbZuNvlUgAAAA&pid=Api&P=0&h=180", "Yhteiskuntaoppi"],
    ["/library/YhLäksyt", "https://i.postimg.cc/Wb9qCbcS/th-1.jpg", "YhLäksyt"],
    ["/library/Biologia", "https://mediapankki.otava.fi/api/v1/assets/by-isbn/978-951-1-27929-7.jpg", "Biologia"],
    ["/library/BiLäksyt", "https://mediapankki.otava.fi/api/v1/assets/by-isbn/978-951-1-27929-7.jpg", "BiLäksyt"],
    ["/library/Äidinkieli", "https://mediapankki.otava.fi/api/v1/assets/by-isbn/978-951-1-33657-0.jpg", "Äidinkieli"],
    ["/library/MaLäksyt", "data:image/jpeg;base64,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", "MaLäksyt"],
    ["/library/Yhteiskuntaoppi 8", "https://jyu.finna.fi/Cover/Show?source=Solr&author=&callnumber=&size=large&title=Aikalainen.+8&recordid=jykdok.1261905&isbns%5B0%5D=952631431X&invisbn=9789526314310&index=0", "Historia 8"]
]

editors = [
    ["/", "https://tse1.mm.bing.net/th?id=OIP.TWRWcySMnpG14yPY40qw1gAAAA&pid=Api&P=0&h=180", "Back"],
    ["/editor/Yhteiskuntaoppi", "https://tse3.mm.bing.net/th?id=OIP.VZPNQbhMpMGbvSbZuNvlUgAAAA&pid=Api&P=0&h=180", "Yhteiskuntaoppi"],
    ["/editor/YhLäksyt", "https://i.postimg.cc/Wb9qCbcS/th-1.jpg", "YhLäksyt"],
    ["/editor/Biologia", "https://mediapankki.otava.fi/api/v1/assets/by-isbn/978-951-1-27929-7.jpg", "Biologia"],
    ["/editor/BiLäksyt", "https://mediapankki.otava.fi/api/v1/assets/by-isbn/978-951-1-27929-7.jpg", "BiLäksyt"],
    ["/editor/Äidinkieli", "https://mediapankki.otava.fi/api/v1/assets/by-isbn/978-951-1-33657-0.jpg", "Äidinkieli"],
    ["/editor/MaLäksyt", "data:image/jpeg;base64,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", "MaLäksyt"],
    ["/editor/Yhteiskuntaoppi 8", "https://jyu.finna.fi/Cover/Show?source=Solr&author=&callnumber=&size=large&title=Aikalainen.+8&recordid=jykdok.1261905&isbns%5B0%5D=952631431X&invisbn=9789526314310&index=0", "Historia 8"]
]
dropdown_data = [
    {'name': 'Wiki', 'filename': 'Wiki.zip'}

]




def generate_random_key(length=50):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for i in range(length))

def add_date(text):
     numbers = text.split('.')
     date = ""
     additionals = []
     for i, num in enumerate(numbers):
         temp = num.split('+')
         if len(temp) == 2:
             d = temp[0]
             plus = temp[1]
         else:
             d = temp[0]
             plus = 0
         if i == len(numbers) - 1:
             date += f"{d}"
             additionals.append(plus)
         else:
             date += f"{d}."
             additionals.append(plus)



     date = datetime.strptime(date, '%d.%m.%Y').date()
     date = date + timedelta(days=int(additionals[0]))
     date = date + relativedelta(months=int(additionals[1]))
     date = date + relativedelta(years=int(additionals[2]))
     return date.strftime("%d.%m.%Y")


def setUser(user, password):
        data = {
        "password": password
        }

        database.child("Users").child(user).set(data)

def setUserImage(user, image):
        data = {
        "image": image
        }

        database.child("Users").child(user).child("settings").set(data)



def getUserImage(user):
        alldata = database.child("Users").get().val()
        try:
            data = alldata[user]["settings"]["image"]
            return True, data
        except:
            return False, "https://tse2.mm.bing.net/th?id=OIP._OqRgj5NA_zHcfc_qHYXdQHaHa&pid=Api&P=0&h=180"


def getUserData(user):
        alldata = database.child("Users").get().val()
        try:
            data = alldata[user]
            return True, data
        except:
            return False, None

def getUser(user):
        alldata = database.child("Users").get().val()
        try:
            password = alldata[user]["password"]
            return True, password
        except:
            return False, None
def getUserTags(user):
    alldata = database.child("Users").get().val()
    alldata = alldata[user]["permissions"]
    return alldata


def getData(subject):
        alldata = database.child("subjects").get().val()

        data = alldata[subject]["content"]
        permission = alldata[subject]["permissions"]
        return data, permission
def setUserTags(user,tags):

    database.child("Users").child(user).child("permissions").set(tags)
def addDataF(content,subject):

    data = content
    if content != "":
        database.child("subjects").child(subject).update(data)
        return True
    else:
        return False

def addNewKey(data, key_type,ownership=None):
        database.child("keys").child(key_type).child(data).update({'time': str(datetime.now())})
        database.child("keys").child(key_type).child(data).update({'ownership': str(ownership)})



@app.route('/library/<path:subpath>')
def library(subpath=''):
    if "logged_in" in session:
        content = getData(subpath.replace("library/", ""))
        print(content[1])
        print(session)
        if content[1] in session or "all-access" in session or content[1] == "public":
            values = {
            "content": content[0],
            }
            return render_template('library.html', text_values=values, dropdown_data=dropdown_data,profile_image=getUserImage(session['username'])[1], username=session['username'],is_admin=str(True if 'admin' in session else False).lower())
        else:
            return redirect(url_for('permission_denied'))
    else:
        return redirect(url_for("login", next="library/"+subpath))

@app.route('/')
def index():
    if 'logged_in' in session:
        return render_template('index_loggedin.html', box_data=box_data, dropdown_data=dropdown_data,profile_image=getUserImage(session['username'])[1], username=session['username'],is_admin=str(True if 'admin' in session else False).lower())
    else:
        return render_template('index.html', box_data=box_data, dropdown_data=dropdown_data)


@app.route('/editor')
def editorSelect():
    if 'admin' in session:
        return render_template('index_loggedin.html', box_data=editors, dropdown_data=dropdown_data,profile_image=getUserImage(session['username'])[1], username=session['username'], is_admin=str(True if 'admin' in session else False).lower())
    else:
        return redirect(url_for('login', next="editor"))

@app.route('/editor/<path:subpath>')
def editor(subpath=''):
    if subpath == "EnUutinen" and 'admin' not in session:
        return redirect('https://anwser.pythonanywhere.com/library/EnUutinen')
    try:
        content = getData(subpath)
        if content[1] == "public":
            payload = {
            "content": content[0]
            }
            return render_template('editor.html', initial_content=payload,subpath=subpath, dropdown_data=dropdown_data,profile_image=getUserImage(session['username'])[1], username=session['username'], is_admin=str(True if 'admin' in session else False).lower())
    except:
        pass
    if 'admin' in session:
        try:
            data = getData(subpath)
            payload = {
            "content": data[0]
            }
        except:
            return "This editor does not exist"
        return render_template('editor.html', initial_content=payload,subpath=subpath, dropdown_data=dropdown_data,profile_image=getUserImage(session['username'])[1], username=session['username'], is_admin=str(True if 'admin' in session else False).lower())
    else:
        return redirect(url_for('login', next="editor/"+subpath))


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory("files", filename, as_attachment=True)

@app.route('/save', methods=['POST'])
def save():
    try:
        subpath = request.args.get('subpath')
        content = request.get_json().get('content')
        print(subpath)
        data = {
        "content": content
        }
        addDataF(data,subpath)
        return 'Content saved successfully!', 200
    except Exception as e:
        print('Error saving content:', str(e))
        return 'Error saving content', 500



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')





@app.route('/protected')
def protected():
    if 'logged_in' in session:
        return 'This is the protected area. <a href="/logout">Logout</a>'
    else:
        return redirect(url_for('login', next="protected/"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        data = getUser(username)

        if data[0] and password == data[1]:
            session['logged_in'] = True
            session['username'] = username
            current_date = datetime.now()
            for tag in getUserTags(username):
                print(tag)
                #   tag = ast.literal_eval(tag)
                if tag['date'] != 'none':
                    date = datetime.strptime(tag['date'], '%d.%m.%Y')
                    if current_date < date:
                        session[tag['permission']] = True
                else:
                    session[tag['permission']] = True

            session['last_activity'] = datetime.now()

            # Redirect to the originally intended URL if present, otherwise go to home page
            if request.form.get('next') != "None":
                return redirect(request.form.get('next'))
            else:
                return redirect('/')

    return render_template('login.html', form=form, next=request.form.get('next'))


class requestResetPasswordForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Request password reset')




@app.route('/password-recovery', methods=['GET', 'POST'])
def reset_password():
    form = requestResetPasswordForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        token = generate_random_key(50)
        data = getUserData(username)
        addNewKey(token, "password-reset", username)
        if data[0] and email == data[1]['email']:
            email_sender = 'mypyalarm@gmail.com'
            email_password = 'en halua jakaa' #postin varmuuden vuoksi
            email_reciver = email

            subject = 'Anws password reset'
            body = f"""
            Hello {username},

A password reset was requested from your account. If this was not you, please ignore this message.

To reset your password, please click the link below:

[Reset Password]

If you are unable to click the link, please copy and paste the following URL into your browser:

http://anwser.pythonanywhere.com/reset-password?token={token}

If you have any questions or need further assistance, please contact our support team at support@example.com.

Best regards,
The Anws Team
            """

            em = EmailMessage()
            em['From'] = email_sender
            em['To'] = email_reciver
            em['Subject']= subject
            em.set_content(body)

            context = ssl.create_default_context()

            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, email_reciver, em.as_string())
            return redirect('/')

    return render_template('password-reset.html', form=form)

class resetPasswordForm(FlaskForm):
    password = StringField('New password', validators=[DataRequired()])
    checkPassword = StringField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Reset password')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_users_password():
    form = resetPasswordForm()
    if form.validate_on_submit():
        password = form.password.data
        checkPassword = form.checkPassword.data
        if password == checkPassword:
            token = request.form.get('token')
            try:
                data = database.child("keys").child("password-reset").child(token).get().val()
            except:
                data = None
            if data != None:
                date= datetime.strptime(data['time'], '%Y-%m-%d %H:%M:%S.%f')
                time_difference = datetime.now() - date
                if time_difference > timedelta(minutes=10):
                    database.child("keys").child("password-reset").child(token).remove()
                    return ("your token has expired")
                else:
                    ownership = data['ownership']
                    if ownership != None:
                        user_ref = database.child("Users").child(ownership)
                        user_ref.update({"password": password})
                        return ("succesfully changed your password")
                        database.child("keys").child("password-reset").child(token).remove()
            else:
                return ("there was an issue retriving the token please try again later")


    return render_template('password_resetting_link.html', form=form)


@app.before_request
def before_request():
    if 'logged_in' in session and session['logged_in']:
        # Check if the session has expired
        if 'last_activity' in session and datetime.now(pytz.utc) > session['last_activity'] + app.permanent_session_lifetime:
            # Clear all session variables
            session.clear()
            return redirect('/')
        else:
            # Update the last activity timestamp
            session['last_activity'] = datetime.now(pytz.utc)




@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
@app.route('/login', methods=['GET', 'POST'])


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        if getUser(username)[0] == False:
            if password == confirm_password:
                session['logged_in'] = True
                if username == "Collectseal120": #oma käyttäjä
                    session['admin'] = True
                setUser(username, password)
                session['username'] = username
                data = {
                "permission": 'yh',
                "date": 'none'
                }
                values = [data,{"permission": 'bi', "date": 'none'},{"permission": 'ai', "date": 'none'}]
                setUserTags(username, values)
                return redirect('/')
            else:
                flash('Passwords do not match', 'error')
        else:
            flash('Username already exists', 'error')

    return render_template('register.html', form=form)



class CreateForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    permissions = StringField('Permissions', validators=[DataRequired()])
    submit = SubmitField('Create')

@app.route('/create', methods=['GET', 'POST'])
def create():
    if "admin" in session:
        form = CreateForm()

        if form.validate_on_submit():
            name = form.name.data
            permissions = form.permissions.data



            data = {
            "content": "",
            "permissions": permissions
            }
            addDataF(data,name)
        else:
            flash('Something went wrong', 'error')

        return render_template('create.html', form=form)
    else:
        return redirect(url_for('permission_denied'))

@app.route('/permission_denied')
def permission_denied():
    return 'you do not have the rights to view this page <a href="/">Return home</a>'

@app.route('/users')
def users_panel():
    if 'logged_in' in session and 'admin' in session:
        allUsers= database.child("Users").get().val()
        userList = []
        for user in allUsers:
            list_of_perms = [[d['date'], d['permission']] for d in allUsers[user]["permissions"]]
            formatted_string = "[{}]".format(",\n".join(map(str, list_of_perms)))
            print(formatted_string)
            userList.append([user, formatted_string])

        return render_template('users_panel.html', users=userList, dropdown_data=dropdown_data, username=session['username'],profile_image=getUserImage(session['username'])[1])
    else:
        return 'you do not have the rights to view this page <a href="/">Return home</a>'


@app.route('/process_usersettings', methods=['POST'])
def process_label():
    data = request.get_json()

    username = data.get('username')
    label_value = data.get('label')
    try:
        processed_result = ast.literal_eval(label_value)
        print(processed_result)
        values = []
        for result in processed_result:
            if result[0] == 'none':
                data = {
                    "permission": result[1],
                    "date": 'none'
                    }
                values.append(data)
            else:
                data = {
                "permission": result[1],
                "date": add_date(result[0])
                }
                values.append(data)
        setUserTags(username, values)
        return jsonify({'result': label_value})
    except:
        return jsonify({'result': "something went wrong"})

    #processed_result = [item.replace(' ', '').replace('\n', '') for item in label_value.split(',')]





@app.route('/profile')
def profileEdit():
    if 'logged_in' in session:
        username = session['username']
        userData = getUserData(username)[1]
        image = getUserImage(username)[1]
        return render_template('profile.html', username=username, profile_image=image,owner=True, content=userData["permissions"])
    else:
        return redirect(url_for('login', next="profile"))

@app.route('/profile/<path:subpath>')
def profileView(subpath=''):
        owner = True if session['username'] == subpath else False
        try:
            data = getUserData(subpath)[1]
            image = getUserImage(subpath)[1]
            return render_template('profile.html', username=subpath, profile_image=image,owner=owner,content=data["permissions"])
        except:
            return "This profile does not exist"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    if file and allowed_file(file.filename):
        # Upload the file to Firebase Storage
        storage.child(file.filename).put(file)
        storage_url = storage.child(file.filename).get_url(None)
        setUserImage(session['username'], storage_url)

        return storage_url

@app.route('/account-settings')
def accountSettings():
    if 'logged_in' in session:
        username = session['username']
        userData = getUserData(username)[1]
        image = getUserImage(username)[1]
        return render_template('account_settings.html', username=username, profile_image=image,owner=True, content=userData["permissions"])
    else:
        return redirect(url_for('login', next="account-settings"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)




