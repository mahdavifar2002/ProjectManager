import datetime

from model import conf, message, task


class User(conf.Base):
    __tablename__ = 'users'

    username = conf.Column(conf.String(50), primary_key=True)
    password = conf.Column(conf.String(50), nullable=False)
    fullname = conf.Column(conf.String(50))

    time_created = conf.Column(conf.DateTime(timezone=True), server_default=conf.func.now())
    time_updated = conf.Column(conf.DateTime(timezone=True), onupdate=conf.func.now())
    last_seen = conf.Column(conf.DateTime(timezone=True), server_default=conf.func.now())

    is_online = conf.Column(conf.Boolean)
    typing_date = conf.Column(conf.DateTime(timezone=True), server_default=conf.func.now())
    typing_target = conf.Column(
        conf.String(50),
        conf.ForeignKey('users.username'))

    @classmethod
    def search_by_username(cls, username):
        return conf.session.query(User).filter(User.username == username)

    @classmethod
    def find_by_username(cls, username):
        return conf.session.query(User).filter(User.username == username).one()

    def save(self):
        conf.save_to_db(self)

    @staticmethod
    def users():
        return conf.session.query(User).all()

    def messages(self, target_username):
        query = conf.session.query(message.Message).filter(conf.or_(
            conf.and_(message.Message.sender_username == self.username,
                      message.Message.receiver_username == target_username),
            conf.and_(message.Message.sender_username == target_username,
                      message.Message.receiver_username == self.username))).order_by("time_created")

        messages = query.all()
        return messages

    def ten_messages(self, target_username, before_id: int | None = None):
        if before_id is None:
            before_id = 2147483647 # max int in mysql

        query = conf.session.query(message.Message).filter(conf.or_(
            conf.and_(message.Message.sender_username == self.username,
                      message.Message.receiver_username == target_username),
            conf.and_(message.Message.sender_username == target_username,
                      message.Message.receiver_username == self.username)))
        query = query.filter(message.Message.id < before_id).order_by(message.Message.time_created.desc()).limit(10)

        messages = query.all()
        messages.reverse()

        return messages

    def search_messages(self, search: str):
        query = conf.session.query(message.Message).filter(conf.and_(conf.or_(
                message.Message.sender_username == self.username,
                message.Message.receiver_username == self.username)),
            message.Message.text.contains(search)).order_by(conf.desc("time_created"))

        messages = query.all()
        return messages

    def last_message(self, target_username):
        messages = self.messages(target_username)
        if len(messages) > 0:
            return messages[-1]
        else:
            return None

    def tasks(self):
        tasks = conf.session.query(task.Task).filter(task.Task.assignee_username == self.username).all()
        tasks.sort(key=lambda x: x.time_created, reverse=True)
        return tasks

    def get_last_seen(self):
        return "last seen " + conf.date_human_readable(self.last_seen) + " ago"

    def set_typing(self, target_username):
        self.last_seen = conf.func.now()
        self.typing_date = conf.func.now()
        self.typing_target = target_username

    def is_typing_for(self, username) -> bool:
        correct_target_condition = (username == self.typing_target)

        # now = conf.session.query(conf.func.current_date().select()).one()
        now = conf.db_time()
        freshness_condition = conf.time_diff_in_second(now, self.typing_date) < 3

        # print(f"({correct_target_condition}, {freshness_condition}, {correct_target_condition + freshness_condition})")
        # print(f"({self.typing_date.timestamp()}, {datetime.datetime.now() - datetime.timedelta(seconds=3)})")
        return correct_target_condition + freshness_condition == 2
