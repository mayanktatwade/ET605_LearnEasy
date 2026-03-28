"""
Flask backend for GIFT Linear Equations Tutor
Stores session data in SQLite database
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os

app = Flask(__name__)

# ==================== DATABASE CONFIG ====================
# SQLite database (stored in instance folder for free hosting)
basedir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(basedir, 'instance')
if not os.path.exists(instance_dir):
    os.makedirs(instance_dir)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_dir, "tutor.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Enable CORS for frontend requests
CORS(app)

# ==================== DATABASE MODELS ====================
class Session(db.Model):
    """Stores each student tutoring session"""
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(100), nullable=False, index=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    chapter_id = db.Column(db.String(100), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    timestamp = db.Column(db.String(50), nullable=False)  # ISO format from frontend
    
    # Session Status
    session_status = db.Column(db.String(20), default='completed')  # completed, exited_early
    
    # Performance Metrics
    correct_answers = db.Column(db.Integer, default=0)
    wrong_answers = db.Column(db.Integer, default=0)
    questions_attempted = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    retry_count = db.Column(db.Integer, default=0)
    hints_used = db.Column(db.Integer, default=0)
    total_hints_embedded = db.Column(db.Integer, default=0)
    time_spent_seconds = db.Column(db.Integer, default=0)
    topic_completion_ratio = db.Column(db.Float, default=0.0)
    
    # JSON storage for detailed subtopic progress
    subtopic_progress_json = db.Column(db.Text)
    
    # Full payload backup
    full_payload_json = db.Column(db.Text)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'session_id': self.session_id,
            'chapter_id': self.chapter_id,
            'created_at': self.created_at.isoformat(),
            'session_status': self.session_status,
            'correct_answers': self.correct_answers,
            'wrong_answers': self.wrong_answers,
            'questions_attempted': self.questions_attempted,
            'total_questions': self.total_questions,
            'retry_count': self.retry_count,
            'hints_used': self.hints_used,
            'time_spent_seconds': self.time_spent_seconds,
            'topic_completion_ratio': self.topic_completion_ratio,
            'accuracy': round((self.correct_answers / max(self.correct_answers + self.wrong_answers, 1)) * 100)
        }

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Serve the main tutoring application UI"""
    html_file = os.path.join(basedir, 'ET605_Linear_Equations_BACKEND_READY.html')
    if not os.path.exists(html_file):
        files = os.listdir(basedir)
        return jsonify({'error': 'HTML file not found', 'looking_for': html_file, 'files_available': files}), 404
    return send_file(html_file, mimetype='text/html')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'GIFT Tutor Backend is running'}), 200

@app.route('/api/submit-session', methods=['POST'])
def submit_session():
    """
    Endpoint to receive tutoring session data from frontend
    Expected JSON payload from frontend's buildReport()
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['student_id', 'session_id', 'chapter_id', 'timestamp']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create new session record
        session = Session(
            student_id=data['student_id'],
            session_id=data['session_id'],
            chapter_id=data['chapter_id'],
            timestamp=data['timestamp'],
            session_status=data.get('session_status', 'completed'),
            correct_answers=data.get('correct_answers', 0),
            wrong_answers=data.get('wrong_answers', 0),
            questions_attempted=data.get('questions_attempted', 0),
            total_questions=data.get('total_questions', 0),
            retry_count=data.get('retry_count', 0),
            hints_used=data.get('hints_used', 0),
            total_hints_embedded=data.get('total_hints_embedded', 0),
            time_spent_seconds=data.get('time_spent_seconds', 0),
            topic_completion_ratio=data.get('topic_completion_ratio', 0.0),
            subtopic_progress_json=json.dumps(data.get('subtopic_progress', [])),
            full_payload_json=json.dumps(data)
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Session saved successfully',
            'session_id': session.session_id,
            'db_id': session.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/student/<student_id>/sessions', methods=['GET'])
def get_student_sessions(student_id):
    """Retrieve all sessions for a specific student"""
    try:
        sessions = Session.query.filter_by(student_id=student_id).order_by(Session.created_at.desc()).all()
        return jsonify({
            'student_id': student_id,
            'total_sessions': len(sessions),
            'sessions': [s.to_dict() for s in sessions]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session_detail(session_id):
    """Retrieve detailed data for a specific session"""
    try:
        session = Session.query.filter_by(session_id=session_id).first()
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Parse JSON fields
        result = session.to_dict()
        result['subtopic_progress'] = json.loads(session.subtopic_progress_json) if session.subtopic_progress_json else []
        result['full_payload'] = json.loads(session.full_payload_json) if session.full_payload_json else {}
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Global statistics across all sessions"""
    try:
        total_sessions = Session.query.count()
        total_students = db.session.query(db.func.count(db.distinct(Session.student_id))).scalar()
        avg_accuracy = db.session.query(
            db.func.round(
                db.func.avg(
                    (Session.correct_answers * 100.0) / 
                    db.func.greatest(Session.correct_answers + Session.wrong_answers, 1)
                ), 2
            )
        ).scalar() or 0
        
        total_hints = db.session.query(db.func.sum(Session.hints_used)).scalar() or 0
        avg_time = db.session.query(db.func.avg(Session.time_spent_seconds)).scalar() or 0
        
        return jsonify({
            'total_sessions': total_sessions,
            'unique_students': total_students,
            'average_accuracy': float(avg_accuracy),
            'total_hints_used': int(total_hints),
            'average_time_seconds': float(avg_time)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export all sessions as CSV"""
    try:
        import csv
        from io import StringIO
        
        sessions = Session.query.all()
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Session ID', 'Student ID', 'Chapter ID', 'Date Created',
            'Correct', 'Wrong', 'Accuracy %', 'Time (min)',
            'Hints Used', 'Completion %', 'Status'
        ])
        
        # Rows
        for s in sessions:
            accuracy = (s.correct_answers / max(s.correct_answers + s.wrong_answers, 1)) * 100
            minutes = s.time_spent_seconds / 60
            completion = s.topic_completion_ratio * 100
            
            writer.writerow([
                s.session_id,
                s.student_id,
                s.chapter_id,
                s.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                s.correct_answers,
                s.wrong_answers,
                f'{accuracy:.1f}%',
                f'{minutes:.1f}',
                s.hints_used,
                f'{completion:.1f}%',
                s.session_status
            ])
        
        output.seek(0)
        return output.getvalue(), 200, {
            'Content-Disposition': 'attachment; filename=tutor_sessions.csv',
            'Content-Type': 'text/csv'
        }
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== DATABASE INITIALIZATION ====================

def init_db():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()
        print("✓ Database initialized successfully")

if __name__ == '__main__':
    init_db()
    # For production, use a proper WSGI server (Gunicorn)
    app.run(debug=True, host='0.0.0.0', port=5000)
