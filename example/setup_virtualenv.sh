VIRTUALENV_NAME="image_filer_example"
#virtualenv $VIRTUALENV_NAME
#pip -E $VIRTUALENV_NAME install -r ../requirements.pip

#git clone git://github.com/digi604/django-cms-2.0.git ./$VIRTUALENV_NAME/src/django-cms-2.0
touch $VIRTUALENV_NAME/lib/python2.5/site-packages/django-cms-2.0.pth
echo "../../../src/django-cms-2.0" > $VIRTUALENV_NAME/lib/python2.5/site-packages/django-cms-2.0.pth

touch $VIRTUALENV_NAME/lib/python2.5/site-packages/image_filer.pth
echo "../../../../../" > $VIRTUALENV_NAME/lib/python2.5/site-packages/image_filer.pth
source ./$VIRTUALENV_NAME/bin/activate