from flask import Flask, render_template

import config as cfg

app = Flask(__name__)

@app.route("/")
def home():    
    return render_template(
        "index.html", 
        nav_id=cfg.TEMPLATE["NAVBAR"]["ID"],
        btn_ids=cfg.INDEX
    )

@app.route("/graphs")
def graphs():
    return render_template(
        "graphs.html",
        nav_id=cfg.TEMPLATE["NAVBAR"]["ID"],
        graph_id=cfg.GRAPHS["ID"]
    )

@app.route("/maps")
def maps():
    return render_template(
        "maps.html",
        nav_id=cfg.TEMPLATE["NAVBAR"]["ID"],
        map_id=cfg.MAPS["ID"]
    )

@app.route("/carousel")
def carousel():
    return render_template(
        "carousel.html",
        nav_id=cfg.TEMPLATE["NAVBAR"]["ID"],
        carousel_id=cfg.CAROUSEL["ID"]
    )

@app.route("/about")
def about():
    return render_template(
        "about.html",
        nav_id=cfg.TEMPLATE["NAVBAR"]["ID"],
        about_id=cfg.ABOUT["ID"]
    )
    
if __name__ == "__main__":
    app.run(debug=True)