
import os
import django
import random
import argparse
import glob
import shutil
from pathlib import Path

# -------------------- DJANGO SETUP --------------------

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main_app.settings")
django.setup()

from django.utils import timezone
from django.db import models
from accounts.models import User
from issues.models import Issue, IssueImage

# -------------------- GLOBAL CONFIG --------------------

# Frontend Categories
CATEGORIES = [
    "pothole", "streetlight", "garbage", "water", "drainage", "road", "electricity", "other"
]

# Dummy Data Lists - Updated with Nepali names/references
DUMMY_USERS = [
    ("Gwen Stacy", "gwen@stacy.com"),
    ("Rhaenyra Targaryen", "rhaenyra@targaryen.com"),
    ("Night Fury", "night@fury.com"),
    ("Bellatrix Lestrange", "bellatrix@lestrange.com"),
    ("Shristi Stacy", "shristi@stacy.com"),
    ("Andrew Handsome", "andrew@handsome.com"),
    ("Tony Stark", "tony@stark.com"),
    ("Steve Rogers", "steve@rogers.com"),
    ("Natasha Romanoff", "natasha@romanoff.com"),
    ("Wanda Maximoff", "wanda@maximoff.com"),
    ("Aarav Sharma", "aarav@sharma.com"),
    ("Sita Patil", "sita@patil.com"),
    ("Rohan Gupta", "rohan@gupta.com"),
    ("Anjali Singh", "anjali@singh.com"),
    ("Bikram Thapa", "bikram@thapa.com"),
    ("Manita Gurung", "manita@gurung.com"),
    ("Rajesh Hamal", "rajesh@hamal.com"),
    ("Sushma Karki", "sushma@karki.com"),
    ("Nabin Bhattarai", "nabin@bhattarai.com"),
    ("Priya Adhikari", "priya@adhikari.com"),
    ("Suraj Shrestha", "suraj@shrestha.com"),
    ("Kabita Rai", "kabita@rai.com"),
    ("Dipendra Shah", "dipendra@shah.com"),
    ("Ganga Maya", "ganga@maya.com"),
    ("Hari Bahadur", "hari@bahadur.com"),
]

# Central Coordinates for Major Nepali Cities
# We will generate points around these centers.
# Structure: "City Name": (Lat, Lng)
NEPALI_CITIES = {
    "Kathmandu": (27.7172, 85.3240),
    "Lalitpur": (27.6644, 85.3188),
    "Bhaktapur": (27.6710, 85.4298),
    "Pokhara": (28.2096, 83.9856),
    "Biratnagar": (26.4525, 87.2718),
    "Bharatpur": (27.6792, 84.4385),
    "Birgunj": (27.0135, 84.8773),
    "Butwal": (27.6975, 83.4646),
    "Dharan": (26.8126, 87.2852),
    "Hetauda": (27.4292, 85.0305),
}

# Common Nepali Places/Toles/Marga suffix
NEPALI_PLACE_SUFFIXES = ["Tole", "Marg", "Chok", "Bazzar", "Sadak", "Galli", "Nagar"]
NEPALI_PLACE_PREFIXES = ["New", "Old", "Upper", "Lower", "San", "Thulo", "Purano", "Naya"]
COMMON_PLACE_NAMES = [
    "Baneshwor", "Koteshwor", "Maitidevi", "Putalisadak", "Thamel", "Asan", "Indrachowk",
    "Patan", "Jawalakhel", "Kupondole", "Lagankhel", "Suryabinayak", "Kamalbinayak",
    "Mahendrapool", "Lakeside", "Chipledhunga", "Traffic Chowk", "Main Road", "Bargachhi"
]

# Extended Issues List (200+) ensuring coverage of all 8 categories
# Categories: "pothole", "streetlight", "garbage", "water", "drainage", "road", "electricity", "other"

DUMMY_ISSUES = []

# Helper to generate issues
def create_issue_template(title, desc, cat):
    return {"title": title, "desc": desc, "cat": cat}

# 1. Potholes (Target: ~25)
pothole_templates = [
    ("Large Pothole on Main Road", "A massive pothole is causing traffic slowdowns and potential vehicle damage."),
    ("Deep Crater near School", "Dangerous deep pothole right in front of the primary school gate."),
    ("Series of Potholes", "A stretch of 100m is full of small but sharp potholes."),
    ("Resurfaced Road Sinking", "Newly resurfaced road has already developed a pothole."),
    ("Pothole Filled with Water", "Rainwater has filled a pothole making it invisible to bikers."),
    ("Hidden Pothole on Turn", "Dangerous pothole located exactly on a blind turn."),
    ("Sharp Edged Pothole", "Pothole with very sharp edges caused a tire blowout."),
    ("Expanding Pothole", "This pothole has doubled in size over the last month."),
    ("Gravel filled Pothole washed away", "The temporary gravel fill has washed away leaving the hole open."),
    ("Pothole on Bridge", "Concerns about structural integrity due to pothole on the bridge deck."),
    ("Pothole near Bus Stop", "Passengers are tripping over a pothole while getting off the bus."),
    ("Bike Accident caused by Pothole", "Witnessed a bike skid due to this pothole yesterday."),
    ("Pothole obstructing driveway", "Cannot exit driveway safely due to large hole."),
    ("Pothole accumulating trash", "Trash is collecting in the pothole creating a mess."),
    ("Multiple potholes on crosswalk", "Pedestrians twisting ankles on the crosswalk."),
    ("Jagged Pothole", "Asphalt has broken away leaving jagged edges."),
    ("Pothole affecting drainage", "Pothole is diverting water away from the drain."),
    ("Neglected Pothole", "Reported months ago, still no action on this pothole."),
    ("Pothole on Highway connection", "High speed entry ramp has a dangerous pothole."),
    ("Cluster of Potholes", "Impossible to dodge one without hitting another."),
    ("Sunken Manhole Pothole", "Area around manhole has sunk creating a pothole effect."),
    ("Pothole near Hospital", "Ambulances have to slow down significantly here."),
    ("Muddy Pothole", "Pothole creates a mud splash zone for pedestrians."),
    ("Pothole on narrow lane", "Blocks the entire width of the narrow lane."),
    ("Reopened Pothole", "The patch work failed and the pothole is back."),
]
for p in pothole_templates: DUMMY_ISSUES.append(create_issue_template(p[0], p[1], "pothole"))

# 2. Streetlight (Target: ~25)
streetlight_templates = [
    ("Streetlight completely out", "The pole #34 is completely dark at night."),
    ("Flickering Streetlight", "Light is strobing, causing seizures/headaches."),
    ("Dayburning Light", "Streetlight is on during the day, wasting energy."),
    ("Dim Streetlight", "Bulb is failing and providing almost no light."),
    ("Broken Lamp Cover", "The plastic cover is hanging by a wire."),
    ("Leaning Light Pole", "The entire pole is leaning dangerously."),
    ("Light Obstructed by Tree", "Branches have grown over the light blocking it."),
    ("Missing Bulb", "The socket is empty, looks like bulb was stolen or fell."),
    ("Sparks from Light fixture", "Saw sparks coming from the light fixture in rain."),
    ("Light shining into bedroom", "Needs a shield, shines directly into homes."),
    ("Solar Light Battery Dead", "Solar light turns off after 1 hour of darkness."),
    ("Timer Misconfigured", "Lights turn off at 2 AM leaving street dark till dawn."),
    ("Vandalized Light Pole", "Access panel has been kicked open."),
    ("Rusted Pole Base", "Base of the pole is severely corroded."),
    ("Streetlight wire dangling", "Power wire to the light is hanging low."),
    ("Light color mismatch", "One blue light in a row of yellow lights."),
    ("Intermittent outage", "Light works sometimes, then stays off for days."),
    ("Whole street dark", "Entire row of lights is out, likely a fuse."),
    ("New Pole needed", "Area is too dark, needs a new installation."),
    ("Light fell down", "The fixture fell onto the sidewalk."),
    ("Buzzing Streetlight", "Making a very loud buzzing noise."),
    ("Light blocked by banner", "Advertisement banner covers the light."),
    ("Sensor broken", "Light doesn't turn on even when it's pitch black."),
    ("Old Sodium vapor", "Need to upgrade to LED for better visibility."),
    ("Dangerous voltage leak", "Pole gives a shock if touched in rain."),
]
for p in streetlight_templates: DUMMY_ISSUES.append(create_issue_template(p[0], p[1], "streetlight"))

# 3. Garbage (Target: ~25)
garbage_templates = [
    ("Overflowing Dumpster", "Community bin is overflowing onto the street."),
    ("Missed Trash Pickup", "Truck didn't come this Friday as scheduled."),
    ("Illegal Dumping site", "People dumping construction waste in empty lot."),
    ("Dead Animal", "Dead dog on the side of the road needs removal."),
    ("Litter in Park", "Picnic area covered in plastic plates and bottles."),
    ("Broken Dustbin", "Public dustbin is smashed and unusable."),
    ("Burning Plastic", "Toxic smoke from burning garbage pile."),
    ("Medical Waste found", "Syringes and bandages dumped near river."),
    ("Restaurant dumping food", "Local eatery dumping rotten food in alley."),
    ("Recycling pile up", "Recycling sacks haven't been collected in weeks."),
    ("Trash blocking drain", "Garbage bags are blocking the storm drain."),
    ("Smell from garbage", "Unbearable stench from rotting waste."),
    ("Maggot infestation", "Garbage pile has become a breeding ground for flies."),
    ("Glass on sidewalk", "Broken bottles scattered on the walkway."),
    ("Scattered Trash", "Dogs have torn open bags, trash everywhere."),
    ("Construction Debris", "Pile of bricks and sand left on road."),
    ("Electronic Waste", "Old TVs and monitors dumped in the woods."),
    ("River bank pollution", "Plastic accumulation on the river bank."),
    ("Marketplace litter", " vegetable market left huge mess after closing."),
    ("Hazardous chemical dumping", "Strange drums dumped in the ditch."),
    ("Dumpster fire risk", "Someone threw hot ash, bin is smoking."),
    ("No bin availability", "Need a public bin at this busy bus stop."),
    ("Trash truck spill", "Truck spilled load while turning."),
    ("Overflowing recycling bin", "Paper and plastic blowing in wind."),
    ("Sharps hazard", "Needles found in playground sand."),
]
for p in garbage_templates: DUMMY_ISSUES.append(create_issue_template(p[0], p[1], "garbage"))

# 4. Water (Target: ~25)
water_templates = [
    ("No Water Supply", "Taps are dry for 3 days straight."),
    ("Burst Main Pipe", "Drinking water pipe burst, flooding road."),
    ("Dirty/Muddy Water", "Water is dark brown and muddy."),
    ("Low Pressure", "Water not reaching second floor tank."),
    ("Leaking Public Tap", "Public standpost running 24/7 wasting water."),
    ("Contaminated Water", "Water smells like sewage, cross contamination."),
    ("Broken Valve", "Main supply valve is stuck closed."),
    ("Water Theft", "Illegal pump connection reducing neighborhood pressure."),
    ("Meter Leaking", "Water meter is leaking profusely."),
    ("Tank Overflow", "Community tank overflows every morning."),
    ("Frozen Pipe", "External pipe burst due to cold."),
    ("Chlorine smell", "Water has excessive chlorine smell."),
    ("Worms in water", "Visible worms in tap water, health hazard."),
    ("Sand in water", "Heavy sediment load in supply."),
    ("Erratic schedule", "Water comes at 3 AM randomly."),
    ("Pipe exposed", "PVC pipe exposed to traffic, likely to break."),
    ("Hydrant Leaking", "Fire hydrant dripping constantly."),
    ("Water wastage", "Neighbor washing car with open hose for hours."),
    ("Dry Well", "Community well has gone dry, need alternative."),
    ("Supply line cut", "Road construction cut the water line."),
    ("Rusty Water", "Water is orange/red from rusted pipes."),
    ("Air in pipes", "Taps just sputtering air, meter running."),
    ("Leak in chaotic pipes", "Spaghetti of pipes leaking everywhere."),
    ("Manhole full of water", "Water supply valve pit is flooded."),
    ("Water tanker issue", "Scheduled tanker delivery did not arrive."),
]
for p in water_templates: DUMMY_ISSUES.append(create_issue_template(p[0], p[1], "water"))

# 5. Drainage (Target: ~25)
drainage_templates = [
    ("Blocked Storm Drain", "Rainwater pooling because drain is choked."),
    ("Sewage Backflow", "Sewage backing up into house toilets."),
    ("Open Manhole", "Manhole cover missing, death trap."),
    ("Broken Manhole Cover", "Cover is cracked and caved in."),
    ("Foul Odor", "Strong sewer gas smell in the street."),
    ("Stagnant Water", "Drainage ditch has stagnant water, dengue risk."),
    ("Overflowing Sewer", "Black water bubbling up from manhole."),
    ("Drain collapsed", "Current drainage pipe has collapsed underground."),
    ("Drain clogged with plastic", "Plastic bottles completely blocking flow."),
    ("Narrow drain capacity", "Drain cannot handle even light rain."),
    ("Illegal connection to storm drain", "Sewage line connected to rain drain."),
    ("Drainage cover rattling", "Loose cover makes loud noise when cars pass."),
    ("Drain cleaning needed", "Silt has filled 90% of the drain."),
    ("Flooded Basement", "Street drainage leaking into basements."),
    ("Exposed Drain", "Deep open drain near school needs slab."),
    ("Drainage outlet blocked", "River level high, blocking outlet."),
    ("Roots in drain", "Tree roots have invaded and blocked pipe."),
    ("Oil in drain", "Garage dumping oil into storm drain."),
    ("Grease clog", "Restaurant grease has solidified and blocked sewer."),
    ("Drainage pipe leak", "Leaking sewage onto the road."),
    ("Mosquito breeding ground", "Blocked drain is full of larvae."),
    ("Drainage construction delayed", "Open pit left for weeks."),
    ("Manhole hidden", "Paved over manhole, cannot access for cleaning."),
    ("Sewer rats", "Rats entering homes from broken drain."),
    ("Chemical smell from drain", "Industrial waste dumped in sewer."),
]
for p in drainage_templates: DUMMY_ISSUES.append(create_issue_template(p[0], p[1], "drainage"))

# 6. Road (Target: ~25)
road_templates = [
    ("Unpaved Road", "Road is still dirt/mud, impossible in rain."),
    ("Broken Asphalt", "Top layer of road has peeled off."),
    ("Speed breaker too high", "Cars scraping bottom on illegal bump."),
    ("Missing Divider", "Vehicles crossing into oncoming lane."),
    ("Faded Lane Markings", "Cannot see lanes at night."),
    ("Crumbling Edge", "Edge of road breaking away into ditch."),
    ("Slippery Surface", "Oil spill making curve dangerous."),
    ("Loose Gravel", "Skid hazard for two-wheelers."),
    ("Narrow Bottleneck", "Road narrows suddenly causing jams."),
    ("Blind Turn", "Need a convex mirror at this corner."),
    ("Illegal Parking", "Cars parked on both sides blocking traffic."),
    ("Construction Material on Road", "Sand/Gravel pile blocking half the road."),
    ("Uneven surface", "Road is wavy and bumpy."),
    ("Road sinking", "Section of road settling unevenly."),
    ("Bridge joint gap", "Gap in bridge expansion joint is too wide."),
    ("Signage missing", "No entry sign is missing."),
    ("Wrong way drivers", "Need enforcement or barriers."),
    ("Pedestrian crossing unsafe", "Zebra crossing needs repainting."),
    ("Footpath encroached", "Shops displaying goods on sidewalk."),
    ("Broken Curb", "Concrete curb destroyed by trucks."),
    ("Road dust", "Excessive dust causing visibility/health issues."),
    ("Traffic light broken", "Signal stuck on red."),
    ("Barrier damaged", "Safety barrier on cliff edge crushed."),
    ("Tree blocking sign", "Stop sign hidden by branches."),
    ("Cycle lane blocked", "Motorcycles using cycle lane."),
]
for p in road_templates: DUMMY_ISSUES.append(create_issue_template(p[0], p[1], "road"))

# 7. Electricity (Target: ~25)
electricity_templates = [
    ("Low Voltage", "Appliances not working due to voltage drop."),
    ("Power Surge", "High voltage damaged TV and Fridge."),
    ("Wire Sparking", "Service wire sparking at the pole."),
    ("Loose Connection", "Power flickers when wind blows."),
    ("Hanging Wires", "Cable spaghetti hanging head high."),
    ("Pole Bent", "Storm bent the electric pole."),
    ("Transformer Oil Leak", "Oil dripping from transformer."),
    ("Fuse Blown", "Phase missing in the neighborhood."),
    ("Meter Burned", "Electric meter caught fire."),
    ("Illegal Hooking", "People stealing electricity from main line."),
    ("Tree on line", "Branch resting on live wire."),
    ("Power cut unscheduled", "Power out for 10 hours without notice."),
    ("Live wire on ground", "Snapped wire lying on footpath."),
    ("Grid failure", "Whole area blacked out."),
    ("High Tension danger", "House built too close to HT line."),
    ("Switchgear smoke", "Distribution box smoking."),
    ("Exposed conductor", "Insulation peeled off wire."),
    ("Pole interfering with traffic", "Pole in the middle of widened road."),
    ("Bird nest on transformer", "Risk of short circuit."),
    ("Humming noise", "Transformer making unbearable noise."),
    ("Underground cable fault", "Dug up road to fix cable."),
    ("Meter reading error", "Bill is abnormally high."),
    ("Voltage fluctuation", "Lights getting bright and dim."),
    ("Neutral broken", "Causing voltage imbalance."),
    ("Crowded pole", "Too many telecom wires on electric pole."),
]
for p in electricity_templates: DUMMY_ISSUES.append(create_issue_template(p[0], p[1], "electricity"))

# 8. Other (Target: ~25)
other_templates = [
    ("Noise Pollution", "Party palace playing loud music till 2 AM."),
    ("Air Pollution", "Brick kiln smoke blanketing area."),
    ("Stray Dogs Aggressive", "Pack of dogs chasing kids."),
    ("Vandalism", "Bus stop glass smashed."),
    ("Graffiti", "Gang tags on school wall."),
    ("Encroachment", "Public land captured by private party."),
    ("Landslide risk", "Hillside eroding near houses."),
    ("Falling Tree", "Dead tree leaning over playground."),
    ("Overgrown Vegetation", "Bushes blocking walkway."),
    ("Snake infestation", "Lots of snakes seen in community park."),
    ("Public Park neglect", "Swings broken, grass uncut."),
    ("Unauthorized Billboard", "Huge hoarding blocking view."),
    ("Beggar nuisance", "Aggressive begging at traffic light."),
    ("Drunk nuisance", "People drinking in public park."),
    ("Unsafe building", "Old building looks like it will collapse."),
    ("Slippery stairs", "Public staircase covered in moss."),
    ("Missing railing", "Bridge railing stolen."),
    ("Open construction pit", "Unfenced pit is a hazard."),
    ("Monkey menace", "Monkeys entering homes and stealing food."),
    ("Dead birds", "Multiple dead birds found (poison?)."),
    ("Unauthorized stall", "Food cart blocking fire hydrant."),
    ("Public Toilet dirty", " unusable condition."),
    ("Park bench broken", "Nowhere to sit in park."),
    ("Statue defaced", "Community statue vandalized."),
    ("Dust storm", "Construction site not wetting dust."),
]
for p in other_templates: DUMMY_ISSUES.append(create_issue_template(p[0], p[1], "other"))


TARGET_USERS = 10
TARGET_ISSUES = 200 # Increased as requested
POOL_BUFFER_RATIO = 1.25

MEDIA_ROOT = "media"
ISSUE_IMAGES_DIR = os.path.join(MEDIA_ROOT, "issue_images")
PROFILE_PICS_DIR = os.path.join(MEDIA_ROOT, "profile_pics")
POOL_DIR = os.path.join(MEDIA_ROOT, "_seed_pool")

DEFAULT_PASSWORD = "asdfghjkl;'"
VALID_EXT = (".jpg", ".jpeg", ".png", ".webp")


# -------------------- ARGUMENT PARSER --------------------

def parse_args():
    global TARGET_USERS, TARGET_ISSUES
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--users", type=int)
    parser.add_argument("-i", "--issues", type=int)
    args = parser.parse_args()

    if args.users:
        TARGET_USERS = args.users
    if args.issues:
        TARGET_ISSUES = args.issues

# -------------------- UTILITIES --------------------

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def safe_filename(path):
    name, ext = os.path.splitext(os.path.basename(path))
    return f"{name}_{random.randint(10000,99999)}{ext}"

def random_datetime():
    now = timezone.now()
    return now - timezone.timedelta(
        days=random.randint(0, 365),
        seconds=random.randint(0, 86400)
    )

def get_random_nepali_location():
    """Returns (city_name, address_string, lat, lng) within Nepal city bounds."""
    city_name = random.choice(list(NEPALI_CITIES.keys()))
    center_lat, center_lng = NEPALI_CITIES[city_name]
    
    # Generate realistic local address string
    prefix = random.choice(NEPALI_PLACE_PREFIXES) if random.random() < 0.3 else ""
    place = random.choice(COMMON_PLACE_NAMES)
    suffix = random.choice(NEPALI_PLACE_SUFFIXES)
    
    # Construct address like "New Baneshwor Marg, Kathmandu" or "Thamel, Kathmandu"
    # We mix it up for variety
    if random.random() < 0.5:
        local_part = f"{prefix} {place} {suffix}".strip()
    else:
        local_part = f"{place} {suffix}".strip() if random.random() < 0.5 else place
        
    address = f"{local_part}, {city_name}"
    
    # Add random jitter to coordinates (approx 2-3km radius)
    # 0.01 degrees is approx 1.1km
    lat_jitter = random.uniform(-0.02, 0.02)
    lng_jitter = random.uniform(-0.02, 0.02)
    
    final_lat = center_lat + lat_jitter
    final_lng = center_lng + lng_jitter
    
    return city_name, address, final_lat, final_lng

def cast_float_param(val):
    return float(f"{val:.6f}")

def collect_images(directory):
    images = []
    for root, _, files in os.walk(directory):
        for f in files:
            if f.lower().endswith(VALID_EXT):
                images.append(os.path.join(root, f))
    return images

# -------------------- IMAGE POOL LOGIC --------------------

def expand_pool(pool, required_count):
    minimum = int(required_count * POOL_BUFFER_RATIO)

    if not pool:
        raise Exception("No images available to build pool.")

    while len(pool) < minimum:
        src = random.choice(pool)
        duplicate = os.path.join(POOL_DIR, safe_filename(src))
        shutil.copy(src, duplicate)
        pool.append(duplicate)

    random.shuffle(pool)
    return pool

def build_issue_pool():
    ensure_dir(POOL_DIR)
    base_images = collect_images(ISSUE_IMAGES_DIR)

    if not base_images:
        # Fallback if no images found, create dummy empty files if needed or raise
        # For this script we assume images exist or user will provide them.
        # But to prevent crash if empty:
       print("WARNING: No issue images found in media/issue_images. Ensure you have some sample images.")
       return []

    pool = []

    # Copy base images to pool (non-destructive)
    for img in base_images:
        dest = os.path.join(POOL_DIR, safe_filename(img))
        shutil.copy(img, dest)
        pool.append(dest)

    pool = expand_pool(pool, TARGET_ISSUES)

    print(f"Issue pool ready with {len(pool)} images.")
    return pool

def build_user_pool(issue_pool):
    ensure_dir(PROFILE_PICS_DIR)

    user_images = glob.glob(os.path.join(PROFILE_PICS_DIR, "*.*"))

    if not user_images:
        print("User pool empty → borrowing from issue pool.")
        user_images = issue_pool.copy() if issue_pool else []

    if not user_images:
         # Still empty? just return empty, handle gracefully
         return []

    while len(user_images) < int(TARGET_USERS * POOL_BUFFER_RATIO):
        user_images.append(random.choice(user_images))

    random.shuffle(user_images)
    return user_images

# -------------------- USER CREATION --------------------

def create_users():
    existing = list(User.objects.filter(is_superuser=False))
    needed = TARGET_USERS - len(existing)

    users = existing.copy()

    for i in range(max(0, needed)):
        name, email = DUMMY_USERS[i % len(DUMMY_USERS)]
        email = f"{email.split('@')[0]}_{random.randint(1000,9999)}@{email.split('@')[1]}"

        user = User.objects.create(
            first_name=name.split()[0],
            last_name=" ".join(name.split()[1:]),
            email=email,
        )
        user.set_password(DEFAULT_PASSWORD)
        user.save()
        users.append(user)

        print(f"Created user: {user.email}")

    return users

def assign_profile_pics(users, pool):
    if not pool: return

    pool_idx = 0
    for user in users:
        if user.profile_pic:
            continue

        src = pool[pool_idx % len(pool)]
        pool_idx += 1
        
        fname = f"user_{user.id}_{safe_filename(src)}"
        dest = os.path.join(PROFILE_PICS_DIR, fname)

        shutil.copy(src, dest)

        user.profile_pic = f"profile_pics/{fname}"
        user.save()

# -------------------- ISSUE CREATION --------------------

def get_issue_data(index):
    base = DUMMY_ISSUES[index % len(DUMMY_ISSUES)]
    return base

def attach_image_to_issue(issue, image_path):
    issue_dir = os.path.join(ISSUE_IMAGES_DIR, str(issue.id))
    ensure_dir(issue_dir)
    
    fname = safe_filename(image_path)
    dest = os.path.join(issue_dir, fname)
    shutil.copy(image_path, dest)
    
    IssueImage.objects.create(
        issue=issue,
        image=f"issue_images/{issue.id}/{fname}"
    )

def generate_issues(users, pool):
    existing = Issue.objects.count()
    needed = TARGET_ISSUES - existing

    if needed <= 0:
        print("No new issues needed.")
        return
    
    created_issues = []

    for i in range(needed):
        issue_data = get_issue_data(i)
        reporter = random.choice(users)
        
        is_resolved = random.choice([True, False])
        is_archived = random.choice([True, False])
        
        # Get Nepali location data
        city, address, lat, lng = get_random_nepali_location()

        issue = Issue.objects.create(
            title=issue_data["title"],
            description=issue_data["desc"],
            category=issue_data["cat"],
            reported_by=reporter,
            address=address,
            city=city,
            latitude=cast_float_param(lat),
            longitude=cast_float_param(lng),
            created_at=random_datetime(),
            is_resolved=is_resolved,
            is_archived=is_archived
        )
        created_issues.append(issue)
        print(f"Created Issue #{issue.id} in {city} (Resolved: {is_resolved})")

    # Image Distribution
    if not created_issues:
        return

    if not pool:
        print("Warning: No image pool available to attach images.")
        return

    print("Distributing images from pool...")
    for i, image_path in enumerate(pool):
        if i < len(created_issues):
            target_issue = created_issues[i]
        else:
            target_issue = random.choice(created_issues)
        
        attach_image_to_issue(target_issue, image_path)

# -------------------- MAIN --------------------

def main():
    parse_args()

    print(f"Target Users: {TARGET_USERS}")
    print(f"Target Issues: {TARGET_ISSUES}")

    users = create_users()

    issue_pool = build_issue_pool()
    user_pool = build_user_pool(issue_pool)

    assign_profile_pics(users, user_pool)

    generate_issues(users, issue_pool)

    print("Seeding completed successfully.")

if __name__ == "__main__":
    main()
