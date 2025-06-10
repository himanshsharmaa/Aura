import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from auth.auth_service import AuthService
from auth.user_manager import UserManager
from training.training_manager import TrainingManager

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize services
auth_service = AuthService()
user_manager = UserManager()
training_manager = TrainingManager()

@app.route('/')
def index():
    """Home page"""
    if 'email' not in session:
        return render_template('index.html')
    
    user = user_manager.get_user(session['email'])
    if not user:
        session.clear()
        return redirect(url_for('index'))
    
    return render_template('dashboard.html', user=user)

@app.route('/auth/<provider>')
def auth(provider):
    """Start OAuth flow"""
    auth_url = auth_service.get_auth_url(provider)
    if not auth_url:
        return "Invalid provider", 400
    return redirect(auth_url)

@app.route('/auth/<provider>/callback')
def auth_callback(provider):
    """Handle OAuth callback"""
    code = request.args.get('code')
    if not code:
        return "No code provided", 400
    
    success, result = auth_service.handle_callback(provider, code)
    if not success:
        return result, 400
    
    session['email'] = result['email']
    session['name'] = result['name']
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Logout user"""
    if 'email' in session:
        auth_service.logout(session['email'])
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/models')
def get_models():
    """Get user's models"""
    if 'email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    models = training_manager.get_user_models(session['email'])
    return jsonify(models)

@app.route('/api/models/train', methods=['POST'])
def train_model():
    """Train a new model"""
    if 'email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    model_type = data.get('type')
    samples = data.get('samples', [])
    
    if not model_type or not samples:
        return jsonify({'error': 'Missing required fields'}), 400
    
    success, result = training_manager.train_model(
        session['email'],
        model_type,
        samples,
        data.get('params', {})
    )
    
    if not success:
        return jsonify({'error': result}), 400
    
    return jsonify(result)

@app.route('/api/models/<model_id>', methods=['DELETE'])
def delete_model(model_id):
    """Delete a model"""
    if 'email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    success = training_manager.delete_model(session['email'], model_id)
    if not success:
        return jsonify({'error': 'Failed to delete model'}), 400
    
    return jsonify({'success': True})

@app.route('/api/samples/collect', methods=['POST'])
def collect_samples():
    """Start collecting samples"""
    if 'email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    sample_type = data.get('type')
    
    if not sample_type:
        return jsonify({'error': 'Missing sample type'}), 400
    
    success = user_manager.start_collecting_samples(
        session['email'],
        sample_type
    )
    
    if not success:
        return jsonify({'error': 'Failed to start collection'}), 400
    
    return jsonify({'success': True})

@app.route('/api/samples/stop', methods=['POST'])
def stop_collecting_samples():
    """Stop collecting samples"""
    if 'email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    success = user_manager.stop_collecting_samples(session['email'])
    if not success:
        return jsonify({'error': 'Failed to stop collection'}), 400
    
    return jsonify({'success': True})

@app.route('/api/samples')
def get_samples():
    """Get user's samples"""
    if 'email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    samples = user_manager.get_samples(session['email'])
    return jsonify(samples)

if __name__ == '__main__':
    app.run(debug=True, port=8000) 