echo "BUILD START"

# 1. Install dependencies using the specific python3.9 module
# We add --no-cache-dir to prevent installing broken cached versions
python3.9 -m pip install -r requirements.txt --no-cache-dir

# 2. explicit check: Verify Django is actually installed
echo "Verifying Django installation..."
python3.9 -m django --version

# 3. Run Migrations
echo "Running Migrations..."
python3.9 manage.py makemigrations --noinput
python3.9 manage.py migrate --noinput

# 4. Seed Data (Optional - comment out if it fails)
# python3.9 manage.py seed_data

# 5. Collect Static Files (Crucial step)
echo "Collecting Static Files..."
python3.9 manage.py collectstatic --noinput --clear

echo "BUILD END"