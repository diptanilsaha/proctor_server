from proctor import login_manager, db
from proctor.models import User

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
