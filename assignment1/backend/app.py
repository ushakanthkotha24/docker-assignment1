from flask import Flask, jsonify, request
from flask_cors import CORS
from config import config
import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Initialize Flask application
app = Flask(__name__)

# Load configuration
config_name = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Enable CORS for frontend communication
CORS(app)

# Database connection helper function
def get_database_connection():
    """Create and return a database connection"""
    try:
        connection = psycopg2.connect(
            user=app.config['DATABASE_USER'],
            password=app.config['DATABASE_PASSWORD'],
            host=app.config['DATABASE_HOST'],
            port=app.config['DATABASE_PORT'],
            database=app.config['DATABASE_NAME']
        )
        return connection
    except psycopg2.OperationalError as error:
        print(f"Error connecting to database: {error}")
        return None

# Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify API is running"""
    return jsonify({
        'status': 'healthy',
        'message': 'Backend API is running'
    }), 200

@app.route('/api/database-status', methods=['GET'])
def database_status():
    """Check database connection status"""
    connection = get_database_connection()
    
    if connection:
        connection.close()
        return jsonify({
            'status': 'connected',
            'message': 'Successfully connected to PostgreSQL database'
        }), 200
    else:
        return jsonify({
            'status': 'disconnected',
            'message': 'Failed to connect to PostgreSQL database'
        }), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Retrieve all users from the database"""
    connection = get_database_connection()
    
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT id, username, email, created_at FROM users ORDER BY id;')
        users = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'data': users if users else []
        }), 200
    except psycopg2.DatabaseError as error:
        return jsonify({'error': f'Database error: {str(error)}'}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user in the database"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'email' not in data:
        return jsonify({
            'error': 'Missing required fields: username and email'
        }), 400
    
    connection = get_database_connection()
    
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute(
            'INSERT INTO users (username, email) VALUES (%s, %s) RETURNING id, username, email, created_at;',
            (data['username'], data['email'])
        )
        new_user = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'message': 'User created successfully',
            'data': {
                'id': new_user[0],
                'username': new_user[1],
                'email': new_user[2],
                'created_at': str(new_user[3])
            }
        }), 201
    except psycopg2.IntegrityError as error:
        connection.rollback()
        cursor.close()
        connection.close()
        return jsonify({
            'error': 'User with this email already exists'
        }), 409
    except psycopg2.DatabaseError as error:
        connection.rollback()
        cursor.close()
        connection.close()
        return jsonify({'error': f'Database error: {str(error)}'}), 500

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Retrieve a specific user by ID"""
    connection = get_database_connection()
    
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT id, username, email, created_at FROM users WHERE id = %s;', (user_id,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if user:
            return jsonify({
                'status': 'success',
                'data': user
            }), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except psycopg2.DatabaseError as error:
        return jsonify({'error': f'Database error: {str(error)}'}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update a user by ID"""
    data = request.get_json()
    
    connection = get_database_connection()
    
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        # Build update query based on provided fields
        updates = []
        values = []
        
        if 'username' in data:
            updates.append('username = %s')
            values.append(data['username'])
        
        if 'email' in data:
            updates.append('email = %s')
            values.append(data['email'])
        
        if not updates:
            return jsonify({'error': 'No fields to update'}), 400
        
        values.append(user_id)
        
        update_query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s RETURNING id, username, email, created_at;"
        cursor.execute(update_query, values)
        updated_user = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        
        if updated_user:
            return jsonify({
                'status': 'success',
                'message': 'User updated successfully',
                'data': {
                    'id': updated_user[0],
                    'username': updated_user[1],
                    'email': updated_user[2],
                    'created_at': str(updated_user[3])
                }
            }), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except psycopg2.IntegrityError as error:
        connection.rollback()
        cursor.close()
        connection.close()
        return jsonify({'error': 'Email already exists'}), 409
    except psycopg2.DatabaseError as error:
        connection.rollback()
        cursor.close()
        connection.close()
        return jsonify({'error': f'Database error: {str(error)}'}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user by ID"""
    connection = get_database_connection()
    
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM users WHERE id = %s RETURNING id;', (user_id,))
        deleted_user = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        
        if deleted_user:
            return jsonify({
                'status': 'success',
                'message': 'User deleted successfully'
            }), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except psycopg2.DatabaseError as error:
        connection.rollback()
        cursor.close()
        connection.close()
        return jsonify({'error': f'Database error: {str(error)}'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print('Starting Python Flask Application')
    print(f'Environment: {config_name}')
    print(f'Database Host: {app.config["DATABASE_HOST"]}')
    app.run(host='0.0.0.0', port=5000, debug=True)
