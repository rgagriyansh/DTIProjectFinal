from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import mysql.connector
from flask import jsonify



app = Flask(__name__)

db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="admin",
    database="project"
)
cursor = db.cursor()

app.secret_key = 'your_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



#######################USER MODEL #####################
class User(UserMixin):
    def __init__(self, id, name, email, user_type):
        self.id = id
        self.name = name
        self.email = email
        self.user_type = user_type 

@login_manager.user_loader
def load_user(user_id):
    cursor.execute("SELECT * FROM users WHERE users.id = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        return User(id=user[0], name=user[1], email=user[2], user_type='creator')

    cursor.execute("SELECT * FROM brands WHERE id = %s", (user_id,))
    brand = cursor.fetchone()
    if brand:
        return User(id=brand[0], name=brand[1], email=brand[2], user_type='brand')

    return None

@app.route('/')
def index():
    return render_template('index.html', logged_in=current_user.is_authenticated, user_type=getattr(current_user, 'user_type', None))



@app.route('/creator', methods=['GET'])
def show_creator():
    return render_template('creator.html')

@app.route('/creator', methods=['POST'])
def creator_action():
    action = request.form.get('action')

    if action == 'signup':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        category = request.form.get('category')
        social_handle = request.form.get('social_handle')

        query = "INSERT INTO users (name, email, password, category, social_handle) VALUES (%s, %s, %s, %s, %s)"
        values = (name, email, password, category, social_handle)
        cursor.execute(query, values)
        db.commit()

        return redirect(url_for('index'))

    elif action == 'login':
        email = request.form.get('email')
        password = request.form.get('password') 

        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()

        if user:
            user_obj = User(id=user[0], name=user[1], email=user[2], user_type='creator')
            login_user(user_obj)
            print(f"Logged in as a creator: {user_obj.name}")
            return redirect(url_for('index'))
        else:
            pass

    return 'Invalid action', 400



###########################################################
@app.route('/dashboard')
@login_required
def dashboard():
    user_details = {}
    if current_user.user_type == 'creator':
        cursor.execute("SELECT bio, social_media FROM influencers WHERE id = %s", (str(current_user.id),))
        profile_data = cursor.fetchone()

        if profile_data:
            profile = {'bio': profile_data[0], 'social_media': profile_data[1]}
            user_details = {'name': current_user.name, 'email': current_user.email}
            return render_template('profile_display.html', profile=profile, user=user_details)
        else:
            return redirect(url_for('profile_creation'))
    else:
        cursor.execute("SELECT name, email, bio FROM brands WHERE id = %s", (str(current_user.id),))
        brand_info = cursor.fetchone()

        if brand_info:
            brand_details = {
                'name': brand_info[0],
                'email': brand_info[1],
                'bio': brand_info[2],
            }
            return render_template('brand_dashboard.html', brand_details=brand_details)
        else:
            print("Error")
            pass

##################################################################################
@app.route('/profile_creation', methods=['GET', 'POST'])
@login_required
def profile_creation():
    if request.method == 'POST':
        bio = request.form.get('bio')
        social_media = request.form.get('social-media')
        location = request.form.get('location')
        categories = request.form.getlist('category[]')
        age = request.form.get('age')
        gender = request.form.get('gender')
        followers = request.form.get('followers')
        engagement_rate = request.form.get('engagement-rate')
        average_likes = request.form.get('average-likes')
        average_comments = request.form.get('average-comments')
        contact_preference = request.form.get('contact-preference')
        preferred_brands = request.form.get('preferred-brands')
        
        categories_str = ','.join(categories)
        
        query = """
        INSERT INTO influencers (id, bio, social_media, location, categories, age, gender, followers, engagement_rate, average_likes, average_comments, contact_preference, preferred_brands)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE bio=%s, social_media=%s, location=%s, categories=%s, age=%s, gender=%s, followers=%s, engagement_rate=%s, average_likes=%s, average_comments=%s, contact_preference=%s, preferred_brands=%s
        """
        
        values = (current_user.id, bio, social_media, location, categories_str, age, gender, followers, engagement_rate, average_likes, average_comments, contact_preference, preferred_brands,
                  bio, social_media, location, categories_str, age, gender, followers, engagement_rate, average_likes, average_comments, contact_preference, preferred_brands)
        
        cursor.execute(query, values)
        db.commit()
        
        return redirect(url_for('dashboard'))
    else:
        return render_template('influncers.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
######################### CREATORS PROFILE UPDATE ############################################
@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    bio = request.form.get('bio')
    social_media = request.form.get('social_media')
    
    cursor.execute("UPDATE influencers SET bio = %s, social_media = %s WHERE id = %s", (bio, social_media, current_user.id))
    db.commit()
    
    return redirect(url_for('dashboard'))


#################################
@app.route('/brand', methods=['GET'])
def show_brand():
    return render_template("brand.html")
@app.route('/brand', methods=['POST'])
def brand_action():
    action = request.form.get('action')

    if action == 'brand_signup':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password') 
        category = request.form.get('category')
        social_handle = request.form.get('social_handle')

        query = "INSERT INTO brands (id, name, email, password, category, social_handle) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (None, name, email, password, category, social_handle)  
        cursor.execute(query, values)
        db.commit()

        user_obj = User(id=cursor.lastrowid, name=name, email=email, user_type='brand')
        login_user(user_obj)

        return redirect(url_for('index'))

    elif action == 'brand_login':
        email = request.form.get('email')
        password = request.form.get('password')

        cursor.execute("SELECT * FROM brands WHERE email = %s AND password = %s", (email, password))
        brand = cursor.fetchone()

        if brand:
            brand_obj = User(id=brand[0], name=brand[1], email=brand[2], user_type='brand')
            login_user(brand_obj)
            print(f"User type: {brand_obj.user_type}") 

            print(f"Logged in as a brand: {brand_obj.name}")
            return redirect(url_for('index'))
        else:
            pass

    return 'Action not recognized', 400


##############################################################CAMPAIGNS#######################
@app.route('/create_campaign', methods=['GET', 'POST'])
@login_required
def create_campaign():
    if request.method == 'POST':
        title = request.form.get('title')
        categories = ','.join(request.form.getlist('category[]'))
        categoriess = categories
        age_ranges = ','.join(request.form.getlist('age_range[]'))
        location = request.form.get('location')
        gender = request.form.get('gender')
        payment_option = request.form.get('payment_option')
        description = request.form.get('description')
        followers = request.form.get('followers')
        engagement_rate = request.form.get('engagement_rate')
        average_likes = request.form.get('average_likes')
        average_comments = request.form.get('average_comments')

        query = """
        INSERT INTO campaigns (id,title, category, age_range, gender, payment_option, description,location,categories, followers,engagement_rate,average_likes,average_comments)
        VALUES (%s, %s, %s, %s, %s, %s, %s , %s, %s, %s , %s, %s, %s)
        """
        values = (current_user.id, title, categories, age_ranges, gender, payment_option, description,location,categoriess , followers,engagement_rate,average_likes,average_comments)
        cursor.execute(query, values)
        db.commit()

        return redirect(url_for('dashboard'))
    else:
        return render_template('campaigncreate.html')

@app.route('/campaigns')
@login_required
def campaigns():
    cursor.execute("SELECT * FROM campaigns")
    campaigns = cursor.fetchall()
    campaigns_dicts = [
    {'id': c[0], 'brand_id': c[1], 'title': c[2], 'category': c[3], 'age_range': c[4], 'gender': c[5], 'payment_option': c[6], 'description': c[7], 'CID': c[8]}
    for c in campaigns
]
    return render_template('campaigns.html', campaigns=campaigns_dicts)


#################################### SEE CAMPAIGNS ###################################
@app.route('/my_campaigns')
@login_required
def my_campaigns():
    brand_id = current_user.id
    cursor.execute("SELECT * FROM Campaigns WHERE id = %s", (brand_id,))
    campaigns = cursor.fetchall()

    campaigns_dicts = [
        {'id': campaign[0], 'brand_id': campaign[1], 'title': campaign[2], 'category': campaign[3], 'age_range': campaign[4], 'gender': campaign[5], 'payment_option': campaign[6], 'description': campaign[7], 'CID': campaign[8], 'location':campaign[9], 'followers': campaign[11], 'engagement_rate':campaign[12],'average_likes': campaign[13],'average_comments':campaign[14] }
        for campaign in campaigns
    ]

    return render_template('my_campaigns.html', campaigns=campaigns_dicts)
#############################################################################
@app.route('/edit_campaign/<int:CID>', methods=['GET', 'POST'])
@login_required
def edit_campaign(CID):
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        age_range = request.form.get('age_range')
        gender = request.form.get('gender')
        payment_option = request.form.get('payment_option')
        description = request.form.get('description')

        query = """
        UPDATE campaigns
        SET title = %s, category = %s, age_range = %s, gender = %s, payment_option = %s, description = %s
        WHERE CID = %s
        """
        cursor.execute(query, (title, category, age_range, gender, payment_option, description, CID))
        db.commit()
        
        return redirect(url_for('my_campaigns'))
    else:
        cursor.execute("SELECT * FROM campaigns WHERE CID = %s", (CID,))
        campaign = cursor.fetchone()
        
        campaign_dict = {
            'id': campaign[0],
            'brand_id': campaign[1],
            'title': campaign[2],
            'category': campaign[3],
            'age_range': campaign[4],
            'gender': campaign[5],
            'payment_option': campaign[6],
            'description': campaign[7],
            'CID': campaign[8]
        }
        
        return render_template('edit_campaign.html', campaign=campaign_dict)

################################## APPLY CAMPAIGNS ###################
@app.route('/apply_campaign', methods=['GET','POST'])
@login_required
def apply_campaign():
    if current_user.user_type != 'creator':
        return 'Unauthorized', 403
    campaign_id = request.form['campaign_id']
    creator_id = current_user.id

    status = 'Pending'

    query = """
    INSERT INTO applications (campaign_id, creator_id, status) VALUES (%s, %s, %s)
    """
    cursor.execute(query, (campaign_id, creator_id, status))
    db.commit()
    return jsonify({"message": "Successfully Applied"})
##################################################################
@app.route('/view_applications')
@login_required
def view_applications():
    if current_user.user_type != 'brand' or current_user.id < 5000:
        return 'Unauthorized', 403
    
    query = """
    SELECT a.application_id, a.campaign_id, a.creator_id, a.status, c.title AS campaign_title, c.category AS campaign_category, c.age_range AS campaign_age_range, c.gender AS campaign_gender, c.payment_option AS campaign_payment_option, c.description AS campaign_description, u.name AS creator_name, i.followers AS creator_followers, i.categories AS creator_categories, i.bio AS creator_bio , i.age as creator_age
    FROM applications a
    JOIN campaigns c ON a.campaign_id = c.CID
    JOIN influencers i ON a.creator_id = i.id
    JOIN users u ON a.creator_id = u.id
    WHERE c.id = %s;
    """
    cursor.execute(query, (current_user.id,))
    applications = cursor.fetchall()
    
    applications_data = [{
        'application_id': app[0],
        'campaign_id': app[1],
        'creator_id': app[2],
        'status': app[3],
        'campaign_title': app[4],
        'campaign_category': app[5],
        'campaign_age_range': app[6],
        'campaign_gender': app[7],
        'campaign_payment_option': app[8],
        'campaign_description': app[9],
        'creator_name': app[10],
        'creator_followers': app[11],
        'creator_categories': app[12],
        'creator_bio': app[13],
        'creator_age': app[14]
    } for app in applications]

    
    return render_template('applications.html', applications=applications_data)

@app.route('/campaign_applications/<int:campaign_id>')
@login_required
def view_campaign_applications(campaign_id):
    if current_user.user_type != 'brand':
        return 'Unauthorized', 403
    cursor.execute("SELECT title, category, age_range, gender, location FROM campaigns WHERE CID = %s", (campaign_id,))
    campaign = cursor.fetchone()
    campaign_details = {'title': campaign[0], 'category': campaign[1].split(','), 'age_range': campaign[2], 'gender': campaign[3], 'location': campaign[4]}

    cursor.execute("""
    SELECT a.application_id, a.creator_id, a.status, u.name AS creator_name, i.followers AS creator_followers, i.categories AS creator_categories, i.bio AS creator_bio, i.age, i.location
    FROM applications a
    JOIN influencers i ON a.creator_id = i.id
    JOIN users u ON a.creator_id = u.id
    WHERE a.campaign_id = %s
    """, (campaign_id,))
    applications = cursor.fetchall()

    applications_data = []
    for app in applications:
        criteria_report = {}
        creator_categories = app[5].split(',')
        creator_details = {
            'age': app[7],
            'location': app[8],
            'category': creator_categories
        
        }
        
        
        match_percentage = calculate_match_percentage(creator_details, campaign_details)
        applications_data.append({
            'application_id': app[0],
            'creator_id': app[1],
            'status': app[2],
            'creator_name': app[3],
            'creator_followers': app[4],
            'creator_categories': creator_categories, 
            'campaign_categories': campaign_details['category'],
            'creator_bio': app[6],
            'match_percentage': int(match_percentage),
        })

    return render_template('view_campaign_applications.html', applications=applications_data, campaign_id=campaign_id)

#######################################################
def calculate_match_percentage(creator, campaign):
    total_criteria = 8
    matched_criteria = 0
    criteria_report = {}

    creator_category = creator.get('category', [])
    if isinstance(creator_category, str):
        creator_category = creator_category.split(',')

    if isinstance(campaign.get('category', ''), list):
        campaign_category = campaign.get('category', [])
    else:
        campaign_category = campaign.get('category', '').split(',')

    campaign_age_range = campaign.get('age_range', '0-0').split('-')
    creator_age = creator.get('age', 0)
    if int(campaign_age_range[0]) <= creator_age <= int(campaign_age_range[1]):
        matched_criteria += 1
        criteria_report['age'] = 'Accepted'
    else:
        criteria_report['age'] = 'Rejected'

    if creator.get('location', '') == campaign.get('location', ''):
        matched_criteria += 1
        criteria_report['location'] = 'Accepted'
    else:
        criteria_report['location'] = 'Rejected'

    if any(item in creator_category for item in campaign_category):
        matched_criteria += 1
        criteria_report['category'] = 'Accepted'
    else:
        criteria_report['category'] = 'Rejected'

    if creator.get('gender', '') == campaign.get('gender', ''):
        matched_criteria += 1
        criteria_report['gender'] = 'Accepted'
    else:
        criteria_report['gender'] = 'Rejected'

    creator_followers = int(creator.get('followers', 0))
    campaign_min_followers = int(campaign.get('min_followers', 0))
    if creator_followers >= campaign_min_followers:
        matched_criteria += 1
        criteria_report['followers'] = 'Accepted'
    else:
        criteria_report['followers'] = 'Rejected'

    creator_engagement_rate = int(creator.get('engagement_rate', 0))
    campaign_min_engagement_rate = int(campaign.get('min_engagement_rate', 0))
    if creator_engagement_rate >= campaign_min_engagement_rate:
        matched_criteria += 1
        criteria_report['engagement_rate'] = 'Accepted'
    else:
        criteria_report['engagement_rate'] = 'Rejected'

    creator_avg_likes = int(creator.get('average_likes', 0))
    campaign_min_avg_likes = int(campaign.get('min_average_likes', 0))
    if creator_avg_likes >= campaign_min_avg_likes:
        matched_criteria += 1
        criteria_report['average_likes'] = 'Accepted'
    else:
        criteria_report['average_likes'] = 'Rejected'

    creator_avg_comments = int(creator.get('average_comments', 0))
    campaign_min_avg_comments = int(campaign.get('min_average_comments', 0))
    if creator_avg_comments >= campaign_min_avg_comments:
        matched_criteria += 1
        criteria_report['average_comments'] = 'Accepted'
    else:
        criteria_report['average_comments'] = 'Rejected'
    match_percentage = (matched_criteria / total_criteria) * 100


    
    return match_percentage

if __name__ == '__main__':
    app.run(debug=True)
