'''
INITIALIZE
'''
# Import required Flask packages
from flask import (
	Flask, 
	render_template,
	send_from_directory
)

# Import other required packages
import json
import os

# Initialize app with static folder declared
app = Flask(__name__, static_folder='static')

# Global variable with the info for the 
json_path = os.path.join(
	app.static_folder, 
	'data', 
	'info.json'
)
with open(json_path) as f:
	info = json.load(f)

'''
CONTEXT
'''
# Make the global variable info available in parent template for menu
@app.context_processor
def inject_json_data():
	return {'info': info}  # Must be returned as dict


'''
STATIC VIEWS
'''
# Homepage 
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():

	# Render the index template
	return render_template('index.html', title='Home')

# Serve resume.pdf from the static folder
@app.route('/joe_wlos_resume.pdf', methods=['GET'])
def resume():

	# Send the robots file from static folder
	doc_path = os.path.join(app.static_folder, 'documents')
	return send_from_directory(doc_path, 'joe_wlos_resume.pdf')

# Serve robots.txt from the static folder
@app.route('/robots.txt', methods=['GET'])
def robots():

	# Send the robots file from static folder
	doc_path = os.path.join(app.static_folder, 'documents')
	return send_from_directory(doc_path, 'robots.txt')


'''
DYNAMIC VIEWS
'''
# Use the info JSON to populate the pages
@app.route('/<section>/<key>', methods=['GET'])
def page(section, key):

	# Render the template with data and title
	data = info[section]['pages'][key]
	title = data['page_name']
	return render_template('page.html', data=data, title=title)


'''
EXECUTION IN TERMINAL
'''
# Running app with updates for template files
if __name__ == '__main__':
	extra_dirs = [
		'templates',
		'static'
	]
	extra_files = extra_dirs[:]

	# Find all files in extra directories
	for extra_dir in extra_dirs:
		for dirname, dirs, files in os.walk(extra_dir):
			for filename in files:
				filename = os.path.join(dirname, filename)
				if os.path.isfile(filename):
					extra_files.append(filename)

	# Check if Heroku in environ before running
	if 'ON_HEROKU' not in os.environ:
		app.run(extra_files=extra_files, debug=True)
	else:
		app.run()  # On Heroku
