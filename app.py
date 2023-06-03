from flask import Flask, render_template, request
import sqlite3
import requests


app = Flask(__name__)
# path for the image to be tested
path = "home/pi/Desktop/TEFinalProjectT3/images/"

def validate_user(email, password):
    print("validating user...")
    user = {}

    conn = sqlite3.connect('./static/d/activity_tracker.db')
    curs = conn.cursor()
    #get all columns if there is a match
    result  = curs.execute("SELECT name, email, phone FROM users WHERE email=(?) AND password= (?)", [email, password])
  
    for row in result:
       user = {'name': row[0],  'email': row[1], 'phone': row[2]}
         
    conn.close()
    return user


def store_user(name, email, phone, pw):
    conn = sqlite3.connect('./static/d/activity_tracker.db')
    curs = conn.cursor()
    curs.execute("INSERT INTO users (name, email, phone, password) VALUES((?),(?),(?),(?))",
        (name, email, phone, pw))
    
    conn.commit()
    conn.close()


def get_all_users():
    conn = sqlite3.connect('./static/d/activity_tracker.db')
    curs = conn.cursor()
    all_users = [] # will store them in a list
    rows = curs.execute("SELECT rowid, * from users")
    for row in rows:
        user = {'rowid': row[0],
                'name' : row[1], 
                'email': row[2],
                'phone': row[3],
                }
        all_users.append(user)

    conn.close()

    return all_users


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login_user' , methods=['POST'])
def login_user():

    response = requests.get("https://animechan.vercel.app/api/random/character?name=saitama")
    json_data = response.json()
    print(json_data)
    email = request.form['email']
    password = request.form['password']

    all_data = []
    user = validate_user(email, password)
    
    # connect for selection of "data"
    conn = sqlite3.connect('./static/d/activity_tracker.db')
    curs = conn.cursor()
    rows = curs.execute("SELECT anime, quote, character from data")
    data = {}
    for row in rows:
        data = {
                'anime' : json_data['anime'], 
                'quote': json_data['quote'],
                'character': json_data['character'],
        }
    if user:
        # data2 = {
        #     "anime": rows["anime"],
        #     "quote": rows["quote"],
        #     "character": rows["character"]
        # }
        all_data.append(data)
        conn.close()
        #load home if there is a user, along with data.
        return render_template('home.html', data=all_data)
         

    else: 
        error_msg = "Login failed"

        data = {
            "error_msg": error_msg
        }
        #no user redirects back to the main login page, with error msg.
        return render_template('index.html', data=data)

@app.route('/powers', methods=['POST','GET'])
def powers(): 
    conn = sqlite3.connect('./static/d/activity_monitor.db')
    #curs = conn.cursor()
    rows = conn.execute('''SELECT stat_name, stat_number FROM powers''').fetchall()
    print(rows)
    # all_data = []
    # for row in rows:
    #     data = {
    #             'stat_name': row[0], 
    #             'stat_number': row[1],
    #     }
        # data2 = {
        #     "anime": rows["anime"],
        #     "quote": rows["quote"],
        #     "character": rows["character"]
        # }
    # all_data.append(data)
    conn.close()
    return render_template('powers.html', data=rows)


@app.route('/post_user' , methods=['POST'])
def post_user():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    pw = request.form['password']
    
    store_user(name, email, phone, pw)

    users = get_all_users()
    # print(users)

    #get the last user entered
    new_user = users.pop()


    return render_template('index.html', user=new_user)

def detect_faces(path):
    """Detects faces in an image."""
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    with open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.face_detection(image=image)
    faces = response.face_annotations

    # Names of likelihood from google.cloud.vision.enums
    likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                       'LIKELY', 'VERY_LIKELY')
    print('Faces:')

    for face in faces:
        print(f'anger: {likelihood_name[face.anger_likelihood]}')
        print(f'joy: {likelihood_name[face.joy_likelihood]}')
        print(f'surprise: {likelihood_name[face.surprise_likelihood]}')

        vertices = ([f'({vertex.x},{vertex.y})'
                    for vertex in face.bounding_poly.vertices])

        print('face bounds: {}'.format(','.join(vertices)))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='3000')