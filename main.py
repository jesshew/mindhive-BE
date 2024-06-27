from flask import Flask, jsonify,request
from app.models import Outlet, OpeningHours, db
from app.dummy import dummy_data
from app.scraper import scrape_subway_outlets,add_outlets_to_database
from app.geocode import geocode_all_outlets
from app.chat_query import write_json_file,perform_llm_query
from flask_cors import CORS
from flask import send_from_directory
import os


# Initialize Flask application instance
app = Flask(__name__)

# Configure SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../subway_kl_outlets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app) #temporary

# Initialize SQLAlchemy with the Flask application context
db.init_app(app)

# Register the blueprint containing API routes
# app.register_blueprint(api_bp)

# Function to add dummy data 
def add_dummydata():
     # Ensure the database tables are created
    with app.app_context():
        db.create_all()

        # Add dummy data to the database
        for data in dummy_data:
            new_outlet = Outlet(
                name=data['name'],
                address=data['address'],
                waze_link=data['waze_link']
            )
            db.session.add(new_outlet)
            db.session.commit()

            ## Add OpeningHours if hours exist
            if data['hours'] != "Hours not available":
                # Split multiple opening times separated by ;
                opening_times = data['hours'].split('; ')

                for opening_time in opening_times:
                    new_hours = OpeningHours(
                        description=opening_time,
                        outlet_id=new_outlet.id
                    )
                    db.session.add(new_hours)
                    db.session.commit()

# Function to clear the database
def clear_database():
    try:
        with app.app_context():
            db.session.query(OpeningHours).delete()
            db.session.query(Outlet).delete()
            db.session.commit()
        print("Database cleared successfully.")
    except Exception as e:
        print(f"Failed to clear database: {str(e)}")
        raise

@app.route('/clear-db', methods=['DELETE'])
def clear_database_route():
    try:
        clear_database()
        return jsonify({'message': 'Database cleared successfully'}), 200
    except Exception as e:
        return jsonify({'message': f"Failed to clear database: {str(e)}"}), 500


@app.route('/outlets', methods=['GET'])
def get_outlets():
    outlets = Outlet.query.all()
    result = []
    for outlet in outlets:
        outlet_data = {
            'id': outlet.id,
            'name': outlet.name,
            'address': outlet.address,
            'waze_link': outlet.waze_link,
            'latitude':outlet.latitude,
            'longitude':outlet.longitude,
            'opening_hours': [oh.description for oh in outlet.opening_hours]
        }
        result.append(outlet_data)
    return jsonify(result)

@app.route('/outlet/<int:id>', methods=['GET'])
def get_outlet(id):
    outlet = Outlet.query.get(id)
    if not outlet:
        return jsonify({'message': 'Outlet not found'}), 404
    
    outlet_data = {
        'id': outlet.id,
        'name': outlet.name,
        'address': outlet.address,
        'waze_link': outlet.waze_link,
        'latitude':outlet.latitude,
        'longitude':outlet.longitude,
        'opening_hours': [oh.description for oh in outlet.opening_hours]
    }
    
    return jsonify(outlet_data)

# API route to add dummy data
@app.route('/add-dummy-data', methods=['POST'])
def add_dummy_data_route():
    try:
        add_dummydata()
        return jsonify({'message': 'Dummy data added successfully'}), 200
    except Exception as e:
        return jsonify({'message': f"Failed to add dummy data: {str(e)}"}), 500
    
# route to perform LLM query
@app.route('/llm-query', methods=['POST'])
def llm_query():
    try:
        query = request.json.get('query')  # Assuming JSON body with 'query' key
        if not query:
            return jsonify({'message': 'Query parameter is required'}), 400
        
        response = perform_llm_query(query)
 
        return jsonify({'response': response}), 200
    
    except Exception as e:
        return jsonify({'message': f"Failed to perform LLM query: {str(e)}"}), 500

@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    with app.app_context():
        # Ensure the database tables are created
        db.create_all()

        # Clear existing data in the database (optional)
        clear_database()

        # Define URL and location for scraping
        url = "https://subway.com.my/find-a-subway"
        location = "kuala lumpur"

        # Call scrape_subway_outlets function to scrape data
        scraped_data = scrape_subway_outlets(url, location)
        print("Subway outlets scraping completed")
        print("Geocoding outlets...")
        # geocoded_outlets = scraped_data
        geocoded_outlets = geocode_all_outlets(scraped_data)
        print("Geocoding of outlets completed")

        # Add scraped outlets to the database
        add_outlets_to_database(geocoded_outlets)
        print("Subway outlets data added to the database.")
        write_json_file({"outlets":geocoded_outlets})
        # write_to_txt(geocoded_outlets)
        #print(geocoded_outlets)

    # Only run the Flask application if executed directly, not as part of the Flask server
    app.run(use_reloader=False)
