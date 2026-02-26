echo "BUILD START"

# 1. Install dependencies into the CURRENT folder (-t .)
# This forces Django to be right next to manage.py, so it CANNOT be missed.
python3.9 -m pip install -r requirements.txt -t . --no-cache-dir --upgrade

# 2. Verify Django is accessible
echo "Verifying Django..."
python3.9 -m django --version

# 3. Create the output directory manually (just in case)
mkdir -p staticfiles_build

# 4. Run Migrations
echo "Running Migrations..."
python3.9 manage.py makemigrations --noinput
python3.9 manage.py migrate --noinput

# 5. Seed Data (Optional - remove if it causes issues)
# python3.9 manage.py seed_data

# 6. Collect Static Files
echo "Collecting Static Files..."
python3.9 manage.py collectstatic --noinput --clear

echo "BUILD END"