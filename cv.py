from flask import Blueprint, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from utils import process_cv_file, calculate_context_score, allowed_file
from models import CVAnalysis
from app import db
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

cv_bp = Blueprint('cv', __name__)

@cv_bp.route('/upload', methods=['POST'])
@login_required  # Ensure that the user is logged in before uploading a CV
def upload_cv():
    logging.debug('Entering upload_cv function')

    if 'file' not in request.files:
        logging.debug('No file part in request')
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    job_title = request.form.get('job_title')

    if file.filename == '':
        logging.debug('No selected file')
        return jsonify({"error": "No selected file"}), 400

    if not job_title:
        logging.debug('No job title provided')
        return jsonify({"error": "No job title provided"}), 400

    if file and allowed_file(file.filename, {'pdf', 'docx', 'doc'}):
        # Secure the filename and save the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        logging.debug(f'File saved at: {file_path}')

        # Process the file
        file_name, text, name, designation, experience, education, skills = process_cv_file(file_path, filename)

        if name is None:
            logging.debug('Failed to extract information from CV')
            return jsonify({"error": "Failed to extract information from CV"}), 400

        # Use the provided job title for context score calculation
        combined_text = f"{text} {name} {experience} {skills}"
        context_score = calculate_context_score(job_title, combined_text)
        logging.debug(f'Context score calculated: {context_score}')

        if current_user.is_authenticated:
            cv_analysis = CVAnalysis(
                file_name=file_name,
                context_score=context_score * 100,
                user_id=current_user.id,
                name=name,
                designation=designation,
                experience=experience,
                education=education,
                skills=skills
            )
            db.session.add(cv_analysis)
            db.session.commit()
            logging.debug('CV analysis saved to database')

        # Create JSON response
        response = {
            "file_name": file_name,
            "context_score": context_score * 100,
            "name": name,
            "designation": designation,
            "experience": experience,
            "education": education,
            "skills": skills
        }
        logging.debug('Returning JSON response')
        return jsonify(response), 200

    else:
        logging.debug('Invalid file type')
        return jsonify({"error": "Invalid file type"}), 400