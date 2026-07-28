from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import db_base

class StudyCard(db_base):
    __tablename__ = 'study_cards'

    id = Column(Integer, primary_key=True)

    prompt = Column(String(400), nullable=False)
    response = Column(String(800), nullable=False)
    source = Column(Text, nullable=True)
    topic = Column(String(50), default='general')
    level = Column(Integer, default=1)

    creation_date = Column(DateTime, server_default=func.now())
    updated_date = Column(DateTime, onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'prompt': self.prompt,
            'response': self.response,
            'source': self.source,
            'topic': self.topic,
            'level': self.level,
            'creation_date': self.creation_date.isoformat() if self.creation_date else None,
            'updated_date': self.updated_date.isoformat() if self.updated_date else None,
        }

    def __repr__(self):
        return f'<StudyCard {self.id}: {self.prompt} {self.response} {self.source} {self.topic} {self.level}>'
