from model import conf, message, task


class User(conf.Base):
    __tablename__ = 'users'

    username = conf.Column(conf.String(50), primary_key=True)
    password = conf.Column(conf.String(50), nullable=False)
    fullname = conf.Column(conf.String(50))
    time_created = conf.Column(conf.DateTime(timezone=True), server_default=conf.func.now())
    time_updated = conf.Column(conf.DateTime(timezone=True), onupdate=conf.func.now())

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

    def tasks(self):
        tasks = conf.session.query(task.Task).filter(task.Task.assignee_username == self.username).all()
        tasks.sort(key=lambda x: x.time_created, reverse=True)
        return tasks
