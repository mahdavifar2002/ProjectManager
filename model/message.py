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
    time_created = conf.Column(conf.DateTime(timezone=True), server_default=conf.func.now())
    time_updated = conf.Column(conf.DateTime(timezone=True), onupdate=conf.func.now())

    def get_time_created(self):
        return str(jdatetime.datetime.fromgregorian(datetime=self.time_created))

    def get_time_updated(self):
        return str(jdatetime.datetime.fromgregorian(datetime=self.time_updated))

    def save(self):
        conf.save_to_db(self)
