from model import conf


class Task(conf.Base):
    __tablename__ = 'tasks'

    id = conf.Column(conf.Integer, primary_key=True)
    assigner_username = conf.Column(
        conf.String(50),
        conf.ForeignKey('users.username'),
        nullable=False)
    assignee_username = conf.Column(
        conf.String(50),
        conf.ForeignKey('users.username'),
        nullable=False)
    description = conf.Column(conf.String(500))
    time_created = conf.Column(conf.DateTime(timezone=True), server_default=conf.func.now())
    time_updated = conf.Column(conf.DateTime(timezone=True), onupdate=conf.func.now())

    def save(self):
        conf.save_to_db(self)
