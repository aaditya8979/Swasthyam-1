# build_files.sh

echo "BUILD START"

# 1. Create a virtual environment named 'venv'
python3.9 -m venv venv

# 2. Activate the virtual environment
source venv/bin/activate

# 3. Install dependencies INSIDE the venv
# Note: We don't need --break-system-packages here because we are in a venv
pip install -r requirements.txt

# 4. Make migrations
python manage.py makemigrations
python manage.py migrate

# 5. Seed Data (If you are using this)
python manage.py seed_data

# 6. Collect Static Files
python manage.py collectstatic --noinput --clear

echo "BUILD END"