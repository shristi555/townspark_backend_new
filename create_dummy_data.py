import os
import django
import random
import glob
import shutil
import argparse
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main_app.settings')
django.setup()

from accounts.models import User
from issues.models import Issue, IssueImage
from django.db import models
from django.utils import timezone

# Constants
MEDIA_ROOT = 'media'
PROFILE_PICS_DIR = os.path.join(MEDIA_ROOT, 'profile_pics')
ISSUE_IMAGES_DIR = os.path.join(MEDIA_ROOT, 'issue_images')
OUTPUT_FILE = 'user_details.txt'
DEFAULT_PASSWORD = "asdfghjkl;'"

# Frontend Categories
CATEGORIES = [
    "pothole", "streetlight", "garbage", "water", "drainage", "road", "electricity", "other"
]

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
]

# 150+ Predefined Realistic Issues
DUMMY_ISSUES = [
    # Road / Potholes
    {"title": "Large Pothole on Main St", "desc": "A very large pothole has formed in the middle of the road, causing traffic alerts.", "cat": "pothole"},
    {"title": "Cracked Sidewalk near Park", "desc": "The sidewalk pavement is cracked and uneven, posing a tripping hazard for pedestrians.", "cat": "road"},
    {"title": "Missing Street Sign", "desc": "The stop sign at the intersection of 5th and Elm is missing.", "cat": "road"},
    {"title": "Faded Crosswalk Markings", "desc": "The zebra crossing paint has completely faded, making it dangerous for students crossing.", "cat": "road"},
    {"title": "Debris Blocking Bike Lane", "desc": "Construction debris has been left in the bike lane for over a week.", "cat": "garbage"},
    {"title": "Sinkhole Developing", "desc": "Small sinkhole appearing near the breakdown lane on Highway 4.", "cat": "road"},
    {"title": "Damaged Guardrail", "desc": "Guardrail was hit by a car and keeps protruding into the lane.", "cat": "road"},
    {"title": "Unpaved Road Connection", "desc": "The connecting road between Sector 4 and 5 is still unpaved and muddy.", "cat": "road"},
    {"title": "Speed Bump Too High", "desc": "The newly installed speed bump is scraping the bottom of normal sedans.", "cat": "road"},
    {"title": "Traffic Light Malfunction", "desc": "The signal at the busy 4-way junction is stuck on red for all sides.", "cat": "road"},
    {"title": "Blind Spot Mirror Broken", "desc": "The convex mirror at the blind turn is shattered.", "cat": "road"},
    {"title": "Road Resurfacing Needed", "desc": "The entire stretch of road is riddled with small potholes and needs resurfacing.", "cat": "pothole"},
    {"title": "Illegal Parking Blocking Road", "desc": "Cars are parked on both sides of the narrow lane, blocking traffic flow.", "cat": "road"},
    {"title": "Loose Gravel Hazard", "desc": "Loose gravel from recent works is causing skidding risks.", "cat": "road"},
    {"title": "Manhole Cover Loose", "desc": "The manhole cover clanks loudly every time a car passes over it.", "cat": "road"},
    {"title": "Road Markings Invisible at Night", "desc": "Reflectors are missing and lines are not visible in the dark.", "cat": "road"},
    {"title": "Bridge Expansion Joint Gap", "desc": "The gap in the bridge joint has widened dangerously.", "cat": "road"},
    {"title": "Overgrown Bush Blocking View", "desc": "Bushes at the corner are blocking the view of oncoming traffic.", "cat": "other"},
    {"title": "Narrow Road Congestion", "desc": "The single lane road is causing massive bottlenecks during rush hour.", "cat": "road"},
    {"title": "Slippery Road Surface", "desc": "Oil spill has not been cleaned up, making the turn very slippery.", "cat": "other"},

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
    {"title": "Exposed Electrical Wires", "desc": "Live wires are hanging low from the pole near the playground.", "cat": "electricity"},
    {"title": "Transformer Sparking", "desc": "The pole transformer emits sparks and loud bangs randomly.", "cat": "electricity"},
    {"title": "Power Line Down", "desc": "Storm brought down a power line across the driveway.", "cat": "electricity"},
    {"title": "Broken Light Pole Base", "desc": "The base of the light pole is rusted and looks like it might fall.", "cat": "streetlight"},
    {"title": "Dark Park Area", "desc": "The central park area is completely pitch black at night, needs lighting.", "cat": "streetlight"},
    {"title": "Voltage Fluctuation", "desc": "Voltage keeps dropping, damaging appliances in the neighborhood.", "cat": "electricity"},
    {"title": "Leaning Utility Pole", "desc": "The wooden utility pole is leaning dangerously over the road.", "cat": "electricity"},
    {"title": "Dim Streetlights", "desc": "The new LED lights are too dim to illuminate the sidewalk.", "cat": "streetlight"},
    {"title": "Electric Meter Box Open", "desc": "The community distribution box cover is missing.", "cat": "electricity"},
    {"title": "Vegetation on Power Lines", "desc": "Tree branches are entangled with high voltage lines.", "cat": "electricity"},
    {"title": "Unauthorized Cable Fest", "desc": "Too many unauthorized cables dragging down the main pole.", "cat": "electricity"},
    {"title": "Old Bulb Replacement", "desc": "The amber sodium lamps are dead and need LED replacement.", "cat": "streetlight"},
    {"title": "Scheduled Power Cut Issue", "desc": "Power cuts are lasting longer than the announced schedule.", "cat": "electricity"},
    {"title": "Loose Wire on Walkway", "desc": "A wire is dangling at head height on the walkway.", "cat": "electricity"},
    {"title": "Fuse Box Fire Hazard", "desc": "Smoke seen coming from the feeder pillar box.", "cat": "electricity"},
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
    {"title": "Graffiti on Public Wall", "desc": "Offensive graffiti spray-painted on the school wall.", "cat": "other"},
    {"title": "Broken Park Bench", "desc": "Wooden slats on the bench are rotting and broken.", "cat": "other"},
    {"title": "Vandalized Bus Stop", "desc": "Glass shelter at the bus stop has been shattered.", "cat": "other"},
    {"title": "Noise Pollution", "desc": "Construction work continuing late into the night.", "cat": "other"},
    {"title": "Stray Dog Pack Agressive", "desc": "Pack of stray dogs chasing bikers at night.", "cat": "other"},
    {"title": "Tree Falling Hazard", "desc": "Dead tree looks like it will fall on the road in the next storm.", "cat": "other"},
    {"title": "Unauthorized Advertisement", "desc": "Posters glued all over traffic signs.", "cat": "other"},
    {"title": "Slippery Steps", "desc": "Steps to the subway are covered in moss and slippery.", "cat": "other"},
    {"title": "Handrail Missing", "desc": "Handrail on the steep staircase is gone.", "cat": "other"},
    {"title": "Playground Equipment Unsafe", "desc": "The swing set chain is rusted through.", "cat": "other"},
]

def get_issue_data(idx):
    """Get issue data, cycling if idx exceeds predefined list."""
    base_data = DUMMY_ISSUES[idx % len(DUMMY_ISSUES)]
    # Add variation if reused
    if idx >= len(DUMMY_ISSUES):
        return {
            "title": f"{base_data['title']} ({random.choice(['Recurring', 'New Report', 'Again'])})",
            "desc": base_data['desc'],
            "cat": base_data['cat']
        }
    return base_data

def collect_all_images(source_dir):
    """Collect all valid images from source directory recursively."""
    images = []
    print(f"Collecting images from {source_dir}...")
    for root, dirs, files in os.walk(source_dir):
        # We manually skip pool inside the walker, but now we might WANT pool if repairing
        # But this function is usually for finding 'raw' images. 
        # The pool logic is handled specially in main.
        if '_pool' in root:
            continue
            
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                full_path = os.path.join(root, file)
                images.append(full_path)
    print(f"Found {len(images)} images total.")
    return images

def main():
    parser = argparse.ArgumentParser(description="Generate dummy data for Townspark.")
    parser.add_argument('-u', '--users', type=int, default=8, help="Target number of users (default: 8)")
    parser.add_argument('-i', '--issues', type=int, default=150, help="Target number of issues (default: 150)")
    args = parser.parse_args()

    TARGET_USERS = args.users
    TARGET_ISSUES = args.issues

    print(f"Starting detailed dummy data generation (Target: {TARGET_USERS} Users, {TARGET_ISSUES} Issues)...")
    
    # 1. Check Counts FIRST
    existing_user_count = User.objects.filter(is_superuser=False).count()
    users_needed = TARGET_USERS - existing_user_count
    
    current_issue_count = Issue.objects.count()
    issues_needed = TARGET_ISSUES - current_issue_count

    # 2. Check for "Broken" Issues (Existing but no images)
    # This detects if DB has issues but files were lost or not assigned
    issues_without_images = Issue.objects.annotate(num_images=models.Count('images')).filter(num_images=0)
    repair_count = issues_without_images.count()
    
    should_run_image_logic = issues_needed > 0 or repair_count > 0 or users_needed > 0
    
    pooled_images = []
    
    if should_run_image_logic:
        # Move all images to a temporary pool to redistribute
        # Only do this if we actually intend to write/repair data
        pool_dir = os.path.join(ISSUE_IMAGES_DIR, '_pool')
        os.makedirs(pool_dir, exist_ok=True)
        
        # Collect from standard dirs (excluding pool)
        raw_images = collect_all_images(ISSUE_IMAGES_DIR)
        
        # ALSO collect from _pool to 'rescue' them if previous runs left them there
        if os.path.exists(pool_dir):
            for f in os.listdir(pool_dir):
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    raw_images.append(os.path.join(pool_dir, f))
        
        # Deduplicate paths
        raw_images = list(set(raw_images))

        for img_path in raw_images:
            # Don't move if already in pool and we are just listing it
            if os.path.dirname(img_path) == pool_dir:
                pooled_images.append(img_path)
                continue
                
            filename = os.path.basename(img_path)
            # Avoid overwrite
            if os.path.exists(os.path.join(pool_dir, filename)):
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{random.randint(1000, 9999)}{ext}"
            
            dest = os.path.join(pool_dir, filename)
            try:
                shutil.move(img_path, dest)
                pooled_images.append(dest)
            except Exception as e:
                print(f"Error moving {img_path}: {e}")

        # Remove empty directories (cleanup)
        for root, dirs, files in os.walk(ISSUE_IMAGES_DIR, topdown=False):
            if root == pool_dir: continue
            try:
                os.rmdir(root)
            except:
                pass
                
        random.shuffle(pooled_images)
        print(f"Pooled {len(pooled_images)} images for distribution.")
    else:
        print("Skipping image pooling as no generation/repair needed.")

    # 3. Create Users
    created_users = []
    if users_needed <= 0:
        print(f"User check: Found {existing_user_count} users (Target: {TARGET_USERS}). Skipping creation.")
        # Only populate list if we might need them for issue generation (repair doesn't need new users)
        # But reporter logic needs users.
        created_users = list(User.objects.filter(is_superuser=False)[:TARGET_USERS])
        if not created_users: # Fallback if no users at all
             created_users = list(User.objects.all())
    else:
        print(f"User check: Found {existing_user_count} users. Creating {users_needed} more...")
        current_users = list(User.objects.filter(is_superuser=False))
        created_users.extend(current_users)
        
        for i in range(users_needed):
            name, base_email = DUMMY_USERS[(existing_user_count + i) % len(DUMMY_USERS)]
            email = f"{base_email.split('@')[0]}_{random.randint(1000, 999)}@{base_email.split('@')[1]}"
            user = User.objects.create(
                first_name=name.split()[0],
                last_name=" ".join(name.split()[1:]),
                email=email
            )
            user.set_password(DEFAULT_PASSWORD)
            user.save()
            created_users.append(user)
            print(f"Created User: {user.email}")

        # Assign profile pics (only if pooling happened)
        if pooled_images:
            profile_images = glob.glob(os.path.join(PROFILE_PICS_DIR, 'user_*.*'))
            for user in created_users:
                if user.profile_pic: continue
                specific_pic = next((p for p in profile_images if f"user_{user.id}_" in p), None)
                if specific_pic:
                    user.profile_pic = f"profile_pics/{os.path.basename(specific_pic)}"
                    user.save()
                elif random.random() > 0.3: 
                    pic_source = random.choice(pooled_images)
                    pic_name = f"user_{user.id}_profile_{random.randint(1000,9999)}{os.path.splitext(pic_source)[1]}"
                    pic_dest = os.path.join(PROFILE_PICS_DIR, pic_name)
                    shutil.copy(pic_source, pic_dest)
                    user.profile_pic = f"profile_pics/{pic_name}"
                    user.save()
                    print(f"Assigned random profile pic to {user.email}")
                
        if users_needed > 0:
            with open(OUTPUT_FILE, 'w') as f:
                for user in created_users:
                    f.write(f"Email: {user.email}\nPassword: {DEFAULT_PASSWORD}\n---\n")
            print(f"Updated {OUTPUT_FILE}")

    
    # 4. Generate New Issues
    current_issue_count = Issue.objects.count() # refresh
    
    if issues_needed > 0:
        print(f"Issue check: Found {current_issue_count} issues. Generating {issues_needed} more...")
        
        # We need an img_idx tracker
        img_idx = 0
        
        for i in range(issues_needed):
            issue_data = get_issue_data(i)
            reporter = random.choice(created_users) if created_users else None
            
            if not reporter:
                print("Error: No users available to report issues.")
                break

            base_lat, base_lng = 27.7172, 85.3240
            lat = base_lat + (random.random() - 0.5) * 0.1
            lng = base_lng + (random.random() - 0.5) * 0.1
            is_resolved = random.random() < 0.3 
            is_archived = random.random() < 0.1 
            if is_archived: is_resolved = True 
            
            issue = Issue.objects.create(
                title=issue_data['title'],
                description=issue_data['desc'],
                category=issue_data['cat'],
                reported_by=reporter,
                address=f"{random.randint(1, 999)} {random.choice(['Main St', 'Broadway', 'Park Ave', 'River Rd'])}",
                city=random.choice(["Townspark", "Metropolis", "Gotham", "Star City"]),
                latitude=lat,
                longitude=lng,
                is_resolved=is_resolved,
                is_archived=is_archived,
                created_at=timezone.now() - timezone.timedelta(days=random.randint(0, 365))
            )
            if is_resolved:
                issue.resolved_at = issue.created_at + timezone.timedelta(days=random.randint(1, 10))
                issue.save()

            # Assign Images
            images_for_this_issue = []
            
            # 1. Get Primary
            if img_idx < len(pooled_images):
                source_image = pooled_images[img_idx]
                images_for_this_issue.append({'src': source_image, 'move': True})
                img_idx += 1
            else:
                if pooled_images:
                    source_image = random.choice(pooled_images)
                    images_for_this_issue.append({'src': source_image, 'move': False})
                else:
                    # No pooled images at all?
                    pass

            # 2. Get Extras
            if pooled_images:
                remaining_gen = issues_needed - (i + 1)
                remaining_imgs = len(pooled_images) - img_idx
                num_extras = 0
                if remaining_gen > 0 and (remaining_imgs / remaining_gen) > 1.5:
                     num_extras = random.randint(1, min(2, remaining_imgs))
                     use_originals = True
                elif random.random() < 0.3: 
                     num_extras = random.randint(1, 2)
                     use_originals = False
                
                for _ in range(num_extras):
                    if use_originals and img_idx < len(pooled_images):
                        images_for_this_issue.append({'src': pooled_images[img_idx], 'move': True})
                        img_idx += 1
                    elif pooled_images: 
                        images_for_this_issue.append({'src': random.choice(pooled_images), 'move': False})

            # Process Images
            if images_for_this_issue:
                issue_img_dir = os.path.join(ISSUE_IMAGES_DIR, str(issue.id))
                os.makedirs(issue_img_dir, exist_ok=True)
                images_for_this_issue.sort(key=lambda x: x['move']) 
                for item in images_for_this_issue:
                    src_path = item['src']
                    base_name = os.path.basename(src_path)
                    try:
                        if not item['move']:
                            name, ext = os.path.splitext(base_name)
                            fname = f"{name}_{random.randint(10000, 99999)}{ext}"
                            dest_path = os.path.join(issue_img_dir, fname)
                            if os.path.exists(src_path):
                                shutil.copy(src_path, dest_path)
                                IssueImage.objects.create(issue=issue, image=f"issue_images/{issue.id}/{fname}")
                        else:
                            fname = base_name
                            dest_path = os.path.join(issue_img_dir, fname)
                            if os.path.exists(src_path):
                                shutil.move(src_path, dest_path)
                                IssueImage.objects.create(issue=issue, image=f"issue_images/{issue.id}/{fname}")
                    except Exception as e:
                        print(f"Error processing image {src_path}: {e}")
            
            print(f"Created Issue #{issue.id} [{issue.category}] with {len(images_for_this_issue)} images.")
    else:
        print(f"Issue check: Found {current_issue_count} issues (Target: {TARGET_ISSUES}). Skipping new generation.")

    # 5. REPAIR: Assign images to issues that have none
    if repair_count > 0:
        print(f"Health Check: Found {repair_count} issues with NO images. Repairing...")
        if not pooled_images:
             print("Warning: No images available in pool to repair issues!")
        else:
            repaired_count = 0
            for issue in issues_without_images:
                # Pick 1 random image (COPY)
                src = random.choice(pooled_images)
                
                issue_img_dir = os.path.join(ISSUE_IMAGES_DIR, str(issue.id))
                os.makedirs(issue_img_dir, exist_ok=True)
                
                base_name = os.path.basename(src)
                name, ext = os.path.splitext(base_name)
                fname = f"{name}_repair_{random.randint(10000, 99999)}{ext}"
                dest_path = os.path.join(issue_img_dir, fname)
                
                try:
                    if os.path.exists(src):
                        shutil.copy(src, dest_path)
                        IssueImage.objects.create(issue=issue, image=f"issue_images/{issue.id}/{fname}")
                        repaired_count += 1
                except Exception as e:
                    print(f"Failed to repair issue #{issue.id}: {e}")
            print(f"Repaired {repaired_count} issues.")

    # Cleanup pool
    try:
        if os.path.exists(pool_dir):
            if not os.listdir(pool_dir):
                os.rmdir(pool_dir)
            else:
                print(f"Note: {len(os.listdir(pool_dir))} images left unused in pool.")
    except:
        pass

    print(f"Done! Processed checks/generation.")

if __name__ == '__main__':
    main()
