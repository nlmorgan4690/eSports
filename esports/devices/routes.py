from flask import render_template, url_for, flash, session, redirect, request, Blueprint, current_app
from flask_login import login_user, current_user, logout_user, login_required
from esports import db, bcrypt
from esports.models import Device, Platform, School
from esports.devices.forms import DeviceForm, UploadDeviceCSVForm

devices = Blueprint('devices', __name__)

@devices.route('/devices')
@login_required
def dashboard():
    if current_user.role.role not in ['Admin', 'Coach']:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))

    devices = Device.query.order_by(Device.date_added.desc()).all()
    form = DeviceForm()
    platforms = Platform.query.order_by(Platform.device_type).all()
    form.platform.choices = [(p.id, p.device_type) for p in platforms]

    return render_template('devices/dashboard.html', devices=devices, form=form)


@devices.route("/devices/add", methods=["GET", "POST"])
@login_required
def add_device():
    form = DeviceForm()
    form.platform.choices = [(p.id, p.device_type) for p in Platform.query.order_by(Platform.device_type).all()]

    # Show school field only for Admins
    if current_user.role.role == "Admin":
        form.school.choices = [(s.id, s.name) for s in School.query.order_by(School.name).all()]
    else:
        form.school.choices = []  # Prevent rendering errors if template loops choices

    if form.validate_on_submit():
        mac_clean = form.device_mac.data.lower()

        if Device.query.filter_by(device_mac=mac_clean).first():
            flash("This MAC address is already registered.", "warning")
            return redirect(url_for("devices.add_device"))

        # Determine school_id based on role
        school_id = current_user.school_id if current_user.role.role == "Coach" else form.school.data

        new_device = Device(
            device_name=form.device_name.data,
            device_mac=mac_clean,
            school_id=school_id,
            platform_id=form.platform.data
        )
        db.session.add(new_device)
        db.session.commit()
        flash("Device registered!", "success")
        return redirect(url_for("devices.dashboard"))

    return render_template("devices/form.html", form=form)



@devices.route('/delete/<int:device_id>', methods=['POST'])
@login_required
def delete_device(device_id):
    if current_user.role.role not in ['Admin', 'Coach']:
        flash('Access denied.', 'danger')
        return redirect(url_for('devices.dashboard'))

    device = Device.query.get_or_404(device_id)
    db.session.delete(device)
    db.session.commit()
    flash('Device deleted.', 'info')
    return redirect(url_for('devices.dashboard'))


@devices.route("/devices/upload", methods=["GET", "POST"])
@login_required
def upload_devices():
    form = UploadDeviceCSVForm()

    platforms = Platform.query.order_by(Platform.device_type).all()
    platform_map = {p.device_type.lower(): p.id for p in platforms}
    schools = School.query.order_by(School.name).all()
    school_map = {s.name.lower(): s.id for s in schools}

    if form.validate_on_submit():
        file = form.csv_file.data
        stream = TextIOWrapper(file, encoding="utf-8")
        reader = csv.DictReader(stream)

        added, skipped = 0, []

        for row in reader:
            name = row.get("Device Name", "").strip()
            mac = row.get("Mac Address", "").strip().lower()
            platform_name = row.get("Platform", "").strip().lower()
            school_name = row.get("School", "").strip().lower()

            if not name or not mac or not platform_name:
                skipped.append((name, mac, "Missing required fields"))
                continue

            # Validate MAC format
            import re
            if not re.match(r"^([0-9a-f]{2}[:-]){5}([0-9a-f]{2})$", mac):
                skipped.append((name, mac, "Invalid MAC format"))
                continue

            # Check duplicates
            if Device.query.filter_by(device_mac=mac).first():
                skipped.append((name, mac, "Duplicate MAC"))
                continue

            # Resolve platform
            platform_id = platform_map.get(platform_name)
            if not platform_id:
                skipped.append((name, mac, f"Unknown platform '{platform_name}'"))
                continue

            # Resolve school
            if current_user.role.role == "Coach":
                school_id = current_user.school_id
            else:
                school_id = school_map.get(school_name)
                if not school_id:
                    skipped.append((name, mac, f"Unknown school '{school_name}'"))
                    continue

            device = Device(
                device_name=name,
                device_mac=mac,
                school_id=school_id,
                platform_id=platform_id
            )
            db.session.add(device)
            added += 1

        db.session.commit()
        flash(f"✅ {added} devices added. ❌ {len(skipped)} skipped.", "info")
        for name, mac, reason in skipped:
            flash(f"Skipped {name} ({mac}) – {reason}", "warning")

        return redirect(url_for("devices.devices_dashboard"))

    return render_template("devices/upload.html", form=form, platforms=platforms, schools=schools)