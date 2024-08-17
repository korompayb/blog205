from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

# Load existing posts from a JSON file
def load_posts():
    if os.path.exists("posts.json"):
        with open("posts.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_posts(posts):
    with open("posts.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/posts')
def get_posts():
    return jsonify(load_posts())

@app.route('/post/<int:post_id>')
def post(post_id):
    posts = load_posts()
    post = posts[post_id]
    return render_template('post.html', post=post)

@app.route('/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        posts = load_posts()
        title = request.form['title']
        content = request.form['content']

        # Handle file upload
        image_paths = []
        if 'file' in request.files:
            files = request.files.getlist('file')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    image_paths.append(os.path.join('uploads', filename))

        post_id = len(posts)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        post = {
            'id': post_id,
            'title': title,
            'content': content,
            'created_at': timestamp,
            'updated_at': timestamp,
            'image_paths': image_paths
        }
        posts.append(post)
        save_posts(posts)

        return redirect(url_for('post', post_id=post_id))
    return render_template('new_post.html')


@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    posts = load_posts()
    post = posts[post_id]

    if request.method == 'POST':
        if 'delete' in request.form:
            # Delete image if exists
            for image_path in post.get('image_paths', []):
                if image_path and os.path.exists(os.path.join('static', image_path)):
                    os.remove(os.path.join('static', image_path))

            posts.pop(post_id)
            # Reassign IDs to maintain sequential order
            for i, post in enumerate(posts):
                post['id'] = i

            save_posts(posts)

            return redirect(url_for('index'))
        else:
            post['title'] = request.form['title']
            post['content'] = request.form['content']

            # Handle file upload
            if 'file' in request.files:
                files = request.files.getlist('file')
                for file in files:
                    if file and allowed_file(file.filename):
                        # Delete old image if exists
                        for image_path in post.get('image_paths', []):
                            if image_path and os.path.exists(os.path.join('static', image_path)):
                                os.remove(os.path.join('static', image_path))

                        filename = secure_filename(file.filename)
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        post['image_paths'].append(os.path.join('uploads', filename))

            post['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_posts(posts)

            return redirect(url_for('post', post_id=post_id))

    return render_template('edit_post.html', post=post)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, host='0.0.0.0', port=81)
