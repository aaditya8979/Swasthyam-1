# build_files.sh
pip install -r requirements.txt

# 1. Migrate Database
python3.9 manage.py migrate

# 2. Run Seed Data (This adds your vaccines & milestones automatically!)
python3.9 manage.py seed_data

# 3. Collect Static Files
python3.9 manage.py collectstatic --noinput --clear