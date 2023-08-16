import jdatetime

from model import conf


class Message(conf.Base):
    __tablename__ = 'messages'

    id = conf.Column(conf.Integer, primary_key=True)
    text = conf.Column(conf.Text, nullable=False)

    voice_path = conf.Column(conf.Text)
    file_path = conf.Column(conf.Text)
    file_copy = conf.Column(conf.Boolean, default=False)
    file_is_dir = conf.Column(conf.Boolean, default=False)
    file_size = conf.Column(conf.BigInteger, default=0)
    copy_pid = conf.Column(conf.Integer, default=0)
    copy_percent = conf.Column(conf.Integer, default=0)

    sender_username = conf.Column(
        conf.String(50),
        conf.ForeignKey('users.username'),
        nullable=False)
    receiver_username = conf.Column(
        conf.String(50),
        conf.ForeignKey('users.username'),
        nullable=False)
    reply_to = conf.Column(
        conf.Integer,
        conf.ForeignKey('messages.id'))
    time_created = conf.Column(conf.DateTime(timezone=True), server_default=conf.func.now())
    time_updated = conf.Column(conf.DateTime(timezone=True), onupdate=conf.func.now())
    time_seen = conf.Column(conf.DateTime(timezone=True))
    has_been_seen = conf.Column(conf.Boolean, default=False)
    has_been_edited = conf.Column(conf.Boolean, default=False)
    deleted = conf.Column(conf.Boolean, default=False)
    pinned = conf.Column(conf.Boolean, default=False)

    def get_time_created(self):
        week = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']
        text = week[self.time_created.weekday()]
        text += "  "
        text += str(jdatetime.datetime.fromgregorian(datetime=self.time_created)).replace(" ", "  ")
        return text

    def get_time_updated(self):
        return str(jdatetime.datetime.fromgregorian(datetime=self.time_updated)).replace(" ", "   ")

    def get_time_seen(self):
        return str(jdatetime.datetime.fromgregorian(datetime=self.time_seen)).replace(" ", "   ")

    def short_text(self):
        max_len = 20

        the_text = self.text.replace("\n", " ")
        if self.file_path is not None:
            file_name = self.file_path.split('\\')[-1]
            the_text = f"{file_name} " + the_text

        if len(the_text) > max_len:
            the_text = the_text[:max_len] + "..."
        return the_text

    @classmethod
    def find_by_id(cls, id_):
        return conf.session.query(Message).filter(Message.id == id_).one()

    def save(self):
        conf.save_to_db(self)