from fastapi import FastAPI, HTTPException,Request
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB
client = MongoClient('mongodb+srv://saikesav:Gainedi504@cluster0.zhoasvl.mongodb.net/zomato?retryWrites=true&w=majority&appName=Cluster0')
db = client['zomato'] 
collection = db['details']  

def serialize_restaurant(restaurant):
    if not restaurant.get('featured_image'):
        restaurant['featured_image'] = "https://1000logos.net/wp-content/uploads/2023/01/Zomato-Logo-2010.png"
    return {
        "id": str(restaurant['id']),  
        "name": restaurant['name'],
        "image": restaurant['featured_image'],
    }

def format_restaurant_details(restaurant):
    if not restaurant.get('featured_image'):
        restaurant['featured_image'] = "https://1000logos.net/wp-content/uploads/2023/01/Zomato-Logo-2010.png"
    return {
        "id": str(restaurant.get('id')),
        "name": restaurant.get('name'),
        "address": restaurant.get('location').get('address'),
        "cuisines": restaurant.get('cuisines'),
        "average_cost_for_two": restaurant.get('average_cost_for_two'),
        "aggregate_rating": restaurant.get('user_rating').get('aggregate_rating'),
        "rating_text": restaurant.get('user_rating').get('rating_text'),
        "rating_color": restaurant.get('user_rating').get('rating_color'),
        "votes": restaurant.get('user_rating').get('votes'),
        "featured_image": restaurant.get('featured_image'),
        "latitude": restaurant.get('location').get('latitude'),
        "longitude": restaurant.get('location').get('longitude')
    }

@app.get("/restaurantslist")
async def get_restaurants(page: int = 1, limit: int = 10):
    skip = (page - 1) * limit
    restaurants = list(collection.find().skip(skip).limit(limit))
    restaurants = [serialize_restaurant(r) for r in restaurants] 
    count = collection.count_documents({})
    
    return {
        "restaurants": restaurants,
        "total": count
    }

@app.get("/restaurantsDetails/{restaurant_id}")
async def get_restaurant_details_endpoint(restaurant_id: str):
    restaurant = collection.find_one({"id": restaurant_id})
    
    if restaurant:
        details = format_restaurant_details(restaurant)
        return {"details": details}
    else:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
@app.get("/randomRestaurant")  
async def get_random_restaurant():
    restaurant = collection.aggregate([{ "$sample": { "size": 1 } }]).next()
    details = format_restaurant_details(restaurant)
    return {"details": details}

@app.post("/postFeedback")
async def post_feedback(request: Request):
    data = await request.json()
    rating = data.get("rating")
    rating_text = data.get("rating_text")
    res_id = data.get("res_id")
    
    if not rating or not rating_text or not res_id:
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    collection.update_one(
        {"id": res_id}, 
        {"$set": {"user_rating.aggregate_rating": rating, "user_rating.rating_text": rating_text}}
    )
    return 