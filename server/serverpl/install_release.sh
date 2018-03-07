#Checking if python >= 3.5 is installed
if ! hash python3; then
    echo "ERROR: Python >= 3.5 should be installed."
    exit 1
fi

ver=$(python3 --version 2>&1 | sed 's/.* \([0-9]\).\([0-9]\).*/\1\2/')
if [ "$ver" -lt "35" ]; then
    echo "ERROR: Python >= 3.5 should be installed."
    exit 1
fi
echo "Python >= 3.5: OK !"

#Checking if pip3 is installed
command -v pip3 >/dev/null 2>&1 || { echo >&2 "ERROR: pip3 should be installed"; exit 1; }
echo "pip3: OK !"

#Getting requirement
echo ""
echo "Installing requirements..."
pip3 install -r requirements.txt || { echo>&2 "ERROR: pip3 install -r requirements.txt failed" ; exit 1; }
echo "Done !"

#Getting release settings.py
cp -f serverpl/install/settings_release.py serverpl/settings.py

#Creating documentation
echo ""
echo "Creating documentation..."
./make_doc.sh || { echo>&2 "ERROR: ./make_doc.sh failed" ; exit 1; }
echo "Done !"

#Building database
echo ""
echo "Configuring database..."
python3 manage.py migrate || { echo>&2 "ERROR: python3 manage.py migrate failed" ; exit 1; }
echo "Done !"

echo ""
echo "Creating super user account..."
python3 manage.py createsuperuser || { echo>&2 "ERROR: python3 manage.py createsuperuser failed" ; exit 1; }
echo "Do not forget to give you a role throught the application adminisration page."
