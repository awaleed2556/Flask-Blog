
from flaskblog import create_app         # This will import from init file and the create_app function

app = create_app()                      # Running the create_app function
if __name__ == '__main__':
    app.run(debug=True,port=5000)

