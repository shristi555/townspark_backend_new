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

DUMMY_NAMES = [
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
]

def get_random_user_details(used_emails):
    while True:
        name, email = random.choice(DUMMY_NAMES)
        # Add random suffix to email if already used, just in case
        if email in used_emails:
            base, domain = email.split('@')
            email = f"{base}_{random.randint(100, 999)}@{domain}"
        
        if email not in used_emails:
            used_emails.add(email)
            first_name = name.split()[0]
            last_name = " ".join(name.split()[1:])
            return first_name, last_name, email

def main():
    print("Starting dummy data generation...")
    
    created_users = []
    used_emails = set()
    
    # Check existing users to avoid email conflicts
    for u in User.objects.all():
        used_emails.add(u.email)

    # 1. Process Profile Pics -> Create Users
    if os.path.exists(PROFILE_PICS_DIR):
        print(f"Scanning {PROFILE_PICS_DIR}...")
        # Pattern: user_<id>_profile.*
        files = glob.glob(os.path.join(PROFILE_PICS_DIR, 'user_*_profile.*'))
        
        for file_path in files:
            filename = os.path.basename(file_path)
            try:
                # Extract ID: user_123_profile.jpg
                parts = filename.split('_')
                if len(parts) >= 3 and parts[0] == 'user' and parts[2].startswith('profile'):
                    user_id = int(parts[1])
                    
                    # Check if user exists
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
                        print(f"User ID {user_id} already exists. Skipping.")
                        
            except ValueError:
                print(f"Skipping malformed filename: {filename}")
                continue
    else:
        print(f"Profile pics directory not found: {PROFILE_PICS_DIR}")

    # 2. Process Issue Images -> Create Issues
    if os.path.exists(ISSUE_IMAGES_DIR):
        print(f"Scanning {ISSUE_IMAGES_DIR}...")
        # Directories are issue IDs
        items = os.listdir(ISSUE_IMAGES_DIR)
        
        for item in items:
            item_path = os.path.join(ISSUE_IMAGES_DIR, item)
            if os.path.isdir(item_path):
                try:
                    issue_id = int(item)
                    
                    if not Issue.objects.filter(id=issue_id).exists():
                        # We need a reporter. Pick one from created_users or any random user in DB
                        if created_users:
                            reporter = random.choice(created_users)
                        else:
                            # Try to get any user
                            reporter = User.objects.first()
                            if not reporter:
                                # Create a fallback user if absolutely no users exist
                                first, last, email = get_random_user_details(used_emails)
                                reporter = User.objects.create(
                                    first_name=first, last_name=last, email=email
                                )
                                reporter.set_password(DEFAULT_PASSWORD)
                                reporter.save()
                                created_users.append(reporter)
                        
                        # Create Issue
                        issue = Issue(
                            id=issue_id,
                            title=f"Community Issue #{issue_id}",
                            description=f"This is a reported issue found in the media folder. It requires attention from the local authorities. Location ID: {random.randint(1000, 9999)}.",
                            category=random.choice(['road', 'water', 'electricity', 'garbage']),
                            reported_by=reporter,
                            address=f"{random.randint(1, 999)} Main St, Townspark",
                            city="Townspark",
                            latitude=27.7 + random.random() * 0.1,
                            longitude=85.3 + random.random() * 0.1,
                        )
                        issue.save()
                        print(f"Created Issue #{issue_id}")

                        # Create IssueImage (pick minimal 1 random)
                        images = os.listdir(item_path)
                        if images:
                            chosen_image = random.choice(images)
                            # Verify extension
                            if chosen_image.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                                IssueImage.objects.create(
                                    issue=issue,
                                    image=f"issue_images/{issue_id}/{chosen_image}"
                                )
                                print(f"  Added image: {chosen_image}")
                    else:
                        print(f"Issue ID {issue_id} already exists. Skipping.")

                except ValueError:
                    continue
    else:
        print(f"Issue images directory not found: {ISSUE_IMAGES_DIR}")

    # 3. Output User Details
    if created_users:
        with open(OUTPUT_FILE, 'w') as f:
            for user in created_users:
                f.write(f"name: {user.get_full_name()}\n")
                f.write(f"email: {user.email}\n")
                f.write(f"password: {DEFAULT_PASSWORD}\n")
                f.write("\n\n")
        print(f"User details written to {OUTPUT_FILE}")
    else:
        print("No new users created.")

if __name__ == '__main__':
    main()
