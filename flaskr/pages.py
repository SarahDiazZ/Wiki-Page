from flask import render_template
from flaskr import backend
#from flask import Flask, abort

def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        # TODO(Checkpoint Requirement 2 of 3): Change this to use render_template
        # to render main.html on the home page.
        return render_template("main.html")

    # TODO(Project 1): Implement additional routes according to the project requirements.
    @app.route("/pages")
    def pages():
        return "This is the pages page"
        
    @app.route("/pages/<page_title>")
    def page_uploads(page_title):
        pass


    @app.route("/about")
    def about():
        return "About this Wiki"
        


