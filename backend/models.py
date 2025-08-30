from __init__ import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    skills = db.Column(db.Text, nullable=True)
    experience_level = db.Column(db.String(50), default='beginner')
    hourly_rate = db.Column(db.Float, default=0.0)
    portfolio_url = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_skills_list(self):
        return [skill.strip() for skill in self.skills.split(',')] if self.skills else []
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'skills': self.skills,
            'experience_level': self.experience_level,
            'hourly_rate': self.hourly_rate,
            'portfolio_url': self.portfolio_url,
            'bio': self.bio,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class JobOpportunity(db.Model):
    __tablename__ = 'job_opportunities'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.Text, nullable=True)
    budget = db.Column(db.Float, nullable=True)
    source = db.Column(db.String(100), nullable=False)  # upwork, freelancer, etc.
    source_url = db.Column(db.String(500), nullable=True)
    client_name = db.Column(db.String(100), nullable=True)
    match_score = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'required_skills': self.required_skills,
            'budget': self.budget,
            'source': self.source,
            'source_url': self.source_url,
            'client_name': self.client_name,
            'match_score': self.match_score,
            'created_at': self.created_at.isoformat()
        }

class Proposal(db.Model):
    __tablename__ = 'proposals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_opportunities.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='sent')  # sent, accepted, rejected
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='proposals')
    job = db.relationship('JobOpportunity', backref='proposals')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_id': self.job_id,
            'content': self.content,
            'status': self.status,
            'sent_at': self.sent_at.isoformat(),
            'job_title': self.job.title if self.job else None
        }

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    client_name = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    budget = db.Column(db.Float, nullable=False)
    hours_worked = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='active')  # active, completed, cancelled
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='projects')
    
    @property
    def hourly_rate(self):
        return self.budget / self.hours_worked if self.hours_worked > 0 else 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'client_name': self.client_name,
            'description': self.description,
            'budget': self.budget,
            'hours_worked': self.hours_worked,
            'status': self.status,
            'hourly_rate': self.hourly_rate,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat()
        }

class TimeLog(db.Model):
    __tablename__ = 'time_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    description = db.Column(db.Text, nullable=True)
    hours = db.Column(db.Float, nullable=False)
    date_logged = db.Column(db.Date, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='time_logs')
    project = db.relationship('Project', backref='time_logs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'project_id': self.project_id,
            'description': self.description,
            'hours': self.hours,
            'date_logged': self.date_logged.isoformat(),
            'project_title': self.project.title if self.project else None,
            'created_at': self.created_at.isoformat()
        }

class SkillGap(db.Model):
    __tablename__ = 'skill_gaps'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    missing_skill = db.Column(db.String(100), nullable=False)
    job_missed_count = db.Column(db.Integer, default=1)
    learning_resource = db.Column(db.String(500), nullable=True)
    priority_score = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='identified')  # identified, learning, acquired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='skill_gaps')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'missing_skill': self.missing_skill,
            'job_missed_count': self.job_missed_count,
            'learning_resource': self.learning_resource,
            'priority_score': self.priority_score,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class ClientCommunication(db.Model):
    __tablename__ = 'client_communications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    message_type = db.Column(db.String(50), nullable=False)  # proposal, negotiation, update, etc.
    client_message = db.Column(db.Text, nullable=True)
    ai_suggestion = db.Column(db.Text, nullable=False)
    user_response = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='communications')
    project = db.relationship('Project', backref='communications')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'project_id': self.project_id,
            'message_type': self.message_type,
            'client_message': self.client_message,
            'ai_suggestion': self.ai_suggestion,
            'user_response': self.user_response,
            'created_at': self.created_at.isoformat()
        }
