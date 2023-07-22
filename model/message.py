import jdatetime

from model import conf


class Message(conf.Base):
    __tablename__ = 'messages'

    id = conf.Column(conf.Integer, primary_key=True)
    text = conf.Column(conf.Text, nullable=False)
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
    has_been_seen = conf.Column(conf.Boolean, default=False)
    has_been_edited = conf.Column(conf.Boolean, default=False)

    def get_time_created(self):
        return str(jdatetime.datetime.fromgregorian(datetime=self.time_created))

    def get_time_updated(self):
        return str(jdatetime.datetime.fromgregorian(datetime=self.time_updated))

    def short_text(self):
        the_text = self.text.replace("\n", " ")
        if len(the_text) > 20:
            the_text = the_text[:20] + "..."
        return the_text

    @classmethod
    def find_by_id(cls, id_):
        return conf.session.query(Message).filter(Message.id == id_).one()

    def save(self):
        conf.save_to_db(self)