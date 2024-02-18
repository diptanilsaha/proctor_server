import secrets
from flask import current_app, Blueprint
from .database import db
from .models import User, Role, RoleName

cli_bp = Blueprint(
    "cli",
    import_name=__name__
)

@cli_bp.cli.command("create_users")
def create_roles_and_users():
    Role.insert_roles()

    admin_role = db.session.execute(
        db.select(Role).filter_by(
            name=RoleName.ADMIN
        )
    ).scalar_one_or_none()

    robot_role = db.session.execute(
        db.select(Role).filter_by(
            name = RoleName.ROBOT
        )
    ).scalar_one_or_none()

    admin_user = db.session.execute(
        db.select(User).filter_by(
            username = current_app.config['ADMIN_USERNAME']
        )
    ).scalar_one_or_none()

    if admin_user is None:
        admin_user = User()
        admin_user.username = current_app.config['ADMIN_USERNAME']
        admin_user.set_password(current_app.config['ADMIN_PASSWORD'])
        admin_user.role = admin_role
        db.session.add(admin_user)
        db.session.commit()


    robot_user = db.session.execute(
        db.select(User).filter_by(
            username = "proctor_bot"
        )
    ).scalar_one_or_none()

    if robot_user is None:
        robot_user = User()
        robot_user.username = "proctor_bot"
        robot_user.set_password(secrets.token_hex(16))
        robot_user.role = robot_role
        db.session.add(robot_user)
        db.session.commit()
