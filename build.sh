cmd="python3 -m pip install --upgrade --disable-pip-version-check --target . ."

case "$DATABASE_URL" in
    postgres*)
        cmd="$cmd psycopg[binary,pool]~=3.2"
        ;;
    mysql*)
        apt update
        apt install -y python3-dev default-libmysqlclient-dev build-essential pkg-config
        cmd="$cmd mysqlclient~=2.2"
        ;;
esac

echo "Installing packages..."
eval $cmd

# if it doesn't contain files, the deployment fails
mkdir -p static
echo '{"paths": {}, "version": "1.1", "hash": ""}' > static/staticfiles.json

echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear -v 1 &

echo "Creating the cache table..."
python3 manage.py createcachetable &

echo "Migrating..."
python3 manage.py migrate &

if which dnf >/dev/null 2>&1; then
    echo "Using dnf to install gettext..."
    dnf install -y gettext
elif which apt >/dev/null 2>&1; then
    echo "Using apt to install gettext..."
    apt update
    apt install -y gettext
elif which apk >/dev/null 2>&1; then
    echo "Using apk to install gettext..."
    apk add gettext
else
    echo "Warning: dnf, apt and apk are unavailable. Can't install gettext. Translations won't be compiled."
fi

if which gettext >/dev/null 2>&1; then
    echo "Compiling translations..."
    python3 manage.py compilemessages \
        --ignore adminsortable2 \
        --ignore allauth \
        --ignore debug_toolbar \
        --ignore django \
        --ignore phonenumber_field
fi

wait
