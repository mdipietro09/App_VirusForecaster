###############################################################################
#                                MAIN                                         #
###############################################################################

import flask

from pkg.data import data
from pkg.model import model
from config.file_system import *



'''
'''
def create_app(name=None):
    ## app object
    name = name if name is not None else __name__
    app = flask.Flask(name, instance_relative_config=True, 
                      template_folder=dirpath+'app/client/templates',
                      static_folder=dirpath+'app/client/static')
    
    
    ## api
    @app.route('/ping', methods=["GET"])
    def ping():
        return 'pong'
    
    
    @app.route("/", methods=['GET', 'POST'])
    def index():
        try:
            ts = data()
            ts.get_data()
            app.logger.info("Got Data")

            if flask.request.method == 'POST':
                country = flask.request.form["country"]
                app.logger.info("Selected "+country)
            else:
                country = "World"
            
            ts.process_data(country)
            logistic = model()
            logistic.forecast(ts.cases)
            logistic.add_deaths(ts.mortality)
            img = logistic.plot(country)
            return flask.render_template("index.html", img=img, country=country, countrylist=ts.countrylist)
            
        except Exception as e:
            app.logger.error(e)
            flask.abort(500)
    
    
    ## errors
    @app.errorhandler(404)
    def page_not_found(e):
        return flask.render_template("errors.html", msg="Page doesn't exist"), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return flask.render_template('errors.html', msg="Something went terribly wrong"), 500
    
    
    return app