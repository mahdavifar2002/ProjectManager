from model import conf
from model.init import init_users
from model.init import init_messages

# conf.drop_db()
conf.init_db()

init_users.insert()
init_messages.insert()
