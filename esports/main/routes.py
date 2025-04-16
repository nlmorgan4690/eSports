from flask import render_template, request, Blueprint
from esports.models import Post

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

@main.route('/preseason-checklist')
def pre_season_checklist():
    return render_template('main/pre_season_checklist.html')

@main.route('/pregame-checklist')
def pre_game_checklist():
    return render_template('main/pre_game_checklist.html')
