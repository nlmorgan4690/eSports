from flask import render_template, request, Blueprint, current_app
from esports.models import Post
import markdown2
import os

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)


@main.route("/about")
def about():
    return render_template('about.html', title='About')

@main.route("/info")
def info():
    return render_template('main/info.html', title='Info')

@main.route('/preseason-checklist')
def pre_season_checklist():
    return render_template('main/pre_season_checklist.html')

@main.route('/pregame-checklist')
def pre_game_checklist():
    return render_template('main/pre_game_checklist.html')

@main.route('/esports-info')
def esports_info():
    md_path = os.path.join(current_app.root_path, 'static', 'docs', 'esports_info.md')
    with open(md_path, 'r') as f:
        content = markdown2.markdown(f.read())
    return render_template('main/esports_info.html', content=content)

@main.route('/firewall-ports')
def fw_ports():
    md_path = os.path.join(current_app.root_path, 'static', 'docs', 'allowed_ports.md')
    with open(md_path, 'r') as f:
        content = markdown2.markdown(f.read())
    return render_template('main/firewall_ports.html', content=content)

@main.route("/cfaq")
def cfaq():
    return render_template('main/coach_faq.html', title='FAQ')

@main.route("/device-setup")
def device_setup():
    return render_template('main/device_setup.html', title='DeviceSetup')

@main.route("/basic")
def basic_tshoot():
    md_path = os.path.join(current_app.root_path, 'static', 'docs', 'basic_network_troubleshooting.md')
    with open(md_path, 'r') as f:
        content = markdown2.markdown(f.read())
    return render_template('main/basic_network.html', content=content, title='B. Troubleshooting')

@main.route("/intermediate")
def intermediate_tshoot():
    md_path = os.path.join(current_app.root_path, 'static', 'docs', 'intermediate_network_troubleshooting.md')
    with open(md_path, 'r') as f:
        content = markdown2.markdown(f.read())
    return render_template('main/intermediate_network.html', content=content, title='I. Troubleshooting')

@main.route("/advanced")
def advanced_tshoot():
    md_path = os.path.join(current_app.root_path, 'static', 'docs', 'advanced_network_troubleshooting.md')
    with open(md_path, 'r') as f:
        content = markdown2.markdown(f.read())
    return render_template('main/advanced_network.html', content=content, title='A. Troubleshooting')

@main.route("/troubleshooting")
def troubleshooting():
    return render_template('main/torubleshooting.html', title='Info')