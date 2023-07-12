import conf
import message


class User(conf.Base):
    __tablename__ = 'users'

    username = conf.Column(conf.String(50), primary_key=True)
    password = conf.Column(conf.String(50), nullable=False)
    fullname = conf.Column(conf.String(50))

    @classmethod
    def search_by_username(cls, username):
        return conf.session.query(User).filter(User.username == username)

    @classmethod
    def find_by_username(cls, username):
        return conf.session.query(User).filter(User.username == username).one()

    def save(self):
        conf.save_to_db(self)

    def messages(self, target_username):
        messages = conf.session.query(message.Message).filter(conf.or_(
            conf.and_(message.Message.sender_username == self.username,
                      message.Message.receiver_username == target_username),
            conf.and_(message.Message.sender_username == target_username,
                      message.Message.receiver_username == self.username))).all()

        messages.sort(key=lambda x: x.time_created)
        return messages
