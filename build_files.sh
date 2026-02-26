# build_files.sh

# Install requirements with the "break-system-packages" flag to bypass the error
pip install -r requirements.txt --break-system-packages

# Run migrations
python3.9 manage.py migrate

# Seed data (If you kept this step)
python3.9 manage.py seed_data

# Collect static files
python3.9 manage.py collectstatic --noinput --clear