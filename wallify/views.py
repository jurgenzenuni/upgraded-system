from django.shortcuts import render, redirect
from django.db import connection
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth import logout
import boto3
from django.conf import settings
import os
from django.http import JsonResponse
import replicate
from dotenv import load_dotenv

def generate_image(request):
    
    username = request.session.get('username')
    # Set a default profile picture URL
    profile_picture_url = '/static/images/default-profile-image2.png'

    if username:
        profile_picture_url = f'/profile-picture/{username}'
    # Load environment variables from .env file
    load_dotenv()
    # Retrieve the API token
    api_token = os.getenv('REPLICATE_API_TOKEN')
    
    image_url = None

    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        if not prompt:
            return JsonResponse({'error': 'No prompt provided'}, status=400)

        try:
            # Run the model using the Replicate API
            output = replicate.run(
                "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
                input={"prompt": prompt}
            )
            image_url = output[0]
        except replicate.exceptions.ReplicateError as e:
            # Return the Replicate error details
            error_details = str(e)
            print(f"Error generating image: {error_details}")  # Debugging line
            return JsonResponse({'error': error_details}, status=500)
        except Exception as e:
            # Catch any other unexpected errors
            print(f"Unexpected error: {e}")  # Debugging line
            return JsonResponse({'error': 'Unexpected error occurred'}, status=500)

    # Render the template with the image URL if available
    return render(request, 'generate_image.html', {'image_url': image_url, 'username': username, 'profile_picture_url': profile_picture_url})
# def generate_image(request):
#     username = request.session.get('username')
#     # Set a default profile picture URL
#     profile_picture_url = '/static/images/default-profile-image2.png'

#     if username:
#         profile_picture_url = f'/profile-picture/{username}'
    
#     # Load environment variables from .env file
#     load_dotenv()
#     # Retrieve the API token
#     api_token = os.getenv('REPLICATE_API_TOKEN')
#     replicate.Client(api_token)

#     image_url = None

#     # Define the exclusions
#     exclusions = [
#         "ugly", "deformed", "noisy", "blurry", "distorted", "out of focus",
#         "bad anatomy", "extra limbs", "poorly drawn face", "poorly drawn hands",
#         "missing fingers", "nudity", "nude"
#     ]

#     # Convert the list to a comma-separated string
#     exclusions_str = ', '.join(exclusions)

#     if request.method == 'POST':
#         prompt = request.POST.get('prompt')
        
#         if not prompt:
#             return JsonResponse({'error': 'No prompt provided'}, status=400)

#         try:
#             # Run the model using the Replicate API with predefined exclusions
#             output = replicate.run(
#                 "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
#                 input={"prompt": prompt, "exclude": exclusions_str}  # Include the predefined exclusions
#             )
#             image_url = output[0]
#         except replicate.exceptions.ReplicateError as e:
#             # Return the Replicate error details
#             error_details = str(e)
#             print(f"Error generating image: {error_details}")  # Debugging line
#             return JsonResponse({'error': error_details}, status=500)
#         except Exception as e:
#             # Catch any other unexpected errors
#             print(f"Unexpected error: {e}")  # Debugging line
#             return JsonResponse({'error': 'Unexpected error occurred'}, status=500)

#     # Render the template with the image URL if available
#     return render(request, 'generate_image.html', {'image_url': image_url, 'username': username, 'profile_picture_url': profile_picture_url})

def homepage(request):
    username = request.session.get('username')

    # Set a default profile picture URL
    profile_picture_url = '/static/images/default-profile-image2.png'

    if username:
        profile_picture_url = f'/profile-picture/{username}'

    return render(request, 'homepage.html', {'username': username, 'profile_picture_url': profile_picture_url})

def signup(request):
    if request.method == 'POST':
        # Retrieve form data
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Basic form validation
        if password1 != password2:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})

        # Hash the password
        hashed_password = make_password(password1)

        # Get the path to the static file
        pfp_path = os.path.join(settings.BASE_DIR, 'wallify', 'static', 'images', 'dpfp.png')

        # Read the default profile picture as binary data
        with open(pfp_path, 'rb') as pfp_file:
            pfp_blob = pfp_file.read()

        # Insert data into the database with hashed password and default pfp
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO wallify_users (firstname, lastname, email, username, password, pfp)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                [firstname, lastname, email, username, hashed_password, pfp_blob]
            )

        return redirect('/')
    else:
        return render(request, 'signup.html')

def signin(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        with connection.cursor() as cursor:
            cursor.execute("SELECT username, password FROM wallify_users WHERE username = %s", [username])
            user_data = cursor.fetchone()

        if user_data:
            # Extract hashed password from database
            hashed_password = user_data[1]

            # Check if the provided password matches the hashed password
            if check_password(password, hashed_password):
                request.session['username'] = username
                return redirect('/')  # Redirect to home page
            else:
                return render(request, 'login.html', {'error': 'Invalid username or password'})
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    else:
        return render(request, 'login.html')
    
def signout(request):
    logout(request)
    request.session.clear()
    return redirect('/')

# def profile(request):
#     username = request.session.get('username')
#     return render(request, 'profile.html', {'username': username})

def about(request):
    username = request.session.get('username')

    # Set a default profile picture URL
    profile_picture_url = '/static/images/default-profile-image2.png'

    if username:
        profile_picture_url = f'/profile-picture/{username}'
    return render(request, 'about.html', {'username': username, 'profile_picture_url': profile_picture_url})

def gallery(request):
    query = request.GET.get('q', 'free wallpapers')  # Default to 'free wallpapers' if no query is provided
    s3_image_urls = []
    top_search_terms = []

    # Split the search query into individual words
    keywords = query.split()

    # Construct a SQL query dynamically to search for all keywords in the description
    conditions = []
    query_params = []
    for keyword in keywords:
        conditions.append("description LIKE %s")
        query_params.append('%' + keyword + '%')

    # Update SQL query to include username
    sql_query = "SELECT image_key, \"user\" FROM images_table WHERE " + " AND ".join(conditions)

    # Execute the SQL query
    with connection.cursor() as cursor:
        cursor.execute(sql_query, query_params)
        results = cursor.fetchall()

    # S3 bucket URL with '/images/' path
    s3_bucket_url = 'https://{}.s3.amazonaws.com/images/'.format(settings.AWS_STORAGE_BUCKET_NAME)

    # Generate image URLs and include usernames
    for result in results:
        image_key, username = result
        image_url = s3_bucket_url + image_key
        s3_image_urls.append({'url': image_url, 'key': image_key, 'username': username})

    # Log the search term into the search_logs table
    with connection.cursor() as cursor:
        cursor.execute("SELECT search_count FROM search_logs WHERE search_term = %s", [query])
        row = cursor.fetchone()

        if row:
            # If it exists, update the count
            new_count = row[0] + 1
            cursor.execute("UPDATE search_logs SET search_count = %s WHERE search_term = %s", [new_count, query])
        else:
            # If it doesn't exist, insert a new record
            cursor.execute("INSERT INTO search_logs (search_term, search_count) VALUES (%s, %s)", [query, 1])

    # Fetch top 10 search terms
    with connection.cursor() as cursor:
        cursor.execute("SELECT search_term FROM search_logs ORDER BY search_count DESC LIMIT 10")
        top_search_terms = [row[0] for row in cursor.fetchall()]

    # Get the username from session
    username = request.session.get('username')

    # Set a default profile picture URL
    profile_picture_url = '/static/images/default-profile-image2.png'

    if username:
        profile_picture_url = f'/profile-picture/{username}'

    if request.method == 'POST':
        image_key = request.POST.get('image_key')
        if username:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO favorites (image_key, username) VALUES (%s, %s)", [image_key, username])

    # Render the gallery template with the search results and top search terms
    return render(request, 'gallery.html', {
        'results': s3_image_urls,
        'top_search_terms': top_search_terms,
        'username': username,
        'profile_picture_url': profile_picture_url
    })

def upload_image(request):
    if request.method == 'POST':
        description = request.POST.get('description')
        
        # Get the uploaded image file
        uploaded_file = request.FILES.get('image')
        
        # Fetch the username from the session
        username = request.session.get('username')
        if not username:
            return HttpResponse("User not logged in", status=403)
        
        # Initialize a session using Amazon S3
        s3 = boto3.client('s3',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          region_name=settings.AWS_S3_REGION_NAME)
        
        # Define the S3 bucket and file name
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        file_name = uploaded_file.name
        file_content = uploaded_file.read()
        
        # Upload the file to S3
        s3.put_object(Bucket=bucket_name,
                      Key=f'images/{file_name}',
                      Body=file_content,
                      ContentType=uploaded_file.content_type)
        
        # Remove the 'images/' prefix for the database
        db_file_name = file_name

        # Save the image filename, description, and username to the database
        sql_query = """
            INSERT INTO images_table (image_key, description, user)
            VALUES (%s, %s, %s)
        """
        with connection.cursor() as cursor:
            cursor.execute(sql_query, [db_file_name, description, username])
        
        return redirect('profile')
    else:
        return HttpResponse("Image uploaded successfully!")
# def uploadS3(request): 

def profile(request, username=None):
    # Get the username of the logged-in user from the session
    logged_in_username = request.session.get('username')

    # Redirect to login if no username is in session
    if not logged_in_username:
        return redirect('login')

    # If no username is provided, use the session username for the logged-in user's profile
    if username is None:
        username = logged_in_username

    # Set a default profile picture URL for the logged-in user
    profile_picture_url = '/static/images/default-profile-image2.png'
    if logged_in_username:
        profile_picture_url = f'/profile-picture/{logged_in_username}'

    # Handle profile picture update (only for the logged-in user)
    if request.method == 'POST' and logged_in_username == username:
        if 'newProfilePicture' in request.FILES:
            try:
                profile_picture = request.FILES['newProfilePicture']
                file_content = profile_picture.read()

                # Update the user's profile picture in the database
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE wallify_users
                        SET pfp = %s
                        WHERE username = %s
                    """, [file_content, logged_in_username])

                # Redirect to the home page after update
                return redirect('profile')

            except Exception as e:
                # Handle the error (e.g., display an error message)
                return render(request, 'profile.html', {'error': 'Failed to update profile picture'})

    # Fetch user details and profile picture for the profile being viewed
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, firstname, lastname, email, username, pfp FROM wallify_users WHERE username = %s", [username])
        user = cursor.fetchone()

    if user:
        user_id, firstname, lastname, email, viewed_username, pfp_blob = user

        # Construct the URL for the profile picture of the viewed user
        pfp_url = None
        if pfp_blob:
            pfp_url = request.build_absolute_uri(f'/profile_picture/{user_id}/')

        # Fetch favorite images for the user whose profile is being viewed
        favorite_images = []
        with connection.cursor() as cursor:
            cursor.execute("SELECT image_key FROM favorites WHERE username = %s", [username])
            results = cursor.fetchall()
            for result in results:
                image_key = result[0]
                image_url = f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/images/{image_key}'
                favorite_images.append({'url': image_url, 'key': image_key})

        # Fetch uploaded images for the logged-in user
        uploaded_images = []
        with connection.cursor() as cursor:
            cursor.execute("SELECT image_key FROM images_table WHERE \"user\" = %s", [username])
            results = cursor.fetchall()
            for result in results:
                image_key = result[0]
                image_url = f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/images/{image_key}'
                uploaded_images.append({'url': image_url, 'key': image_key})

        context = {
            'firstname': firstname,
            'lastname': lastname,
            'email': email,
            'username': viewed_username,  # User whose profile is being viewed
            'pfp_url': pfp_url,
            'profile_picture_url': profile_picture_url,  # Profile picture URL for the logged-in user
            'favorite_images': favorite_images,
            'uploaded_images': uploaded_images,  # Images uploaded by the logged-in user
            'logged_in_username': logged_in_username,  # Added to display logged-in user's info in navbar
        }
    else:
        context = {'error': 'User not found'}

    return render(request, 'profile.html', context)


def serve_profile_picture(request, user_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT pfp FROM wallify_users WHERE id = %s", [user_id])
        result = cursor.fetchone()

    if result:
        pfp_blob = result[0]
        if pfp_blob:
            return HttpResponse(pfp_blob, content_type='image/png')

    return HttpResponse(status=404)

def get_profile_picture(request, username):
    with connection.cursor() as cursor:
        cursor.execute("SELECT pfp FROM wallify_users WHERE username = %s", [username])
        row = cursor.fetchone()
        if row:
            pfp_data = row[0]
            response = HttpResponse(pfp_data, content_type='image/jpeg')  # Adjust content_type as needed
            return response
    return HttpResponse(status=404)

def delete_favorite_image(request):
    username = request.session.get('username')
    image_key = request.POST.get('image_key')

    if not username:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    if not image_key:
        return JsonResponse({'error': 'No image key provided'}, status=400)

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM favorites
                WHERE username = %s AND image_key = %s
                LIMIT 1
            """, [username, image_key])
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
