echo "Installing gettext..."
dnf install -y gettext

python3 -m pip install --target . psycopg[binary,pool]~=3.2

echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear -v 1 &

echo "Creating the cache tables..."
python3 manage.py createcachetable &

echo "Migrating..."
python3 manage.py migrate &

echo "Compiling translations..."
python3 manage.py compilemessages --ignore adminsortable2 --ignore allauth --ignore debug_toolbar --ignore django

wait
