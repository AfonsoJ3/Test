from flask import Blueprint as bl, render_template, request, jsonify, flash, session, redirect, url_for
from datetime import datetime, timedelta

views = bl('views', __name__)

def is_authenticated():
    """Check if user is authenticated"""
    return session.get('authenticated', False)
 
@views.route('/')
def index():
    # Root route - redirect to login if not authenticated, home if authenticated
    if not is_authenticated():
        return redirect(url_for('auth.login'))
    else:
        return redirect(url_for('views.home'))

@views.route('/home', methods=['GET', 'POST'])
def home():
    # Check if user is authenticated, if not redirect to login
    if not is_authenticated():
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        # Get form data
        origin = request.form.get('origin')
        destination = request.form.get('destination')
        departure_date = request.form.get('departureDate')
        return_date = request.form.get('returnDate')
        
        print(f"DEBUG: Form data - origin: {origin}, destination: {destination}, dep: {departure_date}, ret: {return_date}")
        
        # Basic validation
        if not origin or not origin.strip():
            flash('Please enter an origin city', 'error')
            return render_template("home.html")
        
        if not destination or not destination.strip():
            flash('Please enter a destination city', 'error')
            return render_template("home.html")
        
        if not departure_date:
            flash('Please select a departure date', 'error')
            return render_template("home.html")
        
        if not return_date:
            flash('Please select a return date', 'error')
            return render_template("home.html")
        
        # Validate dates
        try:
            dep_date = datetime.strptime(departure_date, '%Y-%m-%d')
            ret_date = datetime.strptime(return_date, '%Y-%m-%d')
            
            if dep_date < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                flash('Departure date cannot be in the past', 'error')
                return render_template("home.html", 
                                     origin=origin, destination=destination,
                                     departure_date=departure_date, return_date=return_date)
            
            if ret_date <= dep_date:
                flash('Return date must be after departure date', 'error')
                return render_template("home.html", 
                                     origin=origin, destination=destination,
                                     departure_date=departure_date, return_date=return_date)
                
        except ValueError:
            flash('Invalid date format', 'error')
            return render_template("home.html", 
                                 origin=origin, destination=destination,
                                 departure_date=departure_date, return_date=return_date)
        
        # Calculate trip duration
        trip_duration = (ret_date - dep_date).days
        
        # Generate sample itinerary (placeholder for AI integration)
        itinerary = generate_sample_itinerary(origin, destination, dep_date, ret_date, trip_duration)
        
        print(f"DEBUG: Generated itinerary with {len(itinerary)} items")
        
        # Return success result
        flash(f'Perfect! Your itinerary from {origin} to {destination} is ready!', 'success')
        return render_template("home.html", 
                             itinerary=itinerary,
                             origin=origin,
                             destination=destination,
                             departure_date=departure_date,
                             return_date=return_date)
    
    return render_template("home.html")

def generate_sample_itinerary(origin, destination, dep_date, ret_date, duration):
    """
    Generate a sample itinerary. This will be replaced with AI integration later.
    """
    activities_templates = [
        "Explore the historic downtown area and visit local landmarks",
        "Take a guided city tour and visit museums",
        "Enjoy outdoor activities and natural attractions", 
        "Experience local culture and cuisine",
        "Shopping and leisure activities",
        "Visit famous attractions and photo spots",
        "Relaxation and spa activities",
        "Adventure sports and outdoor excursions",
        "Cultural workshops and local experiences",
        "Sunset viewing and evening entertainment"
    ]
    
    itinerary = []
    
    for day in range(duration + 1):
        current_date = dep_date + timedelta(days=day)
        
        if day == 0:
            # Arrival day
            activity = f"Arrive in {destination} from {origin}. Check into accommodation and explore nearby areas. Welcome dinner at a local restaurant."
        elif day == duration:
            # Departure day
            activity = f"Check out and departure back to {origin}. Last-minute shopping and sightseeing if time permits."
        else:
            # Regular days
            activity = f"Full day in {destination}. " + activities_templates[day % len(activities_templates)]
        
        itinerary.append({
            'day': f'Day {day + 1}',
            'date': current_date.strftime('%B %d, %Y'),
            'activities': activity
        })
    
    return itinerary