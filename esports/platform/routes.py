from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from esports import db
from esports.models import Platform
from esports.platform.form import PlatformForm, DeleteForm
from esports.platform.utils import save_platform_icon

platforms = Blueprint('platforms', __name__)

DEFAULT_ICON_URL = "/static/img/default_platform_icon.png"

@platforms.route('/platforms', methods=['GET', 'POST'])
@login_required
def platform_dashboard():
    if current_user.role.role != 'Admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('main.home'))

    form = PlatformForm()
    delete_form = DeleteForm()
    platforms_list = Platform.query.order_by(Platform.device_type).all()

    if form.validate_on_submit():
        icon_file = request.files.get('platform_icon')

        try:
            icon_filename = save_platform_icon(icon_file)
            icon_url = url_for('static', filename=f'platform_icons/{icon_filename}') if icon_filename else DEFAULT_ICON_URL
        except ValueError:
            flash("The uploaded file is not a valid image. Please upload a JPG or PNG file.", 'danger')
            return render_template('platform/platform_dashboard.html', platforms=platforms_list, form=form, delete_form=delete_form)

        new_platform = Platform(
            device_type=form.device_type.data,
            platform_icon=icon_url
        )
        db.session.add(new_platform)
        db.session.commit()
        flash('Platform added successfully.', 'success')
        return redirect(url_for('platforms.platform_dashboard'))


    return render_template('platform/platform_dashboard.html', platforms=platforms_list, form=form, delete_form=delete_form)

@platforms.route('/platforms/delete/<int:platform_id>', methods=['POST'])
@login_required
def delete(platform_id):
    if current_user.role.role != 'Admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('main.home'))

    platform = Platform.query.get_or_404(platform_id)
    db.session.delete(platform)
    db.session.commit()
    flash('Platform deleted.', 'info')
    return redirect(url_for('platforms.platform_dashboard'))