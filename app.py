from flask import Flask, request, send_file
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
from datetime import datetime
from configparser import ConfigParser

app = Flask(__name__)

config = ConfigParser()
config.read('config.ini')

if 'flask' in config:
    app.config['SECRET_KEY'] = config.get('flask', 'SECRET_KEY')
    app.config['DEBUG'] = config.getboolean('flask', 'DEBUG')
else:
    raise Exception("No [flask] section found in config.ini")

if 'database' in config:
    app.config['SQLALCHEMY_DATABASE_URI'] = config.get('database', 'SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.getboolean('database', 'SQLALCHEMY_TRACK_MODIFICATIONS')
else:
    raise Exception("No [database] section found in config.ini")

db = SQLAlchemy(app)

class tasks(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    date = db.Column(db.Date, default=datetime.now().date)  
    time = db.Column(db.Time, default=datetime.now().time)
    imagePath = db.Column(db.LargeBinary)
    description = db.Column(db.Text)
    
    def __init__(self, title, date, time, imagePath, description):
        self.title = title
        self.date = date
        self.time = time
        self.imagePath = imagePath
        self.description = description

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'title' not in request.form or 'imagePath' not in request.files or 'description' not in request.form:
        return 'Bad Request: Required fields missing in the request.', 400
    
    title = request.form['title']
    imagePath = request.files['imagePath'].read()
    description = request.form['description']

    current_utc_datetime = datetime.now()
    current_date = current_utc_datetime.date()
    current_time = current_utc_datetime.time()
    
    record = tasks(title=title, date=current_date, time=current_time, imagePath=imagePath, description=description)
    db.session.add(record)
    db.session.commit()

    return 'Image record successfully uploaded.', 200

@app.route('/get-image', methods=['GET'])
def get_image():
    record_id = request.args.get('id')

    if not record_id:
        return 'Bad Request: ID parameter is missing.', 400

    record = tasks.query.get(record_id)
    if not record:
        return f'Image record with ID {record_id} not found.', 404

    return send_file(
        BytesIO(record.imagePath),
        mimetype='image/jpeg',
        as_attachment=True,
        download_name=f'record_{record.id}.jpg'
    )

if __name__ == '__main__':
    
    with app.app_context():
        db.create_all()

    app.run(debug=True)
