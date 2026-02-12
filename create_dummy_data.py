import os
import django
import random
import glob
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main_app.settings')
django.setup()

from accounts.models import User
from issues.models import Issue, IssueImage

# Constants
MEDIA_ROOT = 'media'
PROFILE_PICS_DIR = os.path.join(MEDIA_ROOT, 'profile_pics')
ISSUE_IMAGES_DIR = os.path.join(MEDIA_ROOT, 'issue_images')
OUTPUT_FILE = 'user_details.txt'
DEFAULT_PASSWORD = "asdfghjkl;'"

# Dummy Data Lists
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
    ("Peter Parker", "peter@parker.com"),
    ("Bruce Banner", "bruce@banner.com"),
    ("Thor Odinson", "thor@asgard.com"),
    ("Loki Laufeyson", "loki@mischief.com"),
    ("Stephen Strange", "doctor@strange.com"),
    ("T'Challa", "black@panther.com"),
    ("Scott Lang", "ant@man.com"),
    ("Carol Danvers", "captain@marvel.com"),
    ("Gamora Zen", "gamora@guardians.com"),
    ("Nebula Zen", "nebula@guardians.com"),
]

# 100+ Predefined Realistic Issues
DUMMY_ISSUES = [
    # Road / Potholes
    {"title": "Large Pothole on Main St", "desc": "A very large pothole has formed in the middle of the road, causing traffic alerts.", "cat": "road"},
    {"title": "Cracked Sidewalk near Park", "desc": "The sidewalk pavement is cracked and uneven, posing a tripping hazard for pedestrians.", "cat": "road"},
    {"title": "Missing Street Sign", "desc": "The stop sign at the intersection of 5th and Elm is missing.", "cat": "road"},
    {"title": "Faded Crosswalk Markings", "desc": "The zebra crossing paint has completely faded, making it dangerous for students crossing.", "cat": "road"},
    {"title": "Debris Blocking Bike Lane", "desc": "Construction debris has been left in the bike lane for over a week.", "cat": "road"},
    {"title": "Sinkhole Developing", "desc": "Small sinkhole appearing near the breakdown lane on Highway 4.", "cat": "road"},
    {"title": "Damaged Guardrail", "desc": "Guardrail was hit by a car and keeps protruding into the lane.", "cat": "road"},
    {"title": "Unpaved Road Connection", "desc": "The connecting road between Sector 4 and 5 is still unpaved and muddy.", "cat": "road"},
    {"title": "Speed Bump Too High", "desc": "The newly installed speed bump is scraping the bottom of normal sedans.", "cat": "road"},
    {"title": "Traffic Light Malfunction", "desc": "The signal at the busy 4-way junction is stuck on red for all sides.", "cat": "road"},
    {"title": "Blind Spot Mirror Broken", "desc": "The convex mirror at the blind turn is shattered.", "cat": "road"},
    {"title": "Road Resurfacing Needed", "desc": "The entire stretch of road is riddled with small potholes and needs resurfacing.", "cat": "road"},
    {"title": "Illegal Parking Blocking Road", "desc": "Cars are parked on both sides of the narrow lane, blocking traffic flow.", "cat": "road"},
    {"title": "Loose Gravel Hazard", "desc": "Loose gravel from recent works is causing skidding risks.", "cat": "road"},
    {"title": "Manhole Cover Loose", "desc": "The manhole cover clanks loudly every time a car passes over it.", "cat": "road"},
    {"title": "Road Markings Invisible at Night", "desc": "Reflectors are missing and lines are not visible in the dark.", "cat": "road"},
    {"title": "Bridge Expansion Joint Gap", "desc": "The gap in the bridge joint has widened dangerously.", "cat": "road"},
    {"title": "Overgrown Bush Blocking View", "desc": "Bushes at the corner are blocking the view of oncoming traffic.", "cat": "road"},
    {"title": "Narrow Road Congestion", "desc": "The single lane road is causing massive bottlenecks during rush hour.", "cat": "road"},
    {"title": "Slippery Road Surface", "desc": "Oil spill has not been cleaned up, making the turn very slippery.", "cat": "road"},

    # Water / Drainage
    {"title": "Burst Water Main", "desc": "Water is gushing out from the ground, flooding the street.", "cat": "water"},
    {"title": "No Water Supply", "desc": "Our entire block has had no running water for the last 24 hours.", "cat": "water"},
    {"title": "Dirty Tap Water", "desc": "The water coming from the tap is brown and smells metallic.", "cat": "water"},
    {"title": "Low Water Pressure", "desc": "Water pressure is too low to even run the shower on the first floor.", "cat": "water"},
    {"title": "Leaking Fire Hydrant", "desc": "Fire hydrant is leaking gallons of water onto the pavement.", "cat": "water"},
    {"title": "Clogged Storm Drain", "desc": "The storm drain is full of leaves and trash, causing immediate flooding when it rains.", "cat": "drainage"},
    {"title": "Sewage Smell in Neighborhood", "desc": "A strong sewage smell is pervading the area, likely a leak nearby.", "cat": "drainage"},
    {"title": "Overflowing Sewer Manhole", "desc": "Sewage is bubbling up from the manhole cover.", "cat": "drainage"},
    {"title": "Broken Drainage Cover", "desc": "The concrete cover of the drain is broken, open hole is dangerous.", "cat": "drainage"},
    {"title": "Stagnant Water Breeding Mosquitoes", "desc": "Water has pooled in the blocked drainage ditch and is breeding mosquitoes.", "cat": "drainage"},
    {"title": "Water Meter Leaking", "desc": "The municipal water meter is leaking at the connection point.", "cat": "water"},
    {"title": "Contaminated Well Water", "desc": "Community well water tested positive for high arsenic levels.", "cat": "water"},
    {"title": "Drainage Pipe Exposed", "desc": "Underground drainage pipe creates a trip hazard as it has become exposed.", "cat": "drainage"},
    {"title": "Flooded Underpass", "desc": "The underpass floods completely even with light rain.", "cat": "drainage"},
    {"title": "Illegal Water Connection", "desc": "Someone has tapped into the main line illegally, reducing pressure for others.", "cat": "water"},
    {"title": "Broken Public Tap", "desc": "The public water standpost tap is broken and wasting water.", "cat": "water"},
    {"title": "Drainage Blocked by Construction", "desc": "Construction soil has filled up the roadside drainage.", "cat": "drainage"},
    {"title": "Water Tank Overflowing", "desc": "Community overhead tank flows over for hours every morning.", "cat": "water"},
    {"title": "Frozen Pipes Risk", "desc": "Exposed community pipes need insulation before winter.", "cat": "water"},
    {"title": "Open Drain Hazard", "desc": "Deep drain running along the school has no fencing.", "cat": "drainage"},

    # Electricity / Streetlights
    {"title": "Streetlight Not Working", "desc": "The streetlight in front of house #45 has been out for weeks.", "cat": "streetlight"},
    {"title": "Flickering Streetlight", "desc": "The light flickers like a strobe light, very distracting for drivers.", "cat": "streetlight"},
    {"title": "Dayburning Streetlight", "desc": "Streetlight stays on all day wasting electricity.", "cat": "streetlight"},
    {"title": "Exposed Electrical Wires", "desc": "Live wires are hanging low from the pole near the playground.", "cat": "streetlight"},
    {"title": "Transformer Sparking", "desc": "The pole transformer emits sparks and loud bangs randomly.", "cat": "streetlight"},
    {"title": "Power Line Down", "desc": "Storm brought down a power line across the driveway.", "cat": "streetlight"},
    {"title": "Broken Light Pole Base", "desc": "The base of the light pole is rusted and looks like it might fall.", "cat": "streetlight"},
    {"title": "Dark Park Area", "desc": "The central park area is completely pitch black at night, needs lighting.", "cat": "streetlight"},
    {"title": "Voltage Fluctuation", "desc": "Voltage keeps dropping, damaging appliances in the neighborhood.", "cat": "streetlight"},
    {"title": "Leaning Utility Pole", "desc": "The wooden utility pole is leaning dangerously over the road.", "cat": "streetlight"},
    {"title": "Dim Streetlights", "desc": "The new LED lights are too dim to illuminate the sidewalk.", "cat": "streetlight"},
    {"title": "Electric Meter Box Open", "desc": "The community distribution box cover is missing.", "cat": "streetlight"},
    {"title": "Vegetation on Power Lines", "desc": "Tree branches are entangled with high voltage lines.", "cat": "streetlight"},
    {"title": "Unauthorized Cable Fest", "desc": "Too many unauthorized cables dragging down the main pole.", "cat": "streetlight"},
    {"title": "Old Bulb Replacement", "desc": "The amber sodium lamps are dead and need LED replacement.", "cat": "streetlight"},
    {"title": "Scheduled Power Cut Issue", "desc": "Power cuts are lasting longer than the announced schedule.", "cat": "streetlight"},
    {"title": "Loose Wire on Walkway", "desc": "A wire is dangling at head height on the walkway.", "cat": "streetlight"},
    {"title": "Fuse Box Fire Hazard", "desc": "Smoke seen coming from the feeder pillar box.", "cat": "streetlight"},
    {"title": "Solar Light Battery Dead", "desc": "The solar street lights don't last past 8 PM.", "cat": "streetlight"},
    {"title": "Light Pollution into Homes", "desc": "Streetlight shield is missing, shining directly into bedroom windows.", "cat": "streetlight"},

    # Garbage / Waste
    {"title": "Overflowing Dumpster", "desc": "The community dumpster hasn't been emptied in 2 weeks.", "cat": "garbage"},
    {"title": "Illegal Dumping in Vacant Lot", "desc": "People are dumping construction waste and old furniture in the empty lot.", "cat": "garbage"},
    {"title": "Missed Trash Collection", "desc": "Garbage truck missed our street this Tuesday.", "cat": "garbage"},
    {"title": "Litter in Public Park", "desc": "The park is covered in plastic bottles and wrappers after the weekend.", "cat": "garbage"},
    {"title": "Dead Animal on Road", "desc": "Roadkill has been decomposing on the shoulder for days.", "cat": "garbage"},
    {"title": "Broken Public Bin", "desc": "The public dustbin is smashed and trash is spilling out.", "cat": "garbage"},
    {"title": "Burning Garbage Smell", "desc": "Toxic smell from someone burning plastic waste nearby.", "cat": "garbage"},
    {"title": "Medical Waste Found", "desc": "Found syringes and medical waste dumped near the creek.", "cat": "garbage"},
    {"title": "Recycling Not Picked Up", "desc": "Recycling bags are piling up on the curb.", "cat": "garbage"},
    {"title": "Trash Blocking Sidewalk", "desc": "Restaurant piles garbage bags blocking the entire sidewalk.", "cat": "garbage"},
    {"title": "Lack of Bins in Market", "desc": "No dustbins available in the main market area causing littering.", "cat": "garbage"},
    {"title": "Dog Waste Issue", "desc": "Sidewalks are covered in dog poop, need specific bins or signs.", "cat": "garbage"},
    {"title": "Spilled Garbage Truck Load", "desc": "The truck spilled a load of trash and drove off without cleaning.", "cat": "garbage"},
    {"title": "Hazardous Waste Dumped", "desc": "Barrels of unknown chemical dumped in the ditch.", "cat": "garbage"},
    {"title": "Fly Tipping in Alley", "desc": "Old mattresses and appliances blocking the alleyway.", "cat": "garbage"},
    {"title": "Maggot Infestation", "desc": "Rotting pile of food waste is causing a maggot infestation.", "cat": "garbage"},
    {"title": "Plastic Waste in River", "desc": "The river bank is chocked with single-use plastics.", "cat": "garbage"},
    {"title": "Full Bin Notification", "desc": "Smart bin sensor says full but no pickup yet.", "cat": "garbage"},
    {"title": "Sharp Object Hazard", "desc": "Broken glass dumped carelessly on the grass.", "cat": "garbage"},
    {"title": "Post-Event Cleanup Needed", "desc": "Street fair ended yesterday but trash is everywhere.", "cat": "garbage"},

    # Generic / Other
    {"title": "Graffiti on Public Wall", "desc": "Offensive graffiti spray-painted on the school wall.", "cat": "garbage"},
    {"title": "Broken Park Bench", "desc": "Wooden slats on the bench are rotting and broken.", "cat": "road"},
    {"title": "Vandalized Bus Stop", "desc": "Glass shelter at the bus stop has been shattered.", "cat": "road"},
    {"title": "Noise Pollution", "desc": "Construction work continuing late into the night.", "cat": "general"},
    {"title": "Stray Dog Pack Agressive", "desc": "Pack of stray dogs chasing bikers at night.", "cat": "general"},
    {"title": "Tree Falling Hazard", "desc": "Dead tree looks like it will fall on the road in the next storm.", "cat": "road"},
    {"title": "Unauthorized Advertisement", "desc": "Posters glued all over traffic signs.", "cat": "garbage"},
    {"title": "Slippery Steps", "desc": "Steps to the subway are covered in moss and slippery.", "cat": "road"},
    {"title": "Handrail Missing", "desc": "Handrail on the steep staircase is gone.", "cat": "road"},
    {"title": "Playground Equipment Unsafe", "desc": "The swing set chain is rusted through.", "cat": "general"},
]

def get_unique_random_issue(used_indices):
    """Get a unique random issue from DUMMY_ISSUES."""
    available_indices = [i for i in range(len(DUMMY_ISSUES)) if i not in used_indices]
    
    if not available_indices:
        # If all used, allow re-use but try to modify slightly later if needed
        # For now, just pick random
        idx = random.randint(0, len(DUMMY_ISSUES) - 1)
        return DUMMY_ISSUES[idx], idx
    
    idx = random.choice(available_indices)
    return DUMMY_ISSUES[idx], idx

def get_random_user_details(used_emails):
    while True:
        name, email = random.choice(DUMMY_USERS)
        # Add random suffix to email if already used
        if email in used_emails:
            base, domain = email.split('@')
            email = f"{base}_{random.randint(100, 999)}@{domain}"
        
        if email not in used_emails:
            used_emails.add(email)
            first_name = name.split()[0]
            last_name = " ".join(name.split()[1:])
            return first_name, last_name, email

def main():
    print("Starting detailed dummy data generation...")
    
    created_users = []
    used_emails = set()
    used_issue_indices = set()
    
    # Check existing users
    for u in User.objects.all():
        used_emails.add(u.email)

    # 1. Process Profile Pics -> Create/Link Users
    if os.path.exists(PROFILE_PICS_DIR):
        print(f"Scanning {PROFILE_PICS_DIR}...")
        files = glob.glob(os.path.join(PROFILE_PICS_DIR, 'user_*_profile.*'))
        
        for file_path in files:
            filename = os.path.basename(file_path)
            try:
                parts = filename.split('_')
                if len(parts) >= 3 and parts[0] == 'user':
                    user_id = int(parts[1])
                    
                    if not User.objects.filter(id=user_id).exists():
                        first_name, last_name, email = get_random_user_details(used_emails)
                        user = User(
                            id=user_id,
                            first_name=first_name,
                            last_name=last_name,
                            email=email,
                            profile_pic=f"profile_pics/{filename}"
                        )
                        user.set_password(DEFAULT_PASSWORD)
                        user.save()
                        print(f"Created User: {first_name} {last_name} (ID: {user_id})")
                        created_users.append(user)
                    else:
                        # Add existing to list so we can use them for reporting
                        user = User.objects.get(id=user_id)
                        if user not in created_users:
                            created_users.append(user)
            except ValueError:
                continue
    
    # Fallback if no users created/found
    if not created_users:
        if User.objects.exists():
            created_users = list(User.objects.all())
        else:
            # Create at least one dummy user
            first, last, email = get_random_user_details(used_emails)
            u = User.objects.create(first_name=first, last_name=last, email=email)
            u.set_password(DEFAULT_PASSWORD)
            u.save()
            created_users.append(u)


    # 2. Process Issue Images -> Create Issues
    if os.path.exists(ISSUE_IMAGES_DIR):
        print(f"Scanning {ISSUE_IMAGES_DIR}...")
        items = os.listdir(ISSUE_IMAGES_DIR)
        # Randomize order so we don't always give top issues to low IDs if that matters
        random.shuffle(items)

        for item in items:
            item_path = os.path.join(ISSUE_IMAGES_DIR, item)
            if os.path.isdir(item_path):
                try:
                    issue_id = int(item)
                    
                    if not Issue.objects.filter(id=issue_id).exists():
                        # Pick unique dummy data
                        data, idx = get_unique_random_issue(used_issue_indices)
                        used_issue_indices.add(idx)

                        reporter = random.choice(created_users)
                        
                        # Randomize location slightly around a central point (Kathmanduish coords or generic)
                        base_lat, base_lng = 27.7172, 85.3240
                        lat_offset = (random.random() - 0.5) * 0.05
                        lng_offset = (random.random() - 0.5) * 0.05
                        
                        issue = Issue(
                            id=issue_id,
                            title=data['title'],
                            description=data['desc'],
                            category=data['cat'],
                            reported_by=reporter,
                            address=f"{random.randint(10, 999)} {random.choice(['Park Lane', 'Main St', 'Broadway', 'Market Rd', 'River Side', 'Hill Top'])}",
                            city=random.choice(["Townspark", "Metropolis", "Gotham", "Queens", "Asgard"]),
                            latitude=base_lat + lat_offset,
                            longitude=base_lng + lng_offset,
                        )
                        issue.save()
                        print(f"Created Issue #{issue_id}: {issue.title}")

                        # Add Images
                        images = os.listdir(item_path)
                        valid_images = [img for img in images if img.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
                        
                        # Add all images (or max 3)
                        for img_name in valid_images[:3]:
                            IssueImage.objects.create(
                                issue=issue,
                                image=f"issue_images/{issue_id}/{img_name}"
                            )
                            print(f"  + Image: {img_name}")
                    else:
                        print(f"Issue #{issue_id} exists. Skipping.")

                except ValueError:
                    continue
    
    # 3. Output User Details
    if created_users:
        with open(OUTPUT_FILE, 'w') as f:
            for user in created_users:
                # Only write if it was likely created by us (default password check is weak but ok)
                # Or just dump all for convenience
                f.write(f"Name: {user.get_full_name()}\n")
                f.write(f"Email: {user.email}\n")
                f.write(f"Password: {DEFAULT_PASSWORD}\n")
                f.write("-" * 20 + "\n")
        print(f"User details written to {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
