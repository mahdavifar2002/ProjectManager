from model import conf
from model.init import users
from model.init import messages

# conf.drop_db()
# conf.init_db()

users.insert()
messages.insert()
