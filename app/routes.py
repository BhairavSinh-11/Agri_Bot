from flask import Blueprint, render_template, session, request,jsonify
from . import db
from . import csrf
from .models import User ,Chat
from flask_login import login_required,current_user
from google import genai
from google.genai import types
import os
from werkzeug.utils import secure_filename
import uuid
import time
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


main = Blueprint('main', __name__)

#useful for session clear gltich

@main.route('/clear-session')
def clear_session():
    session.clear()
    return "Session cleared!"


@main.route('/') 
def home():
    user_data=session.get('user')
    if user_data:
        user_exists = User.query.filter_by(id=user_data['id']).first()
        if not user_exists:
            
            # User was deleted from database, so clear session
            
            session.clear()
    user=session.get('user','')
    return render_template('home.html',username=user,active='home')


#profile
@main.route('/api/profile')
@login_required
def get_profile():
    user = User.query.get(session['user']['id'])

    
    if not user:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    return jsonify({
        "success": True,
        "user": {
            "name": user.display_name,
            "username": user.username,
            "email": user.email
        }
    })


#profile update route

@main.route('/api/profile/update', methods=['POST'])
@login_required
@csrf.exempt
def update_profile():
    user_data = session.get('user')

    if not user_data:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    data = request.get_json()

    new_name = data.get("display_name")
    new_username = data.get("username")

    if not new_name or not new_username:
     return jsonify({"success": False, "message": "All fields required"})

    # Update in DB

    user = User.query.get(user_data['id'])
    if not user:
        return jsonify({"success": False, "message": "User not found"})

    user.display_name=new_name
    user.username = new_username
    db.session.commit()

    # Update in session
    
    session['user'] = {
    "id": user.id,
    "name": new_name,
    "username": new_username,
    "email": user.email
}

    session.modified = True
    return jsonify({"success": True})




#Crops infomation

@main.route('/crops')
@login_required
def crops():
    return render_template('crops.html',active='crops')

@main.route('/annadata')
def annadata():
    return render_template('annadata.html',active='annadata')


#AI ASSISANT
@main.route('/AI')
@login_required
def AI():
    # display_name = current_user.display_name
    return render_template('AI.html',  display_name=current_user.display_name,active='AI')


#market
@main.route('/agrimarket')
@login_required
def agrimarket():
    return render_template("market.html",active="agrimarket")


#about page

@main.route('/about')
def about():
    return render_template("about.html",active="about")



#AI ASSISTANT

@main.route('/api/chat-assistant', methods=['POST'])
@csrf.exempt
@login_required
def chat_assistant():
    try:
        user_message=request.form.get('message')
        image = request.files.get('image')
        image_path = None

        if not user_message and image:
            user_message = "Image uploaded"
        
        if not user_message and not image:
            return jsonify({"error": "No input provided"}), 400

        # 🧠 LOAD LAST 5 CHATS (MEMORY)

        previous_chats = Chat.query.filter_by(user_id=current_user.id)\
            .order_by(Chat.timestamp.desc()).limit(5).all()

        history = ""
        for chat in reversed(previous_chats):
            history += f"User: {chat.message}\nBot: {chat.response}\n"

        prompt = f"""
        You are AgriBot 🌱.

        User name: {current_user.display_name}

        Conversation history:
        {history}

        Give short, practical advice.

        Question: {user_message}
        """

        # 📷 IMAGE
        

        if image:

            image_bytes = image.read()

            filename = f"{uuid.uuid4()}_{secure_filename(image.filename)}"

            upload_folder = os.path.join(
        'app',
        'static',
        'uploads',
        'chat_images'
                 )
            
            os.makedirs(upload_folder, exist_ok=True)

            upload_path = os.path.join(
               upload_folder,
            filename
                 )

            with open(upload_path, 'wb') as f:
                f.write(image_bytes)

            image_path = f"/static/uploads/chat_images/{filename}"

            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type=image.mimetype
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, image_part]
            )
        else:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

        bot_reply = response.text

        # 💾 SAVE CHAT

        chat = Chat(
            user_id=current_user.id,
            message=user_message,
            response=bot_reply,
            image_path=image_path
        )
        db.session.add(chat)
        db.session.commit()

        return jsonify({"response": bot_reply})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)})
    

#Chat History

@main.route('/api/chat-history')
@login_required
def chat_history():
    chats = Chat.query.filter_by(user_id=current_user.id)\
        .order_by(Chat.timestamp.desc()).limit(20).all()

    return jsonify([
        {   
            "id":chat.id,
            "message": chat.message,
            "response": chat.response,
            "image_path": chat.image_path
        }
        for chat in chats
    ])


#chat delete button

@main.route('/api/delete-chat/<int:chat_id>', methods=['DELETE'])
@login_required
@csrf.exempt
def delete_chat(chat_id):
    chat = Chat.query.filter_by(id=chat_id, user_id=current_user.id).first()

    if not chat:
        return jsonify({"error": "Chat not found"}), 404

    db.session.delete(chat)
    db.session.commit()

    return jsonify({"success": True})
