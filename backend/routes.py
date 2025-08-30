# routes.py - Updated with proper session management and fixes
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

# Helper function to check authentication
def require_auth():
    """Check if user is authenticated"""
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])

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

# Authentication Routes - FIXED: Return proper response format for frontend
@main.route('/register', methods=['POST'])
@cross_origin()
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'detail': 'No data provided'}), 400
            
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name', '')
        
        if not email or not password:
            return jsonify({'detail': 'Email and password are required'}), 400
        
        if len(password) < 6:
            return jsonify({'detail': 'Password must be at least 6 characters long'}), 400
            
        if User.query.filter_by(email=email).first():
            return jsonify({'detail': 'Email already registered'}), 400
        
        user = User(
            email=email,
            full_name=full_name,
            skills=data.get('skills', ''),
            experience_level=data.get('experience_level', 'beginner'),
            hourly_rate=data.get('hourly_rate', 0.0)
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'detail': f'Registration failed: {str(e)}'}), 500

@main.route('/login', methods=['POST'])
@cross_origin()
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'detail': 'No data provided'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'detail': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session.permanent = True  # Make session permanent
            
            # Return format expected by frontend
            return jsonify({
                'access_token': f'session_{user.id}',  # Fake token for frontend
                'token_type': 'bearer',
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({'detail': 'Incorrect email or password'}), 401
            
    except Exception as e:
        return jsonify({'detail': f'Login failed: {str(e)}'}), 500

@main.route('/logout', methods=['POST'])
@cross_origin()
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

# FIXED: Add authentication check to all protected routes
@main.route('/jobs/search/<int:user_id>', methods=['POST'])  # Changed to POST to match frontend
@cross_origin()
def search_jobs(user_id):
    try:
        current_user = require_auth()
        if not current_user or current_user.id != user_id:
            return jsonify({'detail': 'Authentication required'}), 401
            
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
        return jsonify({'detail': f'Job search failed: {str(e)}'}), 500

@main.route('/jobs/<int:user_id>', methods=['GET'])
@cross_origin()
def get_jobs(user_id):
    try:
        current_user = require_auth()
        if not current_user or current_user.id != user_id:
            return jsonify({'detail': 'Authentication required'}), 401
            
        # Get jobs with high match scores
        jobs = JobOpportunity.query.filter(
            JobOpportunity.match_score > 50,
            JobOpportunity.is_active == True
        ).order_by(desc(JobOpportunity.match_score)).limit(20).all()
        
        return jsonify({
            'jobs': [job.to_dict() for job in jobs]
        }), 200
        
    except Exception as e:
        return jsonify({'detail': f'Failed to get jobs: {str(e)}'}), 500

# Proposal Routes
@main.route('/proposals/generate', methods=['POST'])
@cross_origin()
def generate_proposal():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        job_id = data.get('job_id')
        
        current_user = require_auth()
        if not current_user or current_user.id != user_id:
            return jsonify({'detail': 'Authentication required'}), 401
        
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
        return jsonify({'detail': f'Proposal generation failed: {str(e)}'}), 500

@main.route('/projects/<int:user_id>', methods=['GET'])
@cross_origin()
def get_user_projects(user_id):
    try:
        current_user = require_auth()
        if not current_user or current_user.id != user_id:
            return jsonify({'detail': 'Authentication required'}), 401
            
        projects = Project.query.filter_by(user_id=user_id).order_by(desc(Project.created_at)).all()
        return jsonify({
            'projects': [project.to_dict() for project in projects]
        }), 200
        
    except Exception as e:
        return jsonify({'detail': f'Failed to get projects: {str(e)}'}), 500

# Analytics Routes
@main.route('/analytics/<int:user_id>', methods=['GET'])
@cross_origin()
def get_analytics(user_id):
    try:
        current_user = require_auth()
        if not current_user or current_user.id != user_id:
            return jsonify({'detail': 'Authentication required'}), 401
            
        # Get earnings summary
        total_earnings = db.session.query(func.sum(Project.budget)).filter_by(
            user_id=user_id, status='completed'
        ).scalar() or 0
        
        total_hours = db.session.query(func.sum(Project.hours_worked)).filter_by(
            user_id=user_id
        ).scalar() or 0
        
        avg_hourly_rate = total_earnings / total_hours if total_hours > 0 else 0
        
        # Get active projects count
        active_projects = Project.query.filter_by(user_id=user_id, status='active').count()
        
        # AI-powered pricing suggestions
        try:
            pricing_suggestion = ai_service.get_pricing_suggestions(
                user_id, total_earnings, total_hours, avg_hourly_rate
            )
        except:
            pricing_suggestion = {
                'recommendation': 'Based on your experience, consider reviewing market rates',
                'target_rate': max(avg_hourly_rate * 1.1, 25),
                'tip': 'Focus on building a strong portfolio to justify higher rates'
            }
        
        return jsonify({
            'summary': {
                'total_earnings': float(total_earnings),
                'total_hours': float(total_hours),
                'average_hourly_rate': round(avg_hourly_rate, 2),
                'active_projects': active_projects
            },
            'pricing_suggestion': pricing_suggestion
        }), 200
        
    except Exception as e:
        return jsonify({'detail': f'Analytics failed: {str(e)}'}), 500

# Skill Gap Analysis Routes
@main.route('/skill-gaps/<int:user_id>', methods=['GET'])
@cross_origin()
def analyze_skill_gaps(user_id):
    try:
        current_user = require_auth()
        if not current_user or current_user.id != user_id:
            return jsonify({'detail': 'Authentication required'}), 401
            
        user = User.query.get_or_404(user_id)
        
        # Get current skill gaps
        current_gaps = SkillGap.query.filter_by(user_id=user_id).order_by(
            desc(SkillGap.priority_score)
        ).all()
        
        return jsonify({
            'skill_gaps': [gap.to_dict() for gap in current_gaps]
        }), 200
        
    except Exception as e:
        return jsonify({'detail': f'Skill gap analysis failed: {str(e)}'}), 500