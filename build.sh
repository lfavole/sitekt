python3 -m pip install --upgrade --disable-pip-version-check --target . . psycopg[binary,pool]~=3.2

# if it doesn't contain files, the deployment fails
mkdir static
echo '{"paths": {}, "version": "1.1", "hash": ""}' > static/staticfiles.json

echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear -v 1 &

echo "Creating the cache table..."
python3 manage.py createcachetable &

echo "Migrating..."
python3 manage.py migrate &

echo "Installing gettext..."
dnf install -y gettext

echo "Compiling translations..."
python3 manage.py compilemessages \
    --ignore adminsortable2 \
    --ignore allauth \
    --ignore debug_toolbar \
    --ignore django \
    --ignore phonenumber_field

wait
