from flask import Blueprint, request, jsonify, session
from flask_cors import cross_origin
# Import all required models
from models import User, JobOpportunity, Proposal, Project, TimeLog, SkillGap, ClientCommunication
from __init__ import db

# Import AI services
from ai_services import AIService
from job_scraper import JobScraper

# Initialize services
ai_service = AIService()
job_scraper = JobScraper()

import os
from datetime import datetime, timedelta
from sqlalchemy import func, desc

main = Blueprint('main', __name__)

# Basic Routes
@main.route('/test', methods=['GET'])
@cross_origin()
def test():
    return jsonify({'message': 'Backend connected successfully!', 'status': 'running'})

@main.route('/', methods=['GET'])
@cross_origin()
def home():
    return jsonify({
        'message': 'Freelance AI Manager API',
        'version': '1.0.0',
        'endpoints': [
            '/api/test',
            '/api/register',
            '/api/login',
            '/api/logout'
        ]
    })

# Authentication Routes
@main.route('/register', methods=['POST'])
@cross_origin()
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name', '')
        skills = data.get('skills', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        

            
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'User with this email already exists'}), 409
        
        user = User(
            email=email,
            full_name=full_name,
            skills=skills,
            experience_level=data.get('experience_level', 'beginner'),
            hourly_rate=data.get('hourly_rate', 0.0)
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@main.route('/login', methods=['POST'])
@cross_origin()
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            return jsonify({
                'message': 'Login successful',
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
            
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@main.route('/logout', methods=['POST'])
@cross_origin()
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200

# Job Opportunity Routes
@main.route('/jobs/search/<int:user_id>', methods=['GET'])
@cross_origin()
def search_jobs(user_id):
    try:
        # FIXED: Check if required models and services exist
        if not all([User, JobOpportunity, job_scraper, ai_service]):
            return jsonify({'error': 'Required services not available'}), 500
            
        user = User.query.get_or_404(user_id)
        
        # Scrape new jobs
        new_jobs = job_scraper.scrape_jobs()
        
        # Store jobs in database and calculate match scores
        matched_jobs = []
        for job_data in new_jobs:
            # Check if job already exists
            existing_job = JobOpportunity.query.filter_by(
                title=job_data['title'],
                source=job_data['source']
            ).first()
            
            if not existing_job:
                # Calculate match score using AI
                match_score = ai_service.calculate_job_match(
                    user.get_skills_list(),
                    job_data['required_skills'],
                    job_data['description']
                )
                
                job = JobOpportunity(
                    title=job_data['title'],
                    description=job_data['description'],
                    required_skills=', '.join(job_data['required_skills']),
                    budget=job_data.get('budget'),
                    source=job_data['source'],
                    source_url=job_data.get('url'),
                    client_name=job_data.get('client_name'),
                    match_score=match_score
                )
                
                db.session.add(job)
                
                if match_score > 50:  # Only return high-match jobs
                    matched_jobs.append(job.to_dict())
        
        db.session.commit()
        
        return jsonify({
            'jobs': matched_jobs,
            'total_found': len(new_jobs),
            'high_match_jobs': len(matched_jobs)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Job search failed: {str(e)}'}), 500

@main.route('/jobs/<int:user_id>', methods=['GET'])
@cross_origin()
def get_jobs(user_id):
    try:
        # FIXED: Check if JobOpportunity model exists
        if 'JobOpportunity' not in globals():
            return jsonify({'error': 'JobOpportunity model not available'}), 500
            
        # Get jobs with high match scores
        jobs = JobOpportunity.query.filter(
            JobOpportunity.match_score > 50,
            JobOpportunity.is_active == True
        ).order_by(desc(JobOpportunity.match_score)).limit(20).all()
        
        return jsonify({
            'jobs': [job.to_dict() for job in jobs]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get jobs: {str(e)}'}), 500

# Proposal Routes
@main.route('/proposals/generate', methods=['POST'])
@cross_origin()
def generate_proposal():
    try:
        # FIXED: Check if required models exist
        if not all([User, JobOpportunity, Proposal, ai_service]):
            return jsonify({'error': 'Required services not available'}), 500
            
        data = request.get_json()
        user_id = data.get('user_id')
        job_id = data.get('job_id')
        
        user = User.query.get_or_404(user_id)
        job = JobOpportunity.query.get_or_404(job_id)
        
        # Generate AI proposal
        proposal_content = ai_service.generate_proposal(
            user.to_dict(),
            job.to_dict()
        )
        
        proposal = Proposal(
            user_id=user_id,
            job_id=job_id,
            content=proposal_content
        )
        
        db.session.add(proposal)
        db.session.commit()
        
        return jsonify({
            'message': 'Proposal generated successfully',
            'proposal': proposal.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Proposal generation failed: {str(e)}'}), 500

@main.route('/proposals/<int:user_id>', methods=['GET'])
@cross_origin()
def get_user_proposals(user_id):
    try:
        if 'Proposal' not in globals():
            return jsonify({'error': 'Proposal model not available'}), 500
            
        proposals = Proposal.query.filter_by(user_id=user_id).order_by(desc(Proposal.sent_at)).all()
        return jsonify({
            'proposals': [proposal.to_dict() for proposal in proposals]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get proposals: {str(e)}'}), 500

# Project & Time Tracking Routes
@main.route('/projects', methods=['POST'])
@cross_origin()
def create_project():
    try:
        if 'Project' not in globals():
            return jsonify({'error': 'Project model not available'}), 500
            
        data = request.get_json()
        
        project = Project(
            user_id=data.get('user_id'),
            title=data.get('title'),
            client_name=data.get('client_name'),
            description=data.get('description'),
            budget=float(data.get('budget', 0))
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'message': 'Project created successfully',
            'project': project.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Project creation failed: {str(e)}'}), 500

@main.route('/projects/<int:user_id>', methods=['GET'])
@cross_origin()
def get_user_projects(user_id):
    try:
        if 'Project' not in globals():
            return jsonify({'error': 'Project model not available'}), 500
            
        projects = Project.query.filter_by(user_id=user_id).order_by(desc(Project.created_at)).all()
        return jsonify({
            'projects': [project.to_dict() for project in projects]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get projects: {str(e)}'}), 500

@main.route('/time-logs', methods=['POST'])
@cross_origin()
def log_time():
    try:
        if not all([TimeLog, Project]):
            return jsonify({'error': 'Required models not available'}), 500
            
        data = request.get_json()
        
        time_log = TimeLog(
            user_id=data.get('user_id'),
            project_id=data.get('project_id'),
            description=data.get('description'),
            hours=float(data.get('hours'))
        )
        
        db.session.add(time_log)
        
        # Update project hours
        project = Project.query.get(data.get('project_id'))
        if project:
            project.hours_worked += float(data.get('hours'))
        
        db.session.commit()
        
        return jsonify({
            'message': 'Time logged successfully',
            'time_log': time_log.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Time logging failed: {str(e)}'}), 500

# Analytics Routes
@main.route('/analytics/<int:user_id>', methods=['GET'])
@cross_origin()
def get_analytics(user_id):
    try:
        if not all([Project, ai_service]):
            return jsonify({'error': 'Required services not available'}), 500
            
        # Get earnings summary
        total_earnings = db.session.query(func.sum(Project.budget)).filter_by(
            user_id=user_id, status='completed'
        ).scalar() or 0
        
        total_hours = db.session.query(func.sum(Project.hours_worked)).filter_by(
            user_id=user_id
        ).scalar() or 0
        
        avg_hourly_rate = total_earnings / total_hours if total_hours > 0 else 0
        
        # Get recent projects
        recent_projects = Project.query.filter_by(user_id=user_id).order_by(
            desc(Project.created_at)
        ).limit(5).all()
        
        # AI-powered pricing suggestions
        pricing_suggestion = ai_service.get_pricing_suggestions(
            user_id, total_earnings, total_hours, avg_hourly_rate
        )
        
        return jsonify({
            'summary': {
                'total_earnings': total_earnings,
                'total_hours': total_hours,
                'average_hourly_rate': round(avg_hourly_rate, 2),
                'active_projects': Project.query.filter_by(user_id=user_id, status='active').count()
            },
            'recent_projects': [project.to_dict() for project in recent_projects],
            'pricing_suggestion': pricing_suggestion
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Analytics failed: {str(e)}'}), 500

# Skill Gap Analysis Routes
@main.route('/skill-gaps/<int:user_id>', methods=['GET'])
@cross_origin()
def analyze_skill_gaps(user_id):
    try:
        if not all([User, JobOpportunity, SkillGap, ai_service]):
            return jsonify({'error': 'Required services not available'}), 500
            
        user = User.query.get_or_404(user_id)
        
        # Get missed jobs (low match scores)
        missed_jobs = JobOpportunity.query.filter(
            JobOpportunity.match_score < 30
        ).order_by(desc(JobOpportunity.created_at)).limit(20).all()
        
        # Analyze skill gaps using AI
        skill_gaps = ai_service.analyze_skill_gaps(
            user.get_skills_list(),
            [job.required_skills for job in missed_jobs]
        )
        
        # Store skill gaps
        for gap in skill_gaps:
            existing_gap = SkillGap.query.filter_by(
                user_id=user_id,
                missing_skill=gap['skill']
            ).first()
            
            if existing_gap:
                existing_gap.job_missed_count += 1
                existing_gap.priority_score = gap['priority']
            else:
                skill_gap = SkillGap(
                    user_id=user_id,
                    missing_skill=gap['skill'],
                    learning_resource=gap.get('resource'),
                    priority_score=gap['priority']
                )
                db.session.add(skill_gap)
        
        db.session.commit()
        
        # Get current skill gaps
        current_gaps = SkillGap.query.filter_by(user_id=user_id).order_by(
            desc(SkillGap.priority_score)
        ).all()
        
        return jsonify({
            'skill_gaps': [gap.to_dict() for gap in current_gaps]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Skill gap analysis failed: {str(e)}'}), 500

# Client Communication Routes
@main.route('/communication/suggest', methods=['POST'])
@cross_origin()
def suggest_communication():
    try:
        if not all([ClientCommunication, ai_service]):
            return jsonify({'error': 'Required services not available'}), 500
            
        data = request.get_json()
        user_id = data.get('user_id')
        message_type = data.get('message_type')
        client_message = data.get('client_message', '')
        context = data.get('context', {})
        
        # Generate AI suggestion
        ai_suggestion = ai_service.generate_communication_response(
            message_type, client_message, context
        )
        
        # Store communication
        communication = ClientCommunication(
            user_id=user_id,
            project_id=context.get('project_id'),
            message_type=message_type,
            client_message=client_message,
            ai_suggestion=ai_suggestion
        )
        
        db.session.add(communication)
        db.session.commit()
        
        return jsonify({
            'suggestion': ai_suggestion,
            'communication_id': communication.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Communication suggestion failed: {str(e)}'}), 500